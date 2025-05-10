#!/usr/bin/env python3
"""
Moneyball Deal Model Implementation Validation Framework

This script validates the Moneyball Deal Model implementation against formal
specifications and generates a comprehensive validation report.
"""

import os
import sys
import unittest
import json
import time
import importlib
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Try to import the test suite
try:
    from test_moneyball_model import (
        TestMoneyballModelCore,
        TestWinWinCalculation,
        TestDealMonitoring,
        TestO3Optimization,
        TestIntegration
    )
    TEST_IMPORT_SUCCESS = True
except ImportError:
    TEST_IMPORT_SUCCESS = False

# Try to import implementation modules
try:
    import moneyball_deal_model
    import win_win_calculation_framework
    import deal_monitoring_system
    import o3_deal_roadmap_optimization
    IMPLEMENTATION_IMPORT_SUCCESS = True
except ImportError:
    IMPLEMENTATION_IMPORT_SUCCESS = False

def check_file_existence(files: List[str]) -> Dict[str, bool]:
    """
    Check if required files exist.
    
    Args:
        files: List of file paths to check
        
    Returns:
        Dictionary mapping file paths to existence status
    """
    return {file_path: os.path.exists(file_path) for file_path in files}

def run_tests() -> Tuple[unittest.TestResult, float]:
    """
    Run the test suite.
    
    Returns:
        Tuple of (test result, execution time)
    """
    if not TEST_IMPORT_SUCCESS:
        print("Error: Could not import test modules. Skipping tests.")
        return None, 0.0
    
    # Create a test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMoneyballModelCore))
    suite.addTest(unittest.makeSuite(TestWinWinCalculation))
    suite.addTest(unittest.makeSuite(TestDealMonitoring))
    suite.addTest(unittest.makeSuite(TestO3Optimization))
    suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run the tests
    start_time = time.time()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    end_time = time.time()
    
    return result, end_time - start_time

