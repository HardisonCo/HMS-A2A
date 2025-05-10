"""
GitHub Service for the MAC Demo.

This module provides a service for interacting with GitHub Issues,
supporting the GitHub Issue Resolution Demo.
"""

import logging
import aiohttp
import json
from typing import Dict, Any, List, Optional

class GitHubService:
    """
    GitHub Service for interacting with GitHub Issues.
    
    This service provides methods for fetching, creating, and updating
    GitHub issues for the MAC demonstration.
    """
    
    def __init__(
        self, 
        token: str = "", 
        repo_owner: str = "", 
        repo_name: str = "",
        repository_url: str = None,
        auth_token: str = None
    ):
        """
        Initialize the GitHub Service.
        
        Args:
            token: GitHub API token (deprecated, use auth_token)
            repo_owner: Repository owner/organization
            repo_name: Repository name
            repository_url: Full repository URL (alternative to owner/name)
            auth_token: GitHub API token (preferred over token)
        """
        # Allow either direct owner/name or parse from URL
        self.token = auth_token or token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_base_url = "https://api.github.com"
        self.logger = logging.getLogger("MAC.Demo.GitHubService")
        
        # Parse repository URL if provided
        if repository_url and (not repo_owner or not repo_name):
            try:
                # Extract owner and repo from URL like https://github.com/owner/repo
                url_parts = repository_url.rstrip('/').split('/')
                if len(url_parts) >= 2:
                    # Get the last two parts as owner/repo
                    self.repo_owner = url_parts[-2]
                    self.repo_name = url_parts[-1]
                    self.logger.info(f"Parsed repository: {self.repo_owner}/{self.repo_name}")
            except Exception as e:
                self.logger.error(f"Failed to parse repository URL: {str(e)}")
        
        # Validate essential parameters
        if not self.token:
            self.logger.warning("No GitHub token provided, API access will be limited")
        
        if not self.repo_owner or not self.repo_name:
            self.logger.warning("No repository specified, service will be limited")
    
    async def get_issue(self, issue_number: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a GitHub issue.
        
        Args:
            issue_number: Issue number
            
        Returns:
            Issue data or None if not found
        """
        if not self.repo_owner or not self.repo_name:
            self.logger.error("No repository specified")
            return None
        
        # Construct API URL
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}"
        
        # Set up headers
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        issue_data = await response.json()
                        self.logger.info(f"Fetched issue #{issue_number}")
                        return issue_data
                    else:
                        self.logger.error(f"Failed to fetch issue #{issue_number}: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error fetching issue: {str(e)}")
            return None
    
    async def create_issue(
        self, 
        title: str, 
        body: str, 
        labels: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new GitHub issue.
        
        Args:
            title: Issue title
            body: Issue body
            labels: List of labels
            
        Returns:
            Created issue data or None if failed
        """
        if not self.repo_owner or not self.repo_name:
            self.logger.error("No repository specified")
            return None
        
        if not self.token:
            self.logger.error("No GitHub token provided, cannot create issue")
            return None
        
        # Construct API URL
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/issues"
        
        # Set up headers
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}"
        }
        
        # Create request body
        data = {
            "title": title,
            "body": body
        }
        
        if labels:
            data["labels"] = labels
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 201:
                        issue_data = await response.json()
                        self.logger.info(f"Created issue #{issue_data['number']}: {title}")
                        return issue_data
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to create issue: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error creating issue: {str(e)}")
            return None
    
    async def add_comment(
        self, 
        issue_number: int, 
        body: str
    ) -> Optional[Dict[str, Any]]:
        """
        Add a comment to a GitHub issue.
        
        Args:
            issue_number: Issue number
            body: Comment body
            
        Returns:
            Comment data or None if failed
        """
        if not self.repo_owner or not self.repo_name:
            self.logger.error("No repository specified")
            return None
        
        if not self.token:
            self.logger.error("No GitHub token provided, cannot add comment")
            return None
        
        # Construct API URL
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}/comments"
        
        # Set up headers
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}"
        }
        
        # Create request body
        data = {
            "body": body
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 201:
                        comment_data = await response.json()
                        self.logger.info(f"Added comment to issue #{issue_number}")
                        return comment_data
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to add comment: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error adding comment: {str(e)}")
            return None
    
    async def close_issue(
        self, 
        issue_number: int, 
        comment: Optional[str] = None
    ) -> bool:
        """
        Close a GitHub issue.
        
        Args:
            issue_number: Issue number
            comment: Optional comment to add when closing
            
        Returns:
            True if successful, False otherwise
        """
        if not self.repo_owner or not self.repo_name:
            self.logger.error("No repository specified")
            return False
        
        if not self.token:
            self.logger.error("No GitHub token provided, cannot close issue")
            return False
        
        # Add comment if provided
        if comment:
            comment_result = await self.add_comment(issue_number, comment)
            if not comment_result:
                self.logger.warning(f"Failed to add closing comment to issue #{issue_number}")
        
        # Construct API URL
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}"
        
        # Set up headers
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}"
        }
        
        # Create request body
        data = {
            "state": "closed"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        self.logger.info(f"Closed issue #{issue_number}")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Failed to close issue: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Error closing issue: {str(e)}")
            return False
    
    async def get_repository_issues(
        self, 
        state: str = "open",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get issues from the repository.
        
        Args:
            state: Issue state ("open", "closed", "all")
            limit: Maximum number of issues to return
            
        Returns:
            List of issues
        """
        if not self.repo_owner or not self.repo_name:
            self.logger.error("No repository specified")
            return []
        
        # Construct API URL
        url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/issues"
        
        # Set up headers
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        # Set up parameters
        params = {
            "state": state,
            "per_page": min(limit, 100)  # GitHub API maximum per page
        }
        
        try:
            issues = []
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        issues = await response.json()
                        self.logger.info(f"Fetched {len(issues)} issues from repository")
                        return issues[:limit]
                    else:
                        self.logger.error(f"Failed to fetch issues: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Error fetching issues: {str(e)}")
            return []