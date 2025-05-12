"""
API-based Data Source

Extension point implementation for API-based data sources (REST, GraphQL, etc.)
"""

from typing import Dict, List, Any, Optional, AsyncIterator, Union
import json
import os
import asyncio
import logging
import aiohttp
from . import DataSourceExtensionPoint
from .. import base

logger = logging.getLogger(__name__)

@base.BaseExtensionPoint.extension_point("data_source", "api")
class APIDataSource(DataSourceExtensionPoint):
    """Implementation of data source extension point for API-based data."""
    
    def __init__(self):
        self.base_url = None
        self.api_type = None
        self.headers = {}
        self.auth = None
        self.timeout = 30
        self.session = None
        self.is_connected = False
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """
        Connect to an API data source.
        
        Args:
            config: Configuration with base_url, headers, etc.
            
        Returns:
            bool: True if connection successful
        """
        try:
            self.base_url = config["base_url"].rstrip("/")
            self.api_type = config.get("api_type", "rest").lower()
            
            # Headers
            self.headers = config.get("headers", {})
            
            # Authentication
            auth_config = config.get("auth", {})
            if auth_config:
                auth_type = auth_config.get("type", "").lower()
                
                if auth_type == "basic":
                    from aiohttp import BasicAuth
                    self.auth = BasicAuth(
                        login=auth_config.get("username", ""),
                        password=auth_config.get("password", ""),
                    )
                elif auth_type == "bearer":
                    token = auth_config.get("token", "")
                    self.headers["Authorization"] = f"Bearer {token}"
                elif auth_type == "api_key":
                    key_name = auth_config.get("key_name", "api_key")
                    key_value = auth_config.get("key_value", "")
                    key_in = auth_config.get("in", "header").lower()
                    
                    if key_in == "header":
                        self.headers[key_name] = key_value
                    # For query params, we'll handle this during request building
            
            # Timeout
            self.timeout = config.get("timeout", 30)
            
            # Create session
            session_timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                auth=self.auth,
                timeout=session_timeout,
            )
            
            # Test connection
            if config.get("test_connection", True):
                test_endpoint = config.get("test_endpoint", "")
                url = f"{self.base_url}/{test_endpoint.lstrip('/')}" if test_endpoint else self.base_url
                
                async with self.session.get(url) as response:
                    if response.status >= 400:
                        logger.error(f"Error testing API connection: {response.status}")
                        await self.session.close()
                        return False
            
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Error connecting to API data source: {e}")
            if self.session:
                await self.session.close()
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the API data source."""
        if self.session:
            await self.session.close()
        self.is_connected = False
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query data from the API.
        
        Args:
            query_params: Parameters for querying the API
            
        Returns:
            List of data records from the API
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to data source")
        
        try:
            if self.api_type == "rest":
                endpoint = query_params.get("endpoint", "")
                method = query_params.get("method", "GET").upper()
                params = query_params.get("params", {})
                data = query_params.get("data")
                json_data = query_params.get("json")
                
                url = f"{self.base_url}/{endpoint.lstrip('/')}"
                
                # Make the request
                async with getattr(self.session, method.lower())(
                    url,
                    params=params,
                    data=data,
                    json=json_data,
                ) as response:
                    if response.status >= 400:
                        logger.error(f"API error: {response.status} - {await response.text()}")
                        return []
                        
                    if response.content_type == 'application/json':
                        result = await response.json()
                        
                        # Extract data from result based on path
                        data_path = query_params.get("data_path", "")
                        if data_path:
                            for key in data_path.split('.'):
                                if key in result:
                                    result = result[key]
                                else:
                                    logger.warning(f"Data path key '{key}' not found in response")
                                    result = []
                                    break
                        
                        # Ensure result is a list
                        if not isinstance(result, list):
                            if isinstance(result, dict):
                                result = [result]
                            else:
                                logger.warning("API response is not a list or dict")
                                result = []
                                
                        return result
                    else:
                        logger.warning(f"Unexpected content type: {response.content_type}")
                        return []
                        
            elif self.api_type == "graphql":
                endpoint = query_params.get("endpoint", "")
                query = query_params.get("query", "")
                variables = query_params.get("variables", {})
                operation_name = query_params.get("operation_name")
                
                if not query:
                    logger.error("GraphQL query is required")
                    return []
                
                url = f"{self.base_url}/{endpoint.lstrip('/')}" if endpoint else self.base_url
                
                # Prepare request
                json_data = {
                    "query": query,
                    "variables": variables,
                }
                
                if operation_name:
                    json_data["operationName"] = operation_name
                
                # Make the request
                async with self.session.post(url, json=json_data) as response:
                    if response.status >= 400:
                        logger.error(f"GraphQL error: {response.status} - {await response.text()}")
                        return []
                    
                    result = await response.json()
                    
                    # Check for GraphQL errors
                    if "errors" in result:
                        errors = result["errors"]
                        logger.error(f"GraphQL errors: {errors}")
                        return []
                    
                    # Extract data
                    if "data" in result:
                        data = result["data"]
                        
                        # Extract by path if provided
                        data_path = query_params.get("data_path", "")
                        if data_path:
                            for key in data_path.split('.'):
                                if key in data:
                                    data = data[key]
                                else:
                                    logger.warning(f"Data path key '{key}' not found in response")
                                    data = []
                                    break
                        
                        # Ensure data is a list
                        if not isinstance(data, list):
                            if isinstance(data, dict):
                                data = [data]
                            else:
                                logger.warning("GraphQL data is not a list or dict")
                                data = []
                                
                        return data
                    else:
                        logger.warning("No data in GraphQL response")
                        return []
                        
            return []
            
        except Exception as e:
            logger.error(f"Error querying API: {e}")
            return []
    
    async def stream(self, query_params: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream data from the API source.
        
        Args:
            query_params: Parameters for streaming from the API
            
        Yields:
            Data records one by one
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to data source")
            
        try:
            if self.api_type == "rest":
                endpoint = query_params.get("endpoint", "")
                method = query_params.get("method", "GET").upper()
                params = query_params.get("params", {})
                
                url = f"{self.base_url}/{endpoint.lstrip('/')}"
                
                # For APIs that support pagination
                page_param = query_params.get("page_param", "page")
                page_size_param = query_params.get("page_size_param", "page_size")
                page_size = query_params.get("page_size", 100)
                max_pages = query_params.get("max_pages")
                
                # Data path for extracting items
                data_path = query_params.get("data_path", "")
                
                # For APIs that use cursors for pagination
                cursor_param = query_params.get("cursor_param", "")
                cursor_path = query_params.get("cursor_path", "")
                
                current_page = 1
                current_cursor = None
                
                while True:
                    # Prepare pagination parameters
                    if cursor_param and current_cursor:
                        # Cursor-based pagination
                        page_params = {cursor_param: current_cursor}
                    else:
                        # Page-based pagination
                        page_params = {
                            page_param: current_page,
                            page_size_param: page_size
                        }
                    
                    # Merge with other params
                    request_params = {**params, **page_params}
                    
                    # Make the request
                    async with getattr(self.session, method.lower())(
                        url,
                        params=request_params,
                    ) as response:
                        if response.status >= 400:
                            logger.error(f"API error: {response.status} - {await response.text()}")
                            break
                            
                        if response.content_type == 'application/json':
                            result = await response.json()
                            
                            # Extract data items
                            items = result
                            if data_path:
                                for key in data_path.split('.'):
                                    if isinstance(items, dict) and key in items:
                                        items = items[key]
                                    else:
                                        logger.warning(f"Data path key '{key}' not found in response")
                                        items = []
                                        break
                            
                            # Ensure items is a list
                            if not isinstance(items, list):
                                if isinstance(items, dict):
                                    items = [items]
                                else:
                                    items = []
                            
                            # Yield each item
                            for item in items:
                                yield item
                                
                            # Check if we should continue pagination
                            if not items:
                                # No more items
                                break
                                
                            # Get next cursor if using cursor-based pagination
                            if cursor_param and cursor_path:
                                current_cursor = None
                                cursor_data = result
                                
                                for key in cursor_path.split('.'):
                                    if isinstance(cursor_data, dict) and key in cursor_data:
                                        cursor_data = cursor_data[key]
                                    else:
                                        break
                                
                                if isinstance(cursor_data, str) and cursor_data:
                                    current_cursor = cursor_data
                                else:
                                    # No more pages
                                    break
                            else:
                                # Increment page for page-based pagination
                                current_page += 1
                            
                            # Check max pages
                            if max_pages and current_page > max_pages:
                                break
                        else:
                            logger.warning(f"Unexpected content type: {response.content_type}")
                            break
                            
            elif self.api_type == "graphql":
                # For GraphQL APIs that support pagination
                endpoint = query_params.get("endpoint", "")
                base_query = query_params.get("query", "")
                variables = query_params.get("variables", {}).copy()
                operation_name = query_params.get("operation_name")
                
                if not base_query:
                    logger.error("GraphQL query is required")
                    return
                
                url = f"{self.base_url}/{endpoint.lstrip('/')}" if endpoint else self.base_url
                
                # Pagination settings
                cursor_param = query_params.get("cursor_param", "after")
                page_size_param = query_params.get("page_size_param", "first")
                page_size = query_params.get("page_size", 100)
                has_next_page_path = query_params.get("has_next_page_path", "pageInfo.hasNextPage")
                next_cursor_path = query_params.get("next_cursor_path", "pageInfo.endCursor")
                max_pages = query_params.get("max_pages")
                
                # Data path for extracting items
                data_path = query_params.get("data_path", "")
                
                variables[page_size_param] = page_size
                current_page = 1
                has_next_page = True
                
                while has_next_page:
                    # Prepare request
                    json_data = {
                        "query": base_query,
                        "variables": variables,
                    }
                    
                    if operation_name:
                        json_data["operationName"] = operation_name
                    
                    # Make the request
                    async with self.session.post(url, json=json_data) as response:
                        if response.status >= 400:
                            logger.error(f"GraphQL error: {response.status} - {await response.text()}")
                            break
                        
                        result = await response.json()
                        
                        # Check for GraphQL errors
                        if "errors" in result:
                            errors = result["errors"]
                            logger.error(f"GraphQL errors: {errors}")
                            break
                        
                        # Extract data
                        if "data" in result:
                            data = result["data"]
                            
                            # Extract items by path
                            items = data
                            if data_path:
                                for key in data_path.split('.'):
                                    if isinstance(items, dict) and key in items:
                                        items = items[key]
                                    else:
                                        logger.warning(f"Data path key '{key}' not found in response")
                                        items = []
                                        break
                            
                            # Ensure items is a list
                            if not isinstance(items, list):
                                if isinstance(items, dict):
                                    items = [items]
                                else:
                                    items = []
                            
                            # Yield each item
                            for item in items:
                                yield item
                            
                            # Check for next page
                            has_next_page = False
                            page_info = data
                            
                            # Extract has_next_page value
                            for key in has_next_page_path.split('.'):
                                if isinstance(page_info, dict) and key in page_info:
                                    page_info = page_info[key]
                                else:
                                    break
                            
                            if isinstance(page_info, bool):
                                has_next_page = page_info
                            
                            # If there's a next page, get the cursor
                            if has_next_page:
                                cursor = data
                                
                                # Extract next_cursor value
                                for key in next_cursor_path.split('.'):
                                    if isinstance(cursor, dict) and key in cursor:
                                        cursor = cursor[key]
                                    else:
                                        cursor = None
                                        break
                                
                                if cursor:
                                    variables[cursor_param] = cursor
                                    current_page += 1
                                else:
                                    has_next_page = False
                            
                            # Check max pages
                            if max_pages and current_page > max_pages:
                                has_next_page = False
                        else:
                            logger.warning("No data in GraphQL response")
                            break
                
        except Exception as e:
            logger.error(f"Error streaming from API: {e}")
    
    async def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> bool:
        """
        Insert data via the API.
        
        Args:
            data: Data record(s) to insert
            
        Returns:
            bool: True if insertion successful
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to data source")
            
        if not isinstance(data, list):
            data = [data]
            
        if not data:
            return True
            
        try:
            if self.api_type == "rest":
                endpoint = data[0].get("_endpoint", "")
                if not endpoint:
                    raise ValueError("Endpoint must be specified in '_endpoint' field")
                
                method = data[0].get("_method", "POST").upper()
                
                # Remove metadata fields
                cleaned_data = []
                for item in data:
                    item_copy = item.copy()
                    if "_endpoint" in item_copy:
                        del item_copy["_endpoint"]
                    if "_method" in item_copy:
                        del item_copy["_method"]
                    cleaned_data.append(item_copy)
                
                url = f"{self.base_url}/{endpoint.lstrip('/')}"
                
                # Send single item or batch depending on API
                if len(cleaned_data) == 1:
                    async with getattr(self.session, method.lower())(
                        url,
                        json=cleaned_data[0],
                    ) as response:
                        if response.status >= 400:
                            logger.error(f"API error: {response.status} - {await response.text()}")
                            return False
                        return True
                else:
                    # Some APIs accept batch operations
                    async with getattr(self.session, method.lower())(
                        url,
                        json=cleaned_data,
                    ) as response:
                        if response.status >= 400:
                            logger.error(f"API batch error: {response.status} - {await response.text()}")
                            return False
                        return True
                        
            elif self.api_type == "graphql":
                endpoint = data[0].get("_endpoint", "")
                mutation = data[0].get("_mutation", "")
                operation_name = data[0].get("_operation_name")
                
                if not mutation:
                    raise ValueError("GraphQL mutation must be specified in '_mutation' field")
                
                # Remove metadata fields and prepare variables
                variables = {}
                for i, item in enumerate(data):
                    item_copy = item.copy()
                    if "_endpoint" in item_copy:
                        del item_copy["_endpoint"]
                    if "_mutation" in item_copy:
                        del item_copy["_mutation"]
                    if "_operation_name" in item_copy:
                        del item_copy["_operation_name"]
                        
                    if len(data) == 1:
                        variables = item_copy
                    else:
                        # For batch operations, structure variables differently
                        variables[f"item{i}"] = item_copy
                
                url = f"{self.base_url}/{endpoint.lstrip('/')}" if endpoint else self.base_url
                
                # Prepare request
                json_data = {
                    "query": mutation,
                    "variables": variables,
                }
                
                if operation_name:
                    json_data["operationName"] = operation_name
                
                # Make the request
                async with self.session.post(url, json=json_data) as response:
                    if response.status >= 400:
                        logger.error(f"GraphQL error: {response.status} - {await response.text()}")
                        return False
                    
                    result = await response.json()
                    
                    # Check for GraphQL errors
                    if "errors" in result:
                        errors = result["errors"]
                        logger.error(f"GraphQL errors: {errors}")
                        return False
                    
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error inserting data via API: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema of the API.
        
        Returns:
            Dict describing the API schema
        """
        schema = {
            "type": "api",
            "api_type": self.api_type,
            "base_url": self.base_url,
        }
        
        # Real implementation would introspect the API schema if available
        # For GraphQL, could use introspection query
        
        return schema
    
    def supports_feature(self, feature_name: str) -> bool:
        """
        Check if a specific feature is supported.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            bool: True if supported
        """
        supported_features = {
            "query": True,
            "stream": True,
            "insert": True,
            "update": self.api_type == "rest",  # GraphQL typically uses mutations for all changes
            "delete": self.api_type == "rest",
            "transactions": False,
        }
        return supported_features.get(feature_name, False)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this data source.
        
        Returns:
            Dict describing capabilities
        """
        capabilities = {
            "readable": True,
            "writable": True,
            "streamable": True,
            "queryable": True,
            "batchable": True,
            "transactional": False,
            "supports_concurrent_access": True,
            "supported_api_types": ["rest", "graphql"],
        }
        
        if self.api_type == "graphql":
            capabilities.update({
                "supports_introspection": True,
            })
            
        return capabilities