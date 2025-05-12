"""
Data Source Extension Points

This module defines interfaces for extending the system with custom data sources.
"""

from typing import Dict, List, Any, Optional, AsyncIterator, Union
import abc
from ..base import BaseExtensionPoint


class DataSourceExtensionPoint(BaseExtensionPoint):
    """
    Extension point for custom data sources.
    
    Allows agencies to integrate custom data sources for disease tracking,
    sample analysis, and other relevant data inputs.
    """
    
    _extension_type: str = "data_source"
    
    @abc.abstractmethod
    async def connect(self, config: Dict[str, Any]) -> bool:
        """
        Establish connection to the data source.
        
        Args:
            config: Configuration parameters for connecting to the data source
            
        Returns:
            bool: True if connection is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the data source."""
        pass
    
    @abc.abstractmethod
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query data from the source.
        
        Args:
            query_params: Parameters defining the query
            
        Returns:
            List of data records matching the query
        """
        pass
    
    @abc.abstractmethod
    async def stream(self, query_params: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream data from the source.
        
        Args:
            query_params: Parameters defining the data stream
            
        Returns:
            AsyncIterator yielding data records
        """
        pass
    
    @abc.abstractmethod
    async def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> bool:
        """
        Insert data into the source.
        
        Args:
            data: Data record(s) to insert
            
        Returns:
            bool: True if insertion is successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema of the data source.
        
        Returns:
            Dict describing the data structure/schema
        """
        pass
    
    @abc.abstractmethod
    def supports_feature(self, feature_name: str) -> bool:
        """
        Check if a specific feature is supported by this data source.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            bool: True if the feature is supported, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this data source.
        
        Returns:
            Dict describing the supported features and capabilities
        """
        pass


# Import specific data source implementations for easy access
from .file_based import FileDataSource
from .database import DatabaseDataSource
from .api_based import APIDataSource

__all__ = [
    'DataSourceExtensionPoint',
    'FileDataSource',
    'DatabaseDataSource',
    'APIDataSource',
]