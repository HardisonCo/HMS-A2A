"""
Schema Registry System for federation framework.

This module provides standardized data schema management 
to ensure consistent data formatting across federated agencies.
"""

import logging
import uuid
import json
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
import os
import re

from federation.models import DatasetSchema, SecurityClassification
from federation.exceptions import SchemaError

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Error raised when data doesn't conform to a schema."""
    pass


class SchemaRegistry:
    """
    Registry for federation data schemas.
    
    This class manages standardized schemas for all datasets
    in the federation to ensure consistent data structures.
    """
    
    def __init__(self, federation_manager):
        """Initialize with federation manager reference."""
        self._federation = federation_manager
        self._schemas = {}  # name:version -> DatasetSchema
        self._latest_versions = {}  # name -> version
        
        # Initialize from configuration
        self._schema_dir = self._federation.config.get("schema", {}).get("directory")
        if self._schema_dir:
            self._load_schemas()
    
    def _load_schemas(self) -> None:
        """Load schemas from schema directory."""
        if not self._schema_dir:
            return
        
        try:
            os.makedirs(self._schema_dir, exist_ok=True)
            for filename in os.listdir(self._schema_dir):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(self._schema_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        schema_data = json.load(f)
                    
                    # Create schema object
                    schema = DatasetSchema(
                        name=schema_data.get("name"),
                        version=schema_data.get("version"),
                        fields=schema_data.get("fields", {}),
                        security_classification=schema_data.get("security_classification"),
                        description=schema_data.get("description"),
                        owner_agency=schema_data.get("owner_agency")
                    )
                    
                    # Register schema
                    self.register_schema(schema)
                    
                except Exception as e:
                    logger.error(f"Failed to load schema from {file_path}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Failed to load schemas: {str(e)}")
    
    def register_schema(self, schema: DatasetSchema) -> None:
        """
        Register a new schema or version.
        
        Args:
            schema: Schema to register
            
        Raises:
            SchemaError: If schema is invalid
        """
        if not schema.name or not schema.version:
            raise SchemaError("Schema must have name and version")
        
        key = f"{schema.name}:{schema.version}"
        
        # Store schema
        self._schemas[key] = schema
        
        # Update latest version if newer
        current_latest = self._latest_versions.get(schema.name)
        if not current_latest or self._compare_versions(schema.version, current_latest) > 0:
            self._latest_versions[schema.name] = schema.version
        
        # Save to file if directory is configured
        if self._schema_dir:
            self._save_schema(schema)
        
        logger.info(f"Registered schema {schema.name} version {schema.version}")
    
    def _save_schema(self, schema: DatasetSchema) -> None:
        """
        Save schema to file.
        
        Args:
            schema: Schema to save
        """
        if not self._schema_dir:
            return
        
        os.makedirs(self._schema_dir, exist_ok=True)
        file_path = os.path.join(self._schema_dir, f"{schema.name}_{schema.version}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(schema.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save schema to {file_path}: {str(e)}")
    
    def get_schema(
        self, 
        name: str, 
        version: Optional[str] = None
    ) -> Optional[DatasetSchema]:
        """
        Get a schema by name and version.
        
        Args:
            name: Schema name
            version: Optional schema version (uses latest if not specified)
            
        Returns:
            DatasetSchema if found, None otherwise
        """
        if not version:
            version = self._latest_versions.get(name)
            if not version:
                return None
        
        key = f"{name}:{version}"
        return self._schemas.get(key)
    
    def list_schemas(self) -> List[DatasetSchema]:
        """
        List all registered schemas.
        
        Returns:
            List of all registered schemas
        """
        return list(self._schemas.values())
    
    def list_versions(self, name: str) -> List[str]:
        """
        List all versions of a schema.
        
        Args:
            name: Schema name
            
        Returns:
            List of version strings
        """
        versions = []
        prefix = f"{name}:"
        for key in self._schemas.keys():
            if key.startswith(prefix):
                version = key[len(prefix):]
                versions.append(version)
        
        # Sort versions
        versions.sort(key=lambda v: self._version_tuple(v))
        return versions
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.
        
        Args:
            version1: First version
            version2: Second version
            
        Returns:
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        v1_tuple = self._version_tuple(version1)
        v2_tuple = self._version_tuple(version2)
        
        if v1_tuple < v2_tuple:
            return -1
        elif v1_tuple > v2_tuple:
            return 1
        else:
            return 0
    
    def _version_tuple(self, version: str) -> tuple:
        """
        Convert version string to comparable tuple.
        
        Args:
            version: Version string
            
        Returns:
            Tuple of version components
        """
        # Handle semantic versioning (x.y.z)
        if re.match(r'^\d+\.\d+\.\d+$', version):
            return tuple(map(int, version.split('.')))
        
        # Handle simple numeric versions
        if version.isdigit():
            return (int(version),)
        
        # Default case - convert to string tuple
        return (version,)
    
    def validate_data(
        self, 
        data: Dict[str, Any], 
        schema_name: str,
        version: Optional[str] = None
    ) -> None:
        """
        Validate data against a schema.
        
        Args:
            data: Data to validate
            schema_name: Schema name
            version: Optional schema version (uses latest if not specified)
            
        Raises:
            SchemaValidationError: If data doesn't conform to schema
            SchemaError: If schema not found
        """
        schema = self.get_schema(schema_name, version)
        if not schema:
            raise SchemaError(f"Schema not found: {schema_name}" + (f" version {version}" if version else ""))
        
        errors = []
        
        # Check each field
        for field_name, field_def in schema.fields.items():
            # Check required fields
            if field_def.get("required", False) and field_name not in data:
                errors.append(f"Required field '{field_name}' is missing")
                continue
            
            # Skip validation for missing optional fields
            if field_name not in data:
                continue
            
            value = data[field_name]
            
            # Check type
            if "type" in field_def:
                type_name = field_def["type"]
                if not self._check_type(value, type_name):
                    errors.append(f"Field '{field_name}' has wrong type (expected {type_name})")
            
            # Check enum values
            if "enum" in field_def and value not in field_def["enum"]:
                errors.append(f"Field '{field_name}' has invalid value (expected one of {field_def['enum']})")
            
            # Check pattern
            if "pattern" in field_def and isinstance(value, str):
                pattern = field_def["pattern"]
                if not re.match(pattern, value):
                    errors.append(f"Field '{field_name}' does not match pattern '{pattern}'")
            
            # Check min/max for numeric values
            if isinstance(value, (int, float)):
                if "minimum" in field_def and value < field_def["minimum"]:
                    errors.append(f"Field '{field_name}' is below minimum value {field_def['minimum']}")
                
                if "maximum" in field_def and value > field_def["maximum"]:
                    errors.append(f"Field '{field_name}' exceeds maximum value {field_def['maximum']}")
            
            # Check min/max length for strings
            if isinstance(value, str):
                if "minLength" in field_def and len(value) < field_def["minLength"]:
                    errors.append(f"Field '{field_name}' is below minimum length {field_def['minLength']}")
                
                if "maxLength" in field_def and len(value) > field_def["maxLength"]:
                    errors.append(f"Field '{field_name}' exceeds maximum length {field_def['maxLength']}")
        
        # Check for unknown fields
        if field_def.get("additionalProperties", True) == False:
            for field_name in data.keys():
                if field_name not in schema.fields:
                    errors.append(f"Unknown field '{field_name}'")
        
        # Raise validation error if there are any issues
        if errors:
            error_message = "\n".join(errors)
            raise SchemaValidationError(f"Schema validation failed for {schema_name}: {error_message}")
    
    def _check_type(self, value: Any, type_name: str) -> bool:
        """
        Check if a value matches the specified type.
        
        Args:
            value: Value to check
            type_name: Type name
            
        Returns:
            True if value matches type, False otherwise
        """
        if type_name == "string":
            return isinstance(value, str)
        elif type_name == "number":
            return isinstance(value, (int, float))
        elif type_name == "integer":
            return isinstance(value, int)
        elif type_name == "boolean":
            return isinstance(value, bool)
        elif type_name == "array":
            return isinstance(value, list)
        elif type_name == "object":
            return isinstance(value, dict)
        elif type_name == "null":
            return value is None
        
        # Handle union types (e.g., "string|number")
        if "|" in type_name:
            types = type_name.split("|")
            return any(self._check_type(value, t) for t in types)
        
        return True  # Unknown type - pass by default
    
    def transform_data(
        self, 
        data: Dict[str, Any],
        source_schema_name: str,
        target_schema_name: str,
        source_version: Optional[str] = None,
        target_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transform data from one schema to another.
        
        Args:
            data: Source data
            source_schema_name: Source schema name
            target_schema_name: Target schema name
            source_version: Optional source schema version
            target_version: Optional target schema version
            
        Returns:
            Transformed data
            
        Raises:
            SchemaError: If transformation is not possible
        """
        # Get schemas
        source_schema = self.get_schema(source_schema_name, source_version)
        if not source_schema:
            raise SchemaError(f"Source schema not found: {source_schema_name}")
        
        target_schema = self.get_schema(target_schema_name, target_version)
        if not target_schema:
            raise SchemaError(f"Target schema not found: {target_schema_name}")
        
        # Start with empty result
        result = {}
        
        # Process each field in target schema
        for field_name, field_def in target_schema.fields.items():
            # Skip if no mapping defined and not in source data
            if field_name not in source_schema.fields and field_name not in data:
                # Use default value if specified
                if "default" in field_def:
                    result[field_name] = field_def["default"]
                continue
            
            # Copy field directly if it exists in source data and has compatible type
            if field_name in data:
                source_value = data[field_name]
                
                # Check type compatibility
                if "type" in field_def and not self._check_type(source_value, field_def["type"]):
                    # Try simple type conversion
                    converted_value = self._convert_type(source_value, field_def["type"])
                    if converted_value is not None:
                        result[field_name] = converted_value
                    elif "default" in field_def:
                        result[field_name] = field_def["default"]
                else:
                    result[field_name] = source_value
            elif "mapping" in field_def:
                # Apply field mapping
                mapping = field_def["mapping"]
                if "source_field" in mapping:
                    source_field = mapping["source_field"]
                    if source_field in data:
                        source_value = data[source_field]
                        
                        # Apply transformation function if specified
                        if "transform" in mapping:
                            # In a real implementation, this would support more complex transformations
                            if mapping["transform"] == "uppercase" and isinstance(source_value, str):
                                source_value = source_value.upper()
                            elif mapping["transform"] == "lowercase" and isinstance(source_value, str):
                                source_value = source_value.lower()
                            elif mapping["transform"] == "toString":
                                source_value = str(source_value)
                        
                        result[field_name] = source_value
            elif "default" in field_def:
                # Use default value
                result[field_name] = field_def["default"]
        
        return result
    
    def _convert_type(self, value: Any, target_type: str) -> Any:
        """
        Attempt to convert a value to the target type.
        
        Args:
            value: Value to convert
            target_type: Target type
            
        Returns:
            Converted value, or None if conversion is not possible
        """
        try:
            if target_type == "string":
                return str(value)
            elif target_type == "number":
                return float(value)
            elif target_type == "integer":
                return int(value)
            elif target_type == "boolean":
                if isinstance(value, str):
                    return value.lower() in ("true", "yes", "1")
                return bool(value)
            elif target_type == "array" and not isinstance(value, list):
                if isinstance(value, (str, bytes, bytearray)):
                    return [value]
                if hasattr(value, "__iter__"):
                    return list(value)
                return [value]
        except (ValueError, TypeError):
            pass
        
        return None