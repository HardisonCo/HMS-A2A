"""
Form models for the APHIS Agency Implementation.
Defines data models for forms, submissions, and related entities.
"""
from typing import Dict, Any, Optional, List, Union
from datetime import date, datetime
from enum import Enum

from .base import BaseModel


class FieldType(str, Enum):
    """Types of form fields"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    MULTISELECT = "multiselect"
    FILE = "file"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    HIDDEN = "hidden"
    SECTION = "section"
    CUSTOM = "custom"


class ValidationRule(str, Enum):
    """Common validation rules for form fields"""
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    PATTERN = "pattern"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    DATE_RANGE = "date_range"
    CUSTOM = "custom"


class FormStatus(str, Enum):
    """Status of a form"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DISABLED = "disabled"


class SubmissionStatus(str, Enum):
    """Status of a form submission"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    WITHDRAWN = "withdrawn"


class FormField(BaseModel):
    """A field in a form"""
    
    def __init__(
        self,
        name: str,
        label: str,
        field_type: Union[FieldType, str],
        order: int,
        required: bool = False,
        default_value: Optional[Any] = None,
        placeholder: Optional[str] = None,
        help_text: Optional[str] = None,
        options: Optional[List[Dict[str, Any]]] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        conditional_display: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a form field"""
        # Convert string enum to Enum value if needed
        if isinstance(field_type, str):
            field_type = FieldType(field_type)
        
        super().__init__(
            name=name,
            label=label,
            field_type=field_type,
            order=order,
            required=required,
            default_value=default_value,
            placeholder=placeholder,
            help_text=help_text,
            options=options or [],
            validation_rules=validation_rules or {},
            conditional_display=conditional_display or {},
            metadata=metadata or {},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert enum values to strings
        if 'field_type' in result and isinstance(result['field_type'], Enum):
            result['field_type'] = result['field_type'].value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FormField':
        """Create from dictionary representation"""
        return cls(**data)
    
    def add_validation_rule(self, rule: Union[ValidationRule, str], value: Any) -> None:
        """Add a validation rule to the field"""
        if isinstance(rule, str):
            rule = ValidationRule(rule)
            
        if not hasattr(self, 'validation_rules'):
            self.validation_rules = {}
            
        self.validation_rules[rule.value] = value
        self.updated_at = datetime.now().isoformat()


class Form(BaseModel):
    """A form for collecting data"""
    
    def __init__(
        self,
        title: str,
        description: str,
        fields: List[Union[FormField, Dict[str, Any]]],
        agency_id: str,
        status: Union[FormStatus, str] = FormStatus.DRAFT,
        version: str = "1.0",
        expires_at: Optional[Union[datetime, str]] = None,
        created_by: Optional[str] = None,
        program_id: Optional[str] = None,
        submission_limit: Optional[int] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a form"""
        # Convert field dicts to FormField if needed
        processed_fields = []
        for field in fields:
            if isinstance(field, dict):
                processed_fields.append(FormField.from_dict(field))
            else:
                processed_fields.append(field)
        
        # Convert string enum to Enum value if needed
        if isinstance(status, str):
            status = FormStatus(status)
        
        # Convert date string to datetime if needed
        if isinstance(expires_at, str) and expires_at:
            expires_at = datetime.fromisoformat(expires_at)
        
        super().__init__(
            title=title,
            description=description,
            fields=processed_fields,
            agency_id=agency_id,
            status=status,
            version=version,
            expires_at=expires_at,
            created_by=created_by,
            program_id=program_id,
            submission_limit=submission_limit,
            tags=tags or [],
            metadata=metadata or {},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert complex objects to dictionaries
        if 'fields' in result:
            result['fields'] = [
                field.to_dict() if isinstance(field, FormField) else field 
                for field in result['fields']
            ]
        
        # Convert enum values to strings
        if 'status' in result and isinstance(result['status'], Enum):
            result['status'] = result['status'].value
        
        # Convert datetime to string
        if 'expires_at' in result and isinstance(result['expires_at'], datetime):
            result['expires_at'] = result['expires_at'].isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Form':
        """Create from dictionary representation"""
        return cls(**data)
    
    def add_field(self, field: Union[FormField, Dict[str, Any]]) -> None:
        """Add a field to the form"""
        if isinstance(field, dict):
            field = FormField.from_dict(field)
            
        if not hasattr(self, 'fields'):
            self.fields = []
            
        # Set order if not provided
        if not hasattr(field, 'order') or field.order is None:
            field.order = len(self.fields)
            
        self.fields.append(field)
        self.updated_at = datetime.now().isoformat()
    
    def update_status(self, new_status: Union[FormStatus, str]) -> None:
        """Update the form status"""
        if isinstance(new_status, str):
            new_status = FormStatus(new_status)
            
        self.status = new_status
        self.updated_at = datetime.now().isoformat()


class FormSubmission(BaseModel):
    """A submission of a form"""
    
    def __init__(
        self,
        form_id: str,
        data: Dict[str, Any],
        submitted_by: Optional[str] = None,
        status: Union[SubmissionStatus, str] = SubmissionStatus.SUBMITTED,
        submitted_at: Optional[Union[datetime, str]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        review_notes: Optional[Dict[str, Any]] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a form submission"""
        # Convert string enum to Enum value if needed
        if isinstance(status, str):
            status = SubmissionStatus(status)
        
        # Set submitted_at if not provided
        if not submitted_at:
            submitted_at = datetime.now().isoformat()
        elif isinstance(submitted_at, datetime):
            submitted_at = submitted_at.isoformat()
        
        super().__init__(
            form_id=form_id,
            data=data,
            submitted_by=submitted_by,
            status=status,
            submitted_at=submitted_at,
            ip_address=ip_address,
            user_agent=user_agent,
            review_notes=review_notes or {},
            files=files or [],
            metadata=metadata or {},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert enum values to strings
        if 'status' in result and isinstance(result['status'], Enum):
            result['status'] = result['status'].value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FormSubmission':
        """Create from dictionary representation"""
        return cls(**data)
    
    def update_status(self, new_status: Union[SubmissionStatus, str], review_note: Optional[str] = None) -> None:
        """Update the submission status"""
        if isinstance(new_status, str):
            new_status = SubmissionStatus(new_status)
            
        self.status = new_status
        
        if review_note:
            if not hasattr(self, 'review_notes'):
                self.review_notes = {}
                
            status_update = {
                'status': new_status.value,
                'timestamp': datetime.now().isoformat(),
                'note': review_note
            }
            
            if 'history' not in self.review_notes:
                self.review_notes['history'] = []
                
            self.review_notes['history'].append(status_update)
            self.review_notes['latest'] = status_update
            
        self.updated_at = datetime.now().isoformat()
    
    def add_file(self, field_name: str, file_name: str, file_type: str, url: str, size: int) -> None:
        """Add a file to the submission"""
        if not hasattr(self, 'files'):
            self.files = []
            
        file_info = {
            'field_name': field_name,
            'file_name': file_name,
            'file_type': file_type,
            'url': url,
            'size': size,
            'uploaded_at': datetime.now().isoformat()
        }
        
        self.files.append(file_info)
        self.updated_at = datetime.now().isoformat()