def analyze_implementation(files: Dict[str, bool]) -> Dict[str, Any]:
    """
    Analyze the implementation completeness.
    
    Args:
        files: Dictionary mapping file paths to existence status
        
    Returns:
        Dictionary of analysis results
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "files_analyzed": len(files),
        "files_present": sum(1 for exists in files.values() if exists),
        "files_missing": sum(1 for exists in files.values() if not exists),
        "components": {},
        "overall_completeness": 0.0
    }
    
    # Define required components and their key elements
    required_components = {
        "moneyball_deal_model.py": {
            "classes": ["Intent", "Solution", "Stakeholder", "FinancingStructure", "ExecutionPlan", "Deal"],
            "functions": ["create_moneyball_deal", "analyze_deal_value", "match_solutions", "map_stakeholders", "optimize_financing"]
        },
        "win_win_calculation_framework.py": {
            "classes": ["EntityProfile", "ValueComponent", "EntityValue"],
            "functions": ["calculate_entity_value", "translate_value_dimension", "ensure_win_win_outcome", "verify_deal_integrity", "calculate_value_distribution"]
        },
        "deal_monitoring_system.py": {
            "classes": ["DealMetric", "MonitoringAlert", "DealStatus", "HistoricalPerformance", "PredictiveModel", "DealMonitoringSystem"],
            "functions": []
        },
        "o3_deal_roadmap_optimization.py": {
            "classes": ["EntityNode", "ValueEdge", "DealHyperedge", "DealRoadmap", "DealHypergraph", "O3Optimizer"],
            "functions": []
        }
    }
    
    # Check each component
    for file_path, file_exists in files.items():
        file_name = os.path.basename(file_path)
        
        if file_name not in required_components:
            continue
        
        component_results = {
            "file_exists": file_exists,
            "classes": {},
            "functions": {},
            "completeness": 0.0
        }
        
        if file_exists:
            # Check for required classes and functions
            required_classes = required_components[file_name]["classes"]
            required_functions = required_components[file_name]["functions"]
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check classes
                for cls in required_classes:
                    class_exists = f"class {cls}" in content
                    component_results["classes"][cls] = class_exists
                
                # Check functions
                for func in required_functions:
                    func_match = re.search(rf"def\s+{func}\s*\(", content)
                    func_exists = bool(func_match)
                    component_results["functions"][func] = func_exists
                
                # Calculate completeness
                total_elements = len(required_classes) + len(required_functions)
                present_elements = sum(1 for exists in component_results["classes"].values() if exists) + \
                                  sum(1 for exists in component_results["functions"].values() if exists)
                
                component_results["completeness"] = present_elements / total_elements if total_elements > 0 else 1.0
            
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                component_results["completeness"] = 0.0
        
        results["components"][file_name] = component_results
    
    # Calculate overall completeness
    if results["components"]:
        overall_completeness = sum(comp["completeness"] for comp in results["components"].values()) / len(results["components"])
        results["overall_completeness"] = overall_completeness
    
    return results

def run_performance_tests() -> Dict[str, Any]:
    """
    Run performance tests on the implementation.
    
    Returns:
        Dictionary of performance test results
    """
    if not IMPLEMENTATION_IMPORT_SUCCESS:
        print("Error: Could not import implementation modules. Skipping performance tests.")
        return {
            "status": "error",
            "message": "Implementation modules not found"
        }
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test O3 optimization performance
    try:
        from o3_deal_roadmap_optimization import DealHypergraph, O3Optimizer, create_example_hypergraph
        
        # Create example hypergraph
        start_time = time.time()
        graph = create_example_hypergraph()
        creation_time = time.time() - start_time
        
        # Test optimization performance
        optimizer = O3Optimizer(graph)
        
        # Optimize deal
        start_time = time.time()
        _ = optimizer.optimize_deal_values("deal1")
        deal_optimization_time = time.time() - start_time
        
        # Optimize roadmap
        start_time = time.time()
        _ = optimizer.optimize_roadmap(max_deals=3)
        roadmap_optimization_time = time.time() - start_time
        
        # Run simulation
        start_time = time.time()
        _ = optimizer.monte_carlo_roadmap_simulation("roadmap1", num_simulations=100)
        simulation_time = time.time() - start_time
        
        results["tests"]["o3_optimization"] = {
            "status": "success",
            "creation_time": creation_time,
            "deal_optimization_time": deal_optimization_time,
            "roadmap_optimization_time": roadmap_optimization_time,
            "simulation_time": simulation_time
        }
    
    except Exception as e:
        results["tests"]["o3_optimization"] = {
            "status": "error",
            "message": str(e)
        }
    
    # Test deal model performance
    try:
        from moneyball_deal_model import create_moneyball_deal, analyze_deal_value
        
        # Test deal creation performance
        start_time = time.time()
        deal = create_moneyball_deal(
            intent_description="Performance test deal",
            solutions=["Solution 1", "Solution 2", "Solution 3"],
            stakeholders=["Stakeholder 1", "Stakeholder 2", "Stakeholder 3", "Stakeholder 4"],
            financing={"public": 1000000, "private": 2000000, "grants": 500000},
            expertise=["Expertise 1", "Expertise 2", "Expertise 3"]
        )
        creation_time = time.time() - start_time
        
        # Test deal analysis performance
        start_time = time.time()
        _ = analyze_deal_value(deal)
        analysis_time = time.time() - start_time
        
        results["tests"]["deal_model"] = {
            "status": "success",
            "creation_time": creation_time,
            "analysis_time": analysis_time
        }
    
    except Exception as e:
        results["tests"]["deal_model"] = {
            "status": "error",
            "message": str(e)
        }
    
    return results

def validate_documentation(file_path: str) -> Dict[str, Any]:
    """
    Validate the model documentation against specifications.
    
    Args:
        file_path: Path to documentation file
        
    Returns:
        Dictionary of validation results
    """
    results = {
        "file_exists": os.path.exists(file_path),
        "sections": {},
        "completeness": 0.0
    }
    
    if not results["file_exists"]:
        return results
    
    # Required documentation sections
    required_sections = [
        "Core Components",
        "Mathematical Framework",
        "Neural Network",
        "Win-Win Calculation",
        "Deal Monitoring System",
        "O3 Optimization",
        "Implementation Tools",
        "Deal Execution Framework",
        "Integration with HMS Ecosystem",
        "Usage Examples"
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check each required section
        for section in required_sections:
            # Check for section headings at various levels (# to ####)
            section_patterns = [
                rf"#\s+{section}",
                rf"##\s+{section}",
                rf"###\s+{section}",
                rf"####\s+{section}"
            ]
            section_exists = any(re.search(pattern, content, re.IGNORECASE) for pattern in section_patterns)
            results["sections"][section] = section_exists
        
        # Calculate completeness
        present_sections = sum(1 for exists in results["sections"].values() if exists)
        results["completeness"] = present_sections / len(required_sections) if required_sections else 1.0
    
    except Exception as e:
        print(f"Error validating documentation {file_path}: {e}")
    
    return results

def generate_validation_report(
    file_existence: Dict[str, bool],
    implementation_analysis: Dict[str, Any],
    test_results: unittest.TestResult,
    test_time: float,
    performance_results: Dict[str, Any],
    documentation_validation: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a comprehensive validation report.
    
    Args:
        file_existence: Dictionary of file existence status
        implementation_analysis: Implementation analysis results
        test_results: Unit test results
        test_time: Time taken to run tests
        performance_results: Performance test results
        documentation_validation: Documentation validation results
        
    Returns:
        Validation report dictionary
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "pass",
        "file_existence": {
            "total": len(file_existence),
            "present": sum(1 for exists in file_existence.values() if exists),
            "missing": sum(1 for exists in file_existence.values() if not exists),
            "details": file_existence
        },
        "implementation_analysis": implementation_analysis,
        "unit_tests": {
            "total": test_results.testsRun if test_results else 0,
            "passed": test_results.testsRun - len(test_results.failures) - len(test_results.errors) if test_results else 0,
            "failures": len(test_results.failures) if test_results else 0,
            "errors": len(test_results.errors) if test_results else 0,
            "execution_time": test_time,
            "details": {
                "failures": [{"test": test[0].id(), "message": test[1]} for test in (test_results.failures if test_results else [])],
                "errors": [{"test": test[0].id(), "message": test[1]} for test in (test_results.errors if test_results else [])]
            }
        },
        "performance_tests": performance_results,
        "documentation_validation": documentation_validation,
        "recommendations": []
    }
    
    # Determine overall status
    if report["file_existence"]["missing"] > 0:
        report["overall_status"] = "fail"
        report["recommendations"].append("Create missing required files")
    
    if implementation_analysis["overall_completeness"] < 0.9:
        report["overall_status"] = "fail"
        report["recommendations"].append("Complete missing implementation components")
    
    if test_results and (len(test_results.failures) > 0 or len(test_results.errors) > 0):
        report["overall_status"] = "fail"
        report["recommendations"].append("Fix failing unit tests")
    
    if "o3_optimization" in performance_results.get("tests", {}) and \
       performance_results["tests"]["o3_optimization"].get("status") == "error":
        report["overall_status"] = "fail"
        report["recommendations"].append("Fix O3 optimization performance issues")
    
    if documentation_validation["completeness"] < 0.9:
        report["overall_status"] = "fail"
        report["recommendations"].append("Complete missing documentation sections")
    
    # Generate specific recommendations
    if implementation_analysis["components"]:
        for component, results in implementation_analysis["components"].items():
            if results["completeness"] < 1.0:
                missing_classes = [cls for cls, exists in results.get("classes", {}).items() if not exists]
                missing_functions = [func for func, exists in results.get("functions", {}).items() if not exists]
                
                if missing_classes:
                    report["recommendations"].append(f"Implement missing classes in {component}: {', '.join(missing_classes)}")
                
                if missing_functions:
                    report["recommendations"].append(f"Implement missing functions in {component}: {', '.join(missing_functions)}")
    
    if documentation_validation["sections"]:
        missing_sections = [section for section, exists in documentation_validation["sections"].items() if not exists]
        if missing_sections:
            report["recommendations"].append(f"Add missing documentation sections: {', '.join(missing_sections)}")
    
    return report

def save_report(report: Dict[str, Any], output_file: str) -> None:
    """
    Save the validation report to a file.
    
    Args:
        report: Validation report dictionary
        output_file: Output file path
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"Validation report saved to {output_file}")
    except Exception as e:
        print(f"Error saving validation report: {e}")

def generate_html_report(report: Dict[str, Any], output_file: str) -> None:
    """
    Generate an HTML version of the validation report.
    
    Args:
        report: Validation report dictionary
        output_file: Output HTML file path
    """
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moneyball Deal Model Validation Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .summary {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .status {
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 3px;
            display: inline-block;
        }
        .pass {
            background-color: #d4edda;
            color: #155724;
        }
        .fail {
            background-color: #f8d7da;
            color: #721c24;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .progress-container {
            width: 100%;
            background-color: #e9ecef;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .progress-bar {
            height: 20px;
            border-radius: 4px;
            background-color: #4CAF50;
            text-align: center;
            line-height: 20px;
            color: white;
        }
        .recommendations {
            background-color: #e2f3f8;
            padding: 15px;
            border-radius: 5px;
        }
        .recommendations ul {
            margin-top: 5px;
        }
        .timestamp {
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .test-details {
            margin-top: 10px;
        }
        .test-detail {
            border-left: 3px solid #dc3545;
            padding-left: 10px;
            margin-bottom: 10px;
        }
        .test-name {
            font-weight: bold;
            color: #495057;
        }
        .test-message {
            font-family: monospace;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            margin-top: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Moneyball Deal Model Validation Report</h1>
        <p class="timestamp">Generated on: {timestamp}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <p>Overall Status: <span class="status {status_class}">{overall_status}</span></p>
            <p>Files: {files_present}/{files_total} present</p>
            <p>Implementation Completeness: 
                <div class="progress-container">
                    <div class="progress-bar" style="width: {implementation_completeness_percent}%">{implementation_completeness_percent}%</div>
                </div>
            </p>
            <p>Tests: {tests_passed}/{tests_total} passed</p>
            <p>Documentation Completeness: 
                <div class="progress-container">
                    <div class="progress-bar" style="width: {documentation_completeness_percent}%">{documentation_completeness_percent}%</div>
                </div>
            </p>
        </div>
        
        <div class="recommendations">
            <h2>Recommendations</h2>
            <ul>
                {recommendations_list}
            </ul>
        </div>
        
        <h2>File Existence</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Status</th>
            </tr>
            {file_existence_rows}
        </table>
        
        <h2>Implementation Analysis</h2>
        {components_tables}
        
        <h2>Unit Tests</h2>
        <p>Total Tests: {tests_total}</p>
        <p>Passed: {tests_passed}</p>
        <p>Failures: {tests_failures}</p>
        <p>Errors: {tests_errors}</p>
        <p>Execution Time: {test_execution_time:.2f} seconds</p>
        
        {test_details}
        
        <h2>Performance Tests</h2>
        {performance_tables}
        
        <h2>Documentation Validation</h2>
        <p>Documentation File: {documentation_file}</p>
        <p>Completeness: 
            <div class="progress-container">
                <div class="progress-bar" style="width: {documentation_completeness_percent}%">{documentation_completeness_percent}%</div>
            </div>
        </p>
        <table>
            <tr>
                <th>Section</th>
                <th>Status</th>
            </tr>
            {documentation_section_rows}
        </table>
    </div>
</body>
</html>
"""
    
    # Prepare the template variables
    timestamp = datetime.fromisoformat(report["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    status_class = "pass" if report["overall_status"] == "pass" else "fail"
    overall_status = "PASS" if report["overall_status"] == "pass" else "FAIL"
    
    files_total = report["file_existence"]["total"]
    files_present = report["file_existence"]["present"]
    
    implementation_completeness = report["implementation_analysis"]["overall_completeness"]
    implementation_completeness_percent = int(implementation_completeness * 100)
    
    tests_total = report["unit_tests"]["total"]
    tests_passed = report["unit_tests"]["passed"]
    tests_failures = report["unit_tests"]["failures"]
    tests_errors = report["unit_tests"]["errors"]
    test_execution_time = report["unit_tests"]["execution_time"]
    
    documentation_completeness = report["documentation_validation"]["completeness"]
    documentation_completeness_percent = int(documentation_completeness * 100)
    
    # Generate file existence rows
    file_existence_rows = ""
    for file_path, exists in report["file_existence"]["details"].items():
        status = "Present" if exists else "Missing"
        status_class = "pass" if exists else "fail"
        file_existence_rows += f"""
            <tr>
                <td>{file_path}</td>
                <td><span class="status {status_class}">{status}</span></td>
            </tr>
        """
    
    # Generate implementation component tables
    components_tables = ""
    for component, data in report["implementation_analysis"]["components"].items():
        component_completeness = data["completeness"]
        component_completeness_percent = int(component_completeness * 100)
        
        components_tables += f"""
            <h3>{component}</h3>
            <p>Completeness: 
                <div class="progress-container">
                    <div class="progress-bar" style="width: {component_completeness_percent}%">{component_completeness_percent}%</div>
                </div>
            </p>
        """
        
        # Classes table
        if data["classes"]:
            components_tables += """
                <h4>Classes</h4>
                <table>
                    <tr>
                        <th>Class</th>
                        <th>Status</th>
                    </tr>
            """
            
            for cls, exists in data["classes"].items():
                status = "Implemented" if exists else "Missing"
                status_class = "pass" if exists else "fail"
                components_tables += f"""
                    <tr>
                        <td>{cls}</td>
                        <td><span class="status {status_class}">{status}</span></td>
                    </tr>
                """
            
            components_tables += """
                </table>
            """
        
        # Functions table
        if data["functions"]:
            components_tables += """
                <h4>Functions</h4>
                <table>
                    <tr>
                        <th>Function</th>
                        <th>Status</th>
                    </tr>
            """
            
            for func, exists in data["functions"].items():
                status = "Implemented" if exists else "Missing"
                status_class = "pass" if exists else "fail"
                components_tables += f"""
                    <tr>
                        <td>{func}</td>
                        <td><span class="status {status_class}">{status}</span></td>
                    </tr>
                """
            
            components_tables += """
                </table>
            """
    
    # Generate test details
    test_details = ""
    if report["unit_tests"]["failures"] or report["unit_tests"]["errors"]:
        test_details += "<h3>Test Failures and Errors</h3>"
        test_details += "<div class='test-details'>"
        
        for failure in report["unit_tests"]["details"]["failures"]:
            test_details += f"""
                <div class="test-detail">
                    <div class="test-name">{failure["test"]}</div>
                    <div class="test-message">{failure["message"]}</div>
                </div>
            """
        
        for error in report["unit_tests"]["details"]["errors"]:
            test_details += f"""
                <div class="test-detail">
                    <div class="test-name">{error["test"]}</div>
                    <div class="test-message">{error["message"]}</div>
                </div>
            """
        
        test_details += "</div>"
    
    # Generate performance tables
    performance_tables = ""
    for test_name, test_data in report["performance_tests"].get("tests", {}).items():
        status = test_data.get("status", "unknown")
        status_class = "pass" if status == "success" else "fail"
        
        performance_tables += f"""
            <h3>{test_name}</h3>
            <p>Status: <span class="status {status_class}">{status}</span></p>
        """
        
        if status == "success":
            performance_tables += "<table>"
            for key, value in test_data.items():
                if key != "status":
                    performance_tables += f"""
                        <tr>
                            <td>{key.replace('_', ' ').title()}</td>
                            <td>{value:.4f} seconds</td>
                        </tr>
                    """
            performance_tables += "</table>"
        else:
            performance_tables += f"<p>Error: {test_data.get('message', 'Unknown error')}</p>"
    
    # Generate documentation section rows
    documentation_file = "moneyball_deal_model.md"
    documentation_section_rows = ""
    for section, exists in report["documentation_validation"]["sections"].items():
        status = "Present" if exists else "Missing"
        status_class = "pass" if exists else "fail"
        documentation_section_rows += f"""
            <tr>
                <td>{section}</td>
                <td><span class="status {status_class}">{status}</span></td>
            </tr>
        """
    
    # Generate recommendations list
    recommendations_list = ""
    for recommendation in report["recommendations"]:
        recommendations_list += f"<li>{recommendation}</li>"
    
    # Substitute values in template
    html_content = html_template.format(
        timestamp=timestamp,
        status_class=status_class,
        overall_status=overall_status,
        files_present=files_present,
        files_total=files_total,
        implementation_completeness_percent=implementation_completeness_percent,
        tests_passed=tests_passed,
        tests_total=tests_total,
        documentation_completeness_percent=documentation_completeness_percent,
        recommendations_list=recommendations_list,
        file_existence_rows=file_existence_rows,
        components_tables=components_tables,
        tests_failures=tests_failures,
        tests_errors=tests_errors,
        test_execution_time=test_execution_time,
        test_details=test_details,
        performance_tables=performance_tables,
        documentation_file=documentation_file,
        documentation_section_rows=documentation_section_rows
    )
    
    # Save HTML report
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML validation report saved to {output_file}")
    except Exception as e:
        print(f"Error saving HTML validation report: {e}")

def main():
    """Main function for the validation framework."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Required files to check
    required_files = [
        os.path.join(base_dir, "moneyball_deal_model.py"),
        os.path.join(base_dir, "win_win_calculation_framework.py"),
        os.path.join(base_dir, "deal_monitoring_system.py"),
        os.path.join(base_dir, "o3_deal_roadmap_optimization.py"),
        os.path.join(base_dir, "update_agency_docs.py"),
        os.path.join(base_dir, "deploy_moneyball_model.py"),
        os.path.join(base_dir, "implementation_script.py"),
        os.path.join(base_dir, "agency_deal_template.md"),
        os.path.join(base_dir, "moneyball_deal_model.md"),
        os.path.join(base_dir, "test_moneyball_model.py")
    ]
    
    print("Validating Moneyball Deal Model Implementation...")
    
    # Step 1: Check file existence
    print("\nChecking required files...")
    file_existence = check_file_existence(required_files)
    for file_path, exists in file_existence.items():
        print(f"  {'✓' if exists else '✗'} {os.path.basename(file_path)}")
    
    # Step 2: Analyze implementation
    print("\nAnalyzing implementation completeness...")
    implementation_analysis = analyze_implementation(file_existence)
    print(f"  Overall completeness: {implementation_analysis['overall_completeness']:.2%}")
    
    # Step 3: Run tests
    print("\nRunning tests...")
    test_results, test_time = run_tests()
    if test_results:
        print(f"  Tests run: {test_results.testsRun}")
        print(f"  Tests passed: {test_results.testsRun - len(test_results.failures) - len(test_results.errors)}")
        print(f"  Failures: {len(test_results.failures)}")
        print(f"  Errors: {len(test_results.errors)}")
        print(f"  Execution time: {test_time:.2f} seconds")
    else:
        print("  Tests could not be run")
    
    # Step 4: Run performance tests
    print("\nRunning performance tests...")
    performance_results = run_performance_tests()
    
    # Step 5: Validate documentation
    print("\nValidating documentation...")
    documentation_file = os.path.join(base_dir, "moneyball_deal_model.md")
    documentation_validation = validate_documentation(documentation_file)
    print(f"  Documentation completeness: {documentation_validation['completeness']:.2%}")
    
    # Step 6: Generate validation report
    print("\nGenerating validation report...")
    report = generate_validation_report(
        file_existence,
        implementation_analysis,
        test_results,
        test_time,
        performance_results,
        documentation_validation
    )
    
    # Save reports
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    json_report_path = os.path.join(reports_dir, f"validation_report_{timestamp}.json")
    html_report_path = os.path.join(reports_dir, f"validation_report_{timestamp}.html")
    
    save_report(report, json_report_path)
    generate_html_report(report, html_report_path)
    
    # Print summary
    print("\nValidation Summary:")
    print(f"  Overall Status: {'PASS' if report['overall_status'] == 'pass' else 'FAIL'}")
    print(f"  Files Present: {report['file_existence']['present']}/{report['file_existence']['total']}")
    print(f"  Implementation Completeness: {implementation_analysis['overall_completeness']:.2%}")
    print(f"  Tests Passed: {report['unit_tests']['passed']}/{report['unit_tests']['total']}")
    print(f"  Documentation Completeness: {documentation_validation['completeness']:.2%}")
    
    if report["recommendations"]:
        print("\nRecommendations:")
        for i, recommendation in enumerate(report["recommendations"], 1):
            print(f"  {i}. {recommendation}")
    
    print(f"\nDetailed reports saved to:")
    print(f"  - {json_report_path}")
    print(f"  - {html_report_path}")
    
    return 0 if report["overall_status"] == "pass" else 1

if __name__ == "__main__":
    sys.exit(main())