"""
File-based Data Source

Extension point implementation for file-based data sources (CSV, JSON, etc.)
"""

from typing import Dict, List, Any, Optional, AsyncIterator, Union
import json
import csv
import os
import aiofiles
import asyncio
from . import DataSourceExtensionPoint
from .. import base


@base.BaseExtensionPoint.extension_point("data_source", "file")
class FileDataSource(DataSourceExtensionPoint):
    """Implementation of data source extension point for file-based data."""
    
    def __init__(self):
        self.file_path = None
        self.file_type = None
        self.delimiter = ","
        self.encoding = "utf-8"
        self.is_connected = False
        self._data = None
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """
        Connect to a file-based data source.
        
        Args:
            config: Configuration with file_path, file_type, etc.
            
        Returns:
            bool: True if connection successful
        """
        try:
            self.file_path = config["file_path"]
            self.file_type = config.get("file_type", "").lower()
            
            # If file type not provided, infer from extension
            if not self.file_type and self.file_path:
                _, ext = os.path.splitext(self.file_path)
                self.file_type = ext.lstrip(".").lower()
            
            # Set other parameters
            self.delimiter = config.get("delimiter", ",")
            self.encoding = config.get("encoding", "utf-8")
            
            # Check if file exists
            if not os.path.exists(self.file_path):
                return False
            
            # For small files, we might load the entire contents
            if config.get("preload", False):
                await self._load_data()
                
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Error connecting to file data source: {e}")
            return False
    
    async def _load_data(self) -> None:
        """Load the entire file into memory."""
        if self.file_type == "csv":
            async with aiofiles.open(self.file_path, mode='r', encoding=self.encoding) as f:
                content = await f.read()
                reader = csv.DictReader(content.splitlines(), delimiter=self.delimiter)
                self._data = list(reader)
        elif self.file_type == "json":
            async with aiofiles.open(self.file_path, mode='r', encoding=self.encoding) as f:
                content = await f.read()
                self._data = json.loads(content)
    
    async def disconnect(self) -> None:
        """Disconnect from the file data source."""
        self.is_connected = False
        self._data = None
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query data from the file.
        
        Args:
            query_params: Parameters for filtering data
            
        Returns:
            List of matching records
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to data source")
        
        # If data is preloaded, filter in memory
        if self._data is not None:
            result = self._data
            
            # Apply filters
            for key, value in query_params.get("filters", {}).items():
                if isinstance(result, list):
                    result = [item for item in result if item.get(key) == value]
                elif isinstance(result, dict):
                    # For JSON objects with nested structure
                    # This is a simplified implementation
                    # Real implementation would need more complex filtering
                    pass
            
            # Apply limit
            limit = query_params.get("limit")
            if limit and isinstance(result, list):
                result = result[:limit]
                
            return result
        
        # For larger files, we need to read and filter line by line
        # This is a simplified implementation
        if self.file_type == "csv":
            result = []
            async with aiofiles.open(self.file_path, mode='r', encoding=self.encoding) as f:
                content = await f.read()
                reader = csv.DictReader(content.splitlines(), delimiter=self.delimiter)
                
                filters = query_params.get("filters", {})
                limit = query_params.get("limit")
                
                for row in reader:
                    matches = all(row.get(k) == v for k, v in filters.items())
                    if matches:
                        result.append(row)
                        if limit and len(result) >= limit:
                            break
                            
            return result
        elif self.file_type == "json":
            async with aiofiles.open(self.file_path, mode='r', encoding=self.encoding) as f:
                content = await f.read()
                data = json.loads(content)
                
                # Apply filters - assuming data is a list of objects
                if isinstance(data, list):
                    filters = query_params.get("filters", {})
                    result = [item for item in data if all(item.get(k) == v for k, v in filters.items())]
                    
                    # Apply limit
                    limit = query_params.get("limit")
                    if limit:
                        result = result[:limit]
                        
                    return result
                
                return data
        
        return []
    
    async def stream(self, query_params: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream data from the file source.
        
        Args:
            query_params: Parameters for filtering the stream
            
        Yields:
            Data records one by one
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to data source")
            
        filters = query_params.get("filters", {})
        
        if self.file_type == "csv":
            async with aiofiles.open(self.file_path, mode='r', encoding=self.encoding) as f:
                # Read header
                header = await f.readline()
                header = header.strip().split(self.delimiter)
                
                # Read data lines
                async for line in f:
                    values = line.strip().split(self.delimiter)
                    record = dict(zip(header, values))
                    
                    # Apply filters
                    matches = all(record.get(k) == v for k, v in filters.items())
                    if matches:
                        yield record
        elif self.file_type == "json":
            # For JSON, we might need to read the whole file
            # This is not truly streaming but a simplification
            async with aiofiles.open(self.file_path, mode='r', encoding=self.encoding) as f:
                content = await f.read()
                data = json.loads(content)
                
                if isinstance(data, list):
                    for item in data:
                        # Apply filters
                        matches = all(item.get(k) == v for k, v in filters.items())
                        if matches:
                            yield item
                            await asyncio.sleep(0)  # Allow other tasks to run
    
    async def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> bool:
        """
        Insert data into the file.
        
        Args:
            data: Data record(s) to insert
            
        Returns:
            bool: True if insertion successful
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to data source")
            
        try:
            if self.file_type == "csv":
                # If file is empty, create with header
                file_empty = os.path.getsize(self.file_path) == 0
                
                if isinstance(data, dict):
                    data = [data]
                    
                if file_empty:
                    # Create file with header and first record
                    fieldnames = data[0].keys()
                    async with aiofiles.open(self.file_path, mode='w', encoding=self.encoding) as f:
                        header = self.delimiter.join(fieldnames) + "\n"
                        await f.write(header)
                        
                        for record in data:
                            row = self.delimiter.join(str(record.get(field, "")) for field in fieldnames) + "\n"
                            await f.write(row)
                else:
                    # Append to existing file
                    # First, get the header
                    async with aiofiles.open(self.file_path, mode='r', encoding=self.encoding) as f:
                        header_line = await f.readline()
                        fieldnames = header_line.strip().split(self.delimiter)
                    
                    # Then append records
                    async with aiofiles.open(self.file_path, mode='a', encoding=self.encoding) as f:
                        for record in data:
                            row = self.delimiter.join(str(record.get(field, "")) for field in fieldnames) + "\n"
                            await f.write(row)
            
            elif self.file_type == "json":
                # Read existing data
                existing_data = []
                if os.path.getsize(self.file_path) > 0:
                    async with aiofiles.open(self.file_path, mode='r', encoding=self.encoding) as f:
                        content = await f.read()
                        existing_data = json.loads(content)
                
                # Append new data
                if isinstance(existing_data, list):
                    if isinstance(data, dict):
                        existing_data.append(data)
                    else:
                        existing_data.extend(data)
                        
                    # Write back to file
                    async with aiofiles.open(self.file_path, mode='w', encoding=self.encoding) as f:
                        await f.write(json.dumps(existing_data, indent=2))
                else:
                    # If existing data is not a list, this is more complex
                    # and depends on specific requirements
                    pass
                    
            return True
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema of the data source.
        
        Returns:
            Dict describing the data schema
        """
        schema = {
            "type": "file",
            "format": self.file_type,
            "fields": {},
        }
        
        # For CSV, infer schema from header
        if self.file_type == "csv" and os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                header = f.readline().strip().split(self.delimiter)
                schema["fields"] = {field: {"type": "string"} for field in header}
                
                # Try to infer types from first data row
                if f.readable():
                    data_row = f.readline().strip().split(self.delimiter)
                    for i, value in enumerate(data_row):
                        if i < len(header):
                            field = header[i]
                            if value.isdigit():
                                schema["fields"][field]["type"] = "integer"
                            elif value.replace(".", "", 1).isdigit():
                                schema["fields"][field]["type"] = "float"
        
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
            "update": False,
            "delete": False,
            "transactions": False,
        }
        return supported_features.get(feature_name, False)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this data source.
        
        Returns:
            Dict describing capabilities
        """
        return {
            "readable": True,
            "writable": True,
            "streamable": True,
            "queryable": True,
            "batchable": True,
            "transactional": False,
            "supports_concurrent_access": False,
            "supported_formats": ["csv", "json"],
        }