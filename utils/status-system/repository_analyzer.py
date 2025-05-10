#!/usr/bin/env python3
"""
HMS Repository Analyzer
This script analyzes repository status and health, providing detailed reports on:
- Code quality
- Test status
- Documentation completeness
- Build status
- Security issues
- Dependency health
"""

import argparse
import json
import os
import subprocess
import sys
import datetime
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Constants
STATUS_DIR = Path("data/status")
ANALYSIS_DIR = Path("data/analysis")
ISSUES_DIR = Path("data/issues")
REPOS_DIR = Path("SYSTEM-COMPONENTS")
DEFAULT_CONFIG = {
    "max_test_age_days": 7,
    "min_test_coverage": 0.7,
    "max_dependency_age_days": 90,
    "security_scan_frequency_days": 14,
    "doc_coverage_threshold": 0.7,
    "allowed_failure_rate": 0.02,
    "min_build_frequency_days": 7
}

class RepositoryAnalyzer:
    """Main repository analyzer class"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the repository analyzer"""
        self.config = config or DEFAULT_CONFIG
        self.ensure_directories()
        
    def ensure_directories(self) -> None:
        """Ensure required directories exist"""
        STATUS_DIR.mkdir(parents=True, exist_ok=True)
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        ISSUES_DIR.mkdir(parents=True, exist_ok=True)
    
    def analyze_repository(self, repo_name: str, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a repository and return its health status"""
        print(f"Analyzing repository: {repo_name}")
        
        # Determine repository path
        repo_path = repo_path or os.path.join(REPOS_DIR, repo_name)
        
        # Run all analysis
        git_status = self.check_git_status(repo_path)
        test_status = self.check_test_status(repo_name, repo_path)
        doc_status = self.check_documentation(repo_name, repo_path)
        build_status = self.check_build_status(repo_name)
        security_status = self.check_security(repo_name, repo_path)
        dependency_status = self.check_dependencies(repo_name, repo_path)
        
        # Combine results
        result = {
            "repository": repo_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "path": repo_path,
            "overall_status": "UNKNOWN",
            "git_status": git_status,
            "test_status": test_status,
            "documentation_status": doc_status,
            "build_status": build_status,
            "security_status": security_status,
            "dependency_status": dependency_status,
            "issues": []
        }
        
        # Calculate overall status
        statuses = [
            git_status.get("status", "UNKNOWN"),
            test_status.get("status", "UNKNOWN"),
            doc_status.get("status", "UNKNOWN"),
            build_status.get("status", "UNKNOWN"),
            security_status.get("status", "UNKNOWN"),
            dependency_status.get("status", "UNKNOWN")
        ]
        
        # Count statuses
        status_counts = {
            "HEALTHY": statuses.count("HEALTHY"),
            "DEGRADED": statuses.count("DEGRADED"),
            "UNHEALTHY": statuses.count("UNHEALTHY"),
            "UNKNOWN": statuses.count("UNKNOWN")
        }
        
        # Determine overall status
        if status_counts["UNHEALTHY"] > 0:
            result["overall_status"] = "UNHEALTHY"
        elif status_counts["DEGRADED"] > 0:
            result["overall_status"] = "DEGRADED"
        elif status_counts["UNKNOWN"] > len(statuses) / 2:
            result["overall_status"] = "UNKNOWN"
        else:
            result["overall_status"] = "HEALTHY"
        
        # Collect issues
        for section in ["git_status", "test_status", "documentation_status", "build_status", "security_status", "dependency_status"]:
            if section in result and "issues" in result[section]:
                for issue in result[section]["issues"]:
                    result["issues"].append({
                        "component": section.replace("_status", ""),
                        "description": issue
                    })
        
        # Save result to file
        self.save_analysis(repo_name, result)
        
        return result

    def check_git_status(self, repo_path: str) -> Dict[str, Any]:
        """Check git status of the repository"""
        try:
            # Check if directory exists and is a git repository
            if not os.path.isdir(repo_path):
                return {
                    "status": "UNKNOWN",
                    "exists": False,
                    "is_git_repo": False,
                    "issues": ["Repository directory does not exist"]
                }
            
            # Check if it's a git repository
            result = subprocess.run(
                ["git", "-C", repo_path, "rev-parse", "--is-inside-work-tree"],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode != 0:
                return {
                    "status": "DEGRADED",
                    "exists": True,
                    "is_git_repo": False,
                    "issues": ["Not a git repository"]
                }
            
            # Check git status
            status_result = subprocess.run(
                ["git", "-C", repo_path, "status", "--porcelain"],
                capture_output=True, text=True, check=True
            )
            
            # Check for uncommitted changes
            has_changes = len(status_result.stdout.strip()) > 0
            
            # Get branch information
            branch_result = subprocess.run(
                ["git", "-C", repo_path, "branch", "--show-current"],
                capture_output=True, text=True, check=True
            )
            current_branch = branch_result.stdout.strip()
            
            # Get commit information
            commit_result = subprocess.run(
                ["git", "-C", repo_path, "log", "-1", "--format=%h %cd", "--date=relative"],
                capture_output=True, text=True, check=True
            )
            latest_commit = commit_result.stdout.strip()
            
            status = "HEALTHY"
            issues = []
            
            if has_changes:
                status = "DEGRADED"
                issues.append("Repository has uncommitted changes")
            
            return {
                "status": status,
                "exists": True,
                "is_git_repo": True,
                "branch": current_branch,
                "latest_commit": latest_commit,
                "has_uncommitted_changes": has_changes,
                "issues": issues
            }
            
        except Exception as e:
            return {
                "status": "UNHEALTHY",
                "error": str(e),
                "issues": [f"Error checking git status: {str(e)}"]
            }

    def check_test_status(self, repo_name: str, repo_path: str) -> Dict[str, Any]:
        """Check test status of the repository"""
        # Look for test results file
        test_results_path = os.path.join("data/test-results", f"{repo_name}.json")
        if not os.path.exists(test_results_path):
            return {
                "status": "UNKNOWN",
                "has_tests": False,
                "last_run": None,
                "issues": ["No test results found"]
            }
            
        try:
            with open(test_results_path, 'r') as f:
                test_data = json.load(f)
            
            # Check test age
            last_run = datetime.datetime.fromisoformat(test_data.get("timestamp", "2000-01-01T00:00:00"))
            age_days = (datetime.datetime.now() - last_run).days
            
            # Calculate test metrics
            passed = test_data.get("passed", 0)
            failed = test_data.get("failed", 0)
            skipped = test_data.get("skipped", 0)
            total = passed + failed + skipped
            
            if total == 0:
                pass_rate = 0
            else:
                pass_rate = passed / total if passed > 0 else 0
                
            coverage = test_data.get("coverage", 0)
            
            # Determine status
            status = "HEALTHY"
            issues = []
            
            if age_days > self.config["max_test_age_days"]:
                status = "DEGRADED"
                issues.append(f"Tests are {age_days} days old (max: {self.config['max_test_age_days']})")
                
            if failed > 0:
                status = "UNHEALTHY" 
                issues.append(f"{failed} tests are failing")
                
            if coverage < self.config["min_test_coverage"]:
                if status != "UNHEALTHY":
                    status = "DEGRADED"
                issues.append(f"Test coverage is {coverage:.1%} (min: {self.config['min_test_coverage']:.1%})")
                
            return {
                "status": status,
                "has_tests": True,
                "last_run": last_run.isoformat(),
                "age_days": age_days,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "total": total,
                "pass_rate": pass_rate,
                "coverage": coverage,
                "issues": issues
            }
            
        except Exception as e:
            return {
                "status": "DEGRADED",
                "error": str(e),
                "issues": [f"Error checking test status: {str(e)}"]
            }

    def check_documentation(self, repo_name: str, repo_path: str) -> Dict[str, Any]:
        """Check documentation status of the repository"""
        try:
            # Check for README
            readme_exists = any(os.path.exists(os.path.join(repo_path, f)) 
                               for f in ["README.md", "README", "README.txt"])
            
            # Count documentation files
            doc_count = 0
            total_files = 0
            doc_extensions = [".md", ".rst", ".txt", ".html", ".pdf", ".doc", ".docx"]
            
            for root, _, files in os.walk(repo_path):
                for file in files:
                    total_files += 1
                    if any(file.endswith(ext) for ext in doc_extensions):
                        doc_count += 1
            
            # Calculate doc ratio
            doc_ratio = doc_count / max(total_files, 1)
            
            # Determine status
            status = "HEALTHY"
            issues = []
            
            if not readme_exists:
                status = "DEGRADED"
                issues.append("No README file found")
                
            if doc_ratio < self.config["doc_coverage_threshold"]:
                if status != "UNHEALTHY":
                    status = "DEGRADED"
                issues.append(f"Documentation coverage is {doc_ratio:.1%} (min: {self.config['doc_coverage_threshold']:.1%})")
                
            return {
                "status": status,
                "has_readme": readme_exists,
                "doc_files": doc_count,
                "total_files": total_files,
                "doc_ratio": doc_ratio,
                "issues": issues
            }
            
        except Exception as e:
            return {
                "status": "DEGRADED",
                "error": str(e),
                "issues": [f"Error checking documentation: {str(e)}"]
            }

    def check_build_status(self, repo_name: str) -> Dict[str, Any]:
        """Check build status of the repository"""
        # Look for build results file
        build_results_path = os.path.join("data/status", f"{repo_name}-build.json")
        if not os.path.exists(build_results_path):
            return {
                "status": "UNKNOWN",
                "last_build": None,
                "issues": ["No build results found"]
            }
            
        try:
            with open(build_results_path, 'r') as f:
                build_data = json.load(f)
            
            # Check build age
            last_build = datetime.datetime.fromisoformat(build_data.get("timestamp", "2000-01-01T00:00:00"))
            age_days = (datetime.datetime.now() - last_build).days
            
            # Get build result
            success = build_data.get("success", False)
            
            # Determine status
            status = "HEALTHY" if success else "UNHEALTHY"
            issues = []
            
            if age_days > self.config["min_build_frequency_days"]:
                if status != "UNHEALTHY":
                    status = "DEGRADED"
                issues.append(f"Last build was {age_days} days ago (max: {self.config['min_build_frequency_days']})")
                
            if not success:
                issues.append("Last build failed")
                
            return {
                "status": status,
                "last_build": last_build.isoformat(),
                "age_days": age_days,
                "success": success,
                "build_number": build_data.get("build_number", "unknown"),
                "issues": issues
            }
            
        except Exception as e:
            return {
                "status": "DEGRADED",
                "error": str(e),
                "issues": [f"Error checking build status: {str(e)}"]
            }

    def check_security(self, repo_name: str, repo_path: str) -> Dict[str, Any]:
        """Check security status of the repository"""
        # Look for security scan results file
        security_results_path = os.path.join("data/status", f"{repo_name}-security.json")
        if not os.path.exists(security_results_path):
            return {
                "status": "UNKNOWN",
                "last_scan": None,
                "issues": ["No security scan results found"]
            }
            
        try:
            with open(security_results_path, 'r') as f:
                security_data = json.load(f)
            
            # Check scan age
            last_scan = datetime.datetime.fromisoformat(security_data.get("timestamp", "2000-01-01T00:00:00"))
            age_days = (datetime.datetime.now() - last_scan).days
            
            # Get security issues
            critical = security_data.get("critical", 0)
            high = security_data.get("high", 0)
            medium = security_data.get("medium", 0)
            low = security_data.get("low", 0)
            
            # Determine status
            status = "HEALTHY"
            issues = []
            
            if age_days > self.config["security_scan_frequency_days"]:
                status = "DEGRADED"
                issues.append(f"Security scan is {age_days} days old (max: {self.config['security_scan_frequency_days']})")
                
            if critical > 0:
                status = "UNHEALTHY"
                issues.append(f"{critical} critical security issues found")
                
            if high > 0:
                if status != "UNHEALTHY":
                    status = "DEGRADED"
                issues.append(f"{high} high severity security issues found")
                
            return {
                "status": status,
                "last_scan": last_scan.isoformat(),
                "age_days": age_days,
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low,
                "total_issues": critical + high + medium + low,
                "issues": issues
            }
            
        except Exception as e:
            return {
                "status": "DEGRADED",
                "error": str(e),
                "issues": [f"Error checking security status: {str(e)}"]
            }

    def check_dependencies(self, repo_name: str, repo_path: str) -> Dict[str, Any]:
        """Check dependency status of the repository"""
        # Look for package files
        package_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file in ["package.json", "requirements.txt", "Cargo.toml", "go.mod", "pom.xml", "build.gradle"]:
                    package_files.append(os.path.join(root, file))
                    
        if not package_files:
            return {
                "status": "UNKNOWN",
                "has_package_file": False,
                "issues": ["No package files found"]
            }
            
        # Check for dependency update file
        dependency_results_path = os.path.join("data/status", f"{repo_name}-dependencies.json")
        if not os.path.exists(dependency_results_path):
            return {
                "status": "UNKNOWN",
                "has_package_file": True,
                "package_files": package_files,
                "issues": ["No dependency scan results found"]
            }
            
        try:
            with open(dependency_results_path, 'r') as f:
                dependency_data = json.load(f)
            
            # Check update age
            last_update = datetime.datetime.fromisoformat(dependency_data.get("timestamp", "2000-01-01T00:00:00"))
            age_days = (datetime.datetime.now() - last_update).days
            
            # Get outdated dependencies
            outdated = dependency_data.get("outdated", 0)
            total = dependency_data.get("total", 0)
            
            # Calculate outdated ratio
            outdated_ratio = outdated / max(total, 1)
            
            # Determine status
            status = "HEALTHY"
            issues = []
            
            if age_days > self.config["max_dependency_age_days"]:
                status = "DEGRADED"
                issues.append(f"Dependency scan is {age_days} days old (max: {self.config['max_dependency_age_days']})")
                
            if outdated_ratio > self.config["allowed_failure_rate"]:
                if status != "UNHEALTHY":
                    status = "DEGRADED"
                issues.append(f"{outdated} of {total} dependencies are outdated ({outdated_ratio:.1%})")
                
            return {
                "status": status,
                "has_package_file": True,
                "package_files": package_files,
                "last_update": last_update.isoformat(),
                "age_days": age_days,
                "outdated": outdated,
                "total": total,
                "outdated_ratio": outdated_ratio,
                "issues": issues
            }
            
        except Exception as e:
            return {
                "status": "DEGRADED",
                "error": str(e),
                "issues": [f"Error checking dependencies: {str(e)}"]
            }

    def save_analysis(self, repo_name: str, analysis: Dict[str, Any]) -> None:
        """Save analysis results to file"""
        file_path = os.path.join(ANALYSIS_DIR, f"{repo_name}.json")
        with open(file_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"Analysis saved to: {file_path}")
        
    def list_repositories(self) -> List[str]:
        """List all repositories in the system components directory"""
        if not os.path.isdir(REPOS_DIR):
            return []
            
        return [
            d for d in os.listdir(REPOS_DIR) 
            if os.path.isdir(os.path.join(REPOS_DIR, d)) and not d.startswith('.')
        ]
        
    def analyze_all(self) -> Dict[str, Dict[str, Any]]:
        """Analyze all repositories"""
        repos = self.list_repositories()
        results = {}
        
        for repo in repos:
            result = self.analyze_repository(repo)
            results[repo] = result
            
        return results
        
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of all repository analyses"""
        repos = self.list_repositories()
        summaries = {}
        
        for repo in repos:
            analysis_path = os.path.join(ANALYSIS_DIR, f"{repo}.json")
            if os.path.exists(analysis_path):
                with open(analysis_path, 'r') as f:
                    analysis = json.load(f)
                summaries[repo] = {
                    "status": analysis.get("overall_status", "UNKNOWN"),
                    "timestamp": analysis.get("timestamp", ""),
                    "issue_count": len(analysis.get("issues", [])),
                    "git_status": analysis.get("git_status", {}).get("status", "UNKNOWN"),
                    "test_status": analysis.get("test_status", {}).get("status", "UNKNOWN"),
                    "doc_status": analysis.get("documentation_status", {}).get("status", "UNKNOWN"),
                    "build_status": analysis.get("build_status", {}).get("status", "UNKNOWN"),
                    "security_status": analysis.get("security_status", {}).get("status", "UNKNOWN"),
                    "dependency_status": analysis.get("dependency_status", {}).get("status", "UNKNOWN")
                }
        
        summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "repository_count": len(summaries),
            "healthy_count": sum(1 for repo in summaries.values() if repo["status"] == "HEALTHY"),
            "degraded_count": sum(1 for repo in summaries.values() if repo["status"] == "DEGRADED"),
            "unhealthy_count": sum(1 for repo in summaries.values() if repo["status"] == "UNHEALTHY"),
            "unknown_count": sum(1 for repo in summaries.values() if repo["status"] == "UNKNOWN"),
            "repositories": summaries
        }
        
        # Save summary
        file_path = os.path.join("data/summaries", "repository_summary.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"Summary saved to: {file_path}")
        return summary


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="HMS Repository Analyzer")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
    
    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a repository")
    analyze_parser.add_argument("repository", help="Repository name to analyze")
    analyze_parser.add_argument("--path", help="Repository path (optional)")
    
    # analyze-all command
    subparsers.add_parser("analyze-all", help="Analyze all repositories")
    
    # list command
    subparsers.add_parser("list", help="List all repositories")
    
    # summary command
    subparsers.add_parser("summary", help="Generate a summary of all repository analyses")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = RepositoryAnalyzer()
    
    # Execute command
    if args.command == "analyze":
        result = analyzer.analyze_repository(args.repository, args.path)
        print(json.dumps(result, indent=2))
    elif args.command == "analyze-all":
        results = analyzer.analyze_all()
        print(f"Analyzed {len(results)} repositories")
    elif args.command == "list":
        repos = analyzer.list_repositories()
        for repo in repos:
            print(repo)
        print(f"Found {len(repos)} repositories")
    elif args.command == "summary":
        summary = analyzer.generate_summary()
        print(f"Total repositories: {summary['repository_count']}")
        print(f"Healthy: {summary['healthy_count']}")
        print(f"Degraded: {summary['degraded_count']}")
        print(f"Unhealthy: {summary['unhealthy_count']}")
        print(f"Unknown: {summary['unknown_count']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()