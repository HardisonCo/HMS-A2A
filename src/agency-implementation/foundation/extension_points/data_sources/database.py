"""
Database Data Source

Extension point implementation for database data sources.
"""

from typing import Dict, List, Any, Optional, AsyncIterator, Union
import json
import os
import asyncio
import logging
from . import DataSourceExtensionPoint
from .. import base

logger = logging.getLogger(__name__)

@base.BaseExtensionPoint.extension_point("data_source", "database")
class DatabaseDataSource(DataSourceExtensionPoint):
    """Implementation of data source extension point for database sources."""
    
    def __init__(self):
        self.connection = None
        self.engine = None
        self.session_factory = None
        self.db_type = None
        self.is_connected = False
    
    async def connect(self, config: Dict[str, Any]) -> bool:
        """
        Connect to a database data source.
        
        Args:
            config: Database connection configuration
            
        Returns:
            bool: True if connection successful
        """
        try:
            self.db_type = config.get("db_type", "").lower()
            
            if self.db_type == "sqlalchemy":
                try:
                    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
                    from sqlalchemy.orm import sessionmaker
                    
                    connection_string = config["connection_string"]
                    
                    # Create engine and session factory
                    self.engine = create_async_engine(
                        connection_string,
                        echo=config.get("echo", False),
                    )
                    
                    self.session_factory = sessionmaker(
                        self.engine, 
                        expire_on_commit=False, 
                        class_=AsyncSession
                    )
                    
                    # Test connection
                    async with self.engine.connect() as conn:
                        await conn.execute("SELECT 1")
                        
                    self.is_connected = True
                    return True
                    
                except ImportError:
                    logger.error("SQLAlchemy not installed or async support not available")
                    return False
                except Exception as e:
                    logger.error(f"Error connecting to database: {e}")
                    return False
            
            elif self.db_type == "aiosqlite":
                try:
                    import aiosqlite
                    
                    db_path = config["db_path"]
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
                    
                    # Connect to the database
                    self.connection = await aiosqlite.connect(db_path)
                    self.connection.row_factory = aiosqlite.Row
                    
                    self.is_connected = True
                    return True
                    
                except ImportError:
                    logger.error("aiosqlite not installed")
                    return False
                except Exception as e:
                    logger.error(f"Error connecting to SQLite database: {e}")
                    return False
            
            elif self.db_type == "asyncpg":
                try:
                    import asyncpg
                    
                    connection_params = {
                        "host": config.get("host", "localhost"),
                        "port": config.get("port", 5432),
                        "user": config.get("user", "postgres"),
                        "password": config.get("password", ""),
                        "database": config.get("database", "postgres"),
                    }
                    
                    # Connect to PostgreSQL
                    self.connection = await asyncpg.connect(**connection_params)
                    
                    self.is_connected = True
                    return True
                    
                except ImportError:
                    logger.error("asyncpg not installed")
                    return False
                except Exception as e:
                    logger.error(f"Error connecting to PostgreSQL database: {e}")
                    return False
                    
            else:
                logger.error(f"Unsupported database type: {self.db_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        try:
            if self.db_type == "sqlalchemy" and self.engine:
                await self.engine.dispose()
                
            elif self.db_type in ["aiosqlite", "asyncpg"] and self.connection:
                await self.connection.close()
                
            self.is_connected = False
            
        except Exception as e:
            logger.error(f"Error disconnecting from database: {e}")
    
    async def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query data from the database.
        
        Args:
            query_params: Query parameters including SQL, table, filters, etc.
            
        Returns:
            List of records matching the query
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to data source")
            
        try:
            if self.db_type == "sqlalchemy":
                table_name = query_params.get("table")
                filters = query_params.get("filters", {})
                limit = query_params.get("limit")
                fields = query_params.get("fields", ["*"])
                
                # For raw SQL queries
                if "sql" in query_params:
                    sql = query_params["sql"]
                    params = query_params.get("params", {})
                    
                    async with self.session_factory() as session:
                        result = await session.execute(sql, params)
                        return [dict(row) for row in result.mappings()]
                
                # For ORM-style queries
                elif table_name:
                    from sqlalchemy import Table, MetaData, select, column
                    
                    metadata = MetaData()
                    table = Table(table_name, metadata, autoload_with=self.engine)
                    
                    # Build query
                    if "*" in fields:
                        query = select(table)
                    else:
                        query = select(*[column(field) for field in fields])
                        
                    # Add filters
                    for key, value in filters.items():
                        if hasattr(table.c, key):
                            query = query.where(getattr(table.c, key) == value)
                    
                    # Add limit
                    if limit:
                        query = query.limit(limit)
                        
                    # Execute query
                    async with self.session_factory() as session:
                        result = await session.execute(query)
                        return [dict(row) for row in result.mappings()]
                        
                return []
                
            elif self.db_type == "aiosqlite":
                # For raw SQL queries
                if "sql" in query_params:
                    sql = query_params["sql"]
                    params = query_params.get("params", ())
                    
                    async with self.connection.execute(sql, params) as cursor:
                        rows = await cursor.fetchall()
                        return [dict(row) for row in rows]
                
                # For table queries
                elif "table" in query_params:
                    table_name = query_params["table"]
                    filters = query_params.get("filters", {})
                    limit = query_params.get("limit")
                    fields = query_params.get("fields", ["*"])
                    
                    # Build query
                    fields_str = ", ".join(fields) if "*" not in fields else "*"
                    sql = f"SELECT {fields_str} FROM {table_name}"
                    
                    # Add WHERE clause
                    params = []
                    if filters:
                        where_clauses = []
                        for key, value in filters.items():
                            where_clauses.append(f"{key} = ?")
                            params.append(value)
                            
                        sql += " WHERE " + " AND ".join(where_clauses)
                    
                    # Add LIMIT
                    if limit:
                        sql += f" LIMIT {limit}"
                        
                    # Execute query
                    async with self.connection.execute(sql, params) as cursor:
                        rows = await cursor.fetchall()
                        return [dict(row) for row in rows]
                        
                return []
                
            elif self.db_type == "asyncpg":
                # For raw SQL queries
                if "sql" in query_params:
                    sql = query_params["sql"]
                    params = query_params.get("params", [])
                    
                    rows = await self.connection.fetch(sql, *params)
                    return [dict(row) for row in rows]
                
                # For table queries
                elif "table" in query_params:
                    table_name = query_params["table"]
                    filters = query_params.get("filters", {})
                    limit = query_params.get("limit")
                    fields = query_params.get("fields", ["*"])
                    
                    # Build query
                    fields_str = ", ".join(fields) if "*" not in fields else "*"
                    sql = f"SELECT {fields_str} FROM {table_name}"
                    
                    # Add WHERE clause
                    params = []
                    if filters:
                        where_clauses = []
                        for i, (key, value) in enumerate(filters.items(), 1):
                            where_clauses.append(f"{key} = ${i}")
                            params.append(value)
                            
                        sql += " WHERE " + " AND ".join(where_clauses)
                    
                    # Add LIMIT
                    if limit:
                        sql += f" LIMIT {limit}"
                        
                    # Execute query
                    rows = await self.connection.fetch(sql, *params)
                    return [dict(row) for row in rows]
                    
                return []
                
            return []
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    async def stream(self, query_params: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream data from the database.
        
        Args:
            query_params: Query parameters
            
        Yields:
            Records one by one
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to data source")
            
        try:
            if self.db_type == "sqlalchemy":
                # SQLAlchemy doesn't have a true streaming API for most databases
                # We'll fetch in chunks
                
                chunk_size = query_params.get("chunk_size", 100)
                offset = 0
                
                while True:
                    # Modify query to include limit and offset
                    chunk_params = query_params.copy()
                    chunk_params["limit"] = chunk_size
                    chunk_params["offset"] = offset
                    
                    # Execute query for this chunk
                    results = await self.query(chunk_params)
                    
                    if not results:
                        break
                        
                    # Yield results
                    for result in results:
                        yield result
                        
                    # Update offset for next chunk
                    offset += chunk_size
                    
                    # If we got fewer results than chunk_size, we're done
                    if len(results) < chunk_size:
                        break
            
            elif self.db_type == "aiosqlite":
                # For raw SQL queries
                if "sql" in query_params:
                    sql = query_params["sql"]
                    params = query_params.get("params", ())
                    
                    async with self.connection.execute(sql, params) as cursor:
                        async for row in cursor:
                            yield dict(row)
                
                # For table queries
                elif "table" in query_params:
                    table_name = query_params["table"]
                    filters = query_params.get("filters", {})
                    fields = query_params.get("fields", ["*"])
                    
                    # Build query
                    fields_str = ", ".join(fields) if "*" not in fields else "*"
                    sql = f"SELECT {fields_str} FROM {table_name}"
                    
                    # Add WHERE clause
                    params = []
                    if filters:
                        where_clauses = []
                        for key, value in filters.items():
                            where_clauses.append(f"{key} = ?")
                            params.append(value)
                            
                        sql += " WHERE " + " AND ".join(where_clauses)
                    
                    # Execute query
                    async with self.connection.execute(sql, params) as cursor:
                        async for row in cursor:
                            yield dict(row)
            
            elif self.db_type == "asyncpg":
                # asyncpg supports true streaming with cursor() method
                
                # For raw SQL queries
                if "sql" in query_params:
                    sql = query_params["sql"]
                    params = query_params.get("params", [])
                    
                    async with self.connection.transaction():
                        async for record in self.connection.cursor(sql, *params):
                            yield dict(record)
                
                # For table queries
                elif "table" in query_params:
                    table_name = query_params["table"]
                    filters = query_params.get("filters", {})
                    fields = query_params.get("fields", ["*"])
                    
                    # Build query
                    fields_str = ", ".join(fields) if "*" not in fields else "*"
                    sql = f"SELECT {fields_str} FROM {table_name}"
                    
                    # Add WHERE clause
                    params = []
                    if filters:
                        where_clauses = []
                        for i, (key, value) in enumerate(filters.items(), 1):
                            where_clauses.append(f"{key} = ${i}")
                            params.append(value)
                            
                        sql += " WHERE " + " AND ".join(where_clauses)
                    
                    # Execute streaming query
                    async with self.connection.transaction():
                        async for record in self.connection.cursor(sql, *params):
                            yield dict(record)
        
        except Exception as e:
            logger.error(f"Error streaming data: {e}")
    
    async def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> bool:
        """
        Insert data into the database.
        
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
            table_name = data[0].get("_table")
            if not table_name:
                raise ValueError("Table name must be specified in '_table' field")
                
            # Remove _table from the data
            for item in data:
                if "_table" in item:
                    del item["_table"]
            
            if self.db_type == "sqlalchemy":
                from sqlalchemy import Table, MetaData, insert
                
                metadata = MetaData()
                table = Table(table_name, metadata, autoload_with=self.engine)
                
                async with self.session_factory() as session:
                    async with session.begin():
                        for item in data:
                            stmt = insert(table).values(**item)
                            await session.execute(stmt)
                    
                return True
                
            elif self.db_type == "aiosqlite":
                for item in data:
                    keys = list(item.keys())
                    placeholders = ", ".join(["?"] * len(keys))
                    columns = ", ".join(keys)
                    
                    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    values = [item[key] for key in keys]
                    
                    await self.connection.execute(sql, values)
                
                await self.connection.commit()
                return True
                
            elif self.db_type == "asyncpg":
                async with self.connection.transaction():
                    for item in data:
                        keys = list(item.keys())
                        placeholders = ", ".join([f"${i+1}" for i in range(len(keys))])
                        columns = ", ".join(keys)
                        
                        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                        values = [item[key] for key in keys]
                        
                        await self.connection.execute(sql, *values)
                
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema of the database.
        
        Returns:
            Dict describing the database schema
        """
        schema = {
            "type": "database",
            "db_type": self.db_type,
            "tables": {},
        }
        
        # This is a simplified implementation
        # A real implementation would query the database metadata
        
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
            "update": True,
            "delete": True,
            "transactions": True,
        }
        
        # asyncpg doesn't support some features
        if self.db_type == "aiosqlite":
            supported_features.update({
                "transactions": True,
            })
            
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
            "transactional": True,
            "supports_concurrent_access": True,
            "supported_db_types": ["sqlalchemy", "aiosqlite", "asyncpg"],
        }
        
        return capabilities