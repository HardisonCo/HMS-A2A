"""
Audit Logging System for federation activities.

This module provides comprehensive audit logging capabilities,
ensuring that all federation-related activities are properly tracked
for compliance, security, and operational purposes.
"""

import logging
import uuid
import json
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
import os
import threading
from concurrent.futures import ThreadPoolExecutor

from federation.models import AuditEvent
from federation.exceptions import AuditError

logger = logging.getLogger(__name__)


class AuditLogHandler:
    """Base class for audit log handlers."""
    
    def __init__(self, manager):
        """Initialize with audit manager reference."""
        self._manager = manager
    
    def log_event(self, event: AuditEvent) -> None:
        """
        Log an audit event.
        
        Args:
            event: The audit event to log
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement log_event()")
    
    def query_events(
        self, 
        filters: Dict[str, Any] = None, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[AuditEvent]:
        """
        Query audit events.
        
        Args:
            filters: Optional filters to apply
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            
        Returns:
            List of matching audit events
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement query_events()")


class FileAuditLogHandler(AuditLogHandler):
    """Audit log handler that stores events in a file."""
    
    def __init__(self, manager, file_path: Optional[str] = None):
        """
        Initialize file-based audit log handler.
        
        Args:
            manager: Audit manager reference
            file_path: Optional path to audit log file
        """
        super().__init__(manager)
        self._file_path = file_path or "federation_audit.log"
        self._file_lock = threading.Lock()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self._file_path)), exist_ok=True)
    
    def log_event(self, event: AuditEvent) -> None:
        """
        Log an audit event to file.
        
        Args:
            event: The audit event to log
        """
        with self._file_lock:
            try:
                with open(self._file_path, "a") as f:
                    f.write(json.dumps(event.to_dict()) + "\n")
            except Exception as e:
                logger.error(f"Failed to write audit event to file: {str(e)}")
                raise AuditError(f"Failed to write audit event: {str(e)}")
    
    def query_events(
        self, 
        filters: Dict[str, Any] = None, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[AuditEvent]:
        """
        Query audit events from file.
        
        Args:
            filters: Optional filters to apply
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            
        Returns:
            List of matching audit events
        """
        events = []
        offset = offset or 0
        
        try:
            with open(self._file_path, "r") as f:
                for line in f:
                    try:
                        event_dict = json.loads(line.strip())
                        event = AuditEvent(**event_dict)
                        
                        # Apply time filters
                        if start_time and event.timestamp < start_time:
                            continue
                        if end_time and event.timestamp > end_time:
                            continue
                        
                        # Apply other filters
                        if filters:
                            match = True
                            for key, value in filters.items():
                                if key in event_dict and event_dict[key] != value:
                                    match = False
                                    break
                            if not match:
                                continue
                        
                        events.append(event)
                    except Exception as e:
                        logger.warning(f"Failed to parse audit event: {str(e)}")
        except FileNotFoundError:
            # No audit log file yet
            return []
        except Exception as e:
            logger.error(f"Failed to read audit events: {str(e)}")
            raise AuditError(f"Failed to read audit events: {str(e)}")
        
        # Apply pagination
        if offset > 0:
            events = events[offset:]
        if limit is not None:
            events = events[:limit]
        
        return events


class DatabaseAuditLogHandler(AuditLogHandler):
    """Audit log handler that stores events in a database."""
    
    def __init__(self, manager, connection_string: Optional[str] = None):
        """
        Initialize database-based audit log handler.
        
        Args:
            manager: Audit manager reference
            connection_string: Optional database connection string
        """
        super().__init__(manager)
        self._connection_string = connection_string
        # In a real implementation, this would initialize a database connection
        logger.info("Database audit log handler initialized as placeholder")
    
    def log_event(self, event: AuditEvent) -> None:
        """
        Log an audit event to database.
        
        Args:
            event: The audit event to log
        """
        # In a real implementation, this would store the event in a database
        logger.info(f"[DB] Audit event: {event.event_type} ({event.event_id})")
    
    def query_events(
        self, 
        filters: Dict[str, Any] = None, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[AuditEvent]:
        """
        Query audit events from database.
        
        Args:
            filters: Optional filters to apply
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            
        Returns:
            List of matching audit events
        """
        # In a real implementation, this would query the database
        return []


class AuditManager:
    """
    Manager for federation audit logging.
    """
    
    def __init__(self, federation_manager):
        """Initialize with federation manager reference."""
        self._federation = federation_manager
        self._handlers = []
        self._thread_pool = ThreadPoolExecutor(max_workers=2)
        
        # Initialize default handlers based on configuration
        self._init_handlers()
    
    def _init_handlers(self) -> None:
        """Initialize audit log handlers based on configuration."""
        config = self._federation.config
        
        # Get audit configuration
        audit_config = config.get("audit", {})
        
        # Initialize file handler if configured
        if audit_config.get("file", {}).get("enabled", True):
            file_path = audit_config.get("file", {}).get("path")
            self.add_handler(FileAuditLogHandler(self, file_path))
        
        # Initialize database handler if configured
        if audit_config.get("database", {}).get("enabled", False):
            connection_string = audit_config.get("database", {}).get("connection_string")
            self.add_handler(DatabaseAuditLogHandler(self, connection_string))
    
    def add_handler(self, handler: AuditLogHandler) -> None:
        """
        Add an audit log handler.
        
        Args:
            handler: The handler to add
        """
        self._handlers.append(handler)
    
    def log_event(
        self,
        event_type: str,
        details: Dict[str, Any] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            details: Additional event details
            user_id: ID of user who performed the action
            request_id: Associated request ID
            ip_address: Client IP address
            
        Returns:
            Created AuditEvent
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            agency_id=self._federation.local_agency_id,
            user_id=user_id,
            details=details or {},
            request_id=request_id,
            ip_address=ip_address
        )
        
        # Log to registered handlers
        self._log_to_handlers(event)
        
        return event
    
    def _log_to_handlers(self, event: AuditEvent) -> None:
        """
        Log event to all registered handlers.
        
        Args:
            event: Event to log
        """
        # If no handlers, log warning and return
        if not self._handlers:
            logger.warning("No audit log handlers configured, audit event not logged")
            return
        
        # Submit logging to thread pool to avoid blocking
        for handler in self._handlers:
            self._thread_pool.submit(self._log_to_handler, handler, event)
    
    def _log_to_handler(self, handler: AuditLogHandler, event: AuditEvent) -> None:
        """
        Log event to a specific handler.
        
        Args:
            handler: Handler to use
            event: Event to log
        """
        try:
            handler.log_event(event)
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
    
    def query_events(
        self, 
        filters: Dict[str, Any] = None, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        handler_index: Optional[int] = None
    ) -> List[AuditEvent]:
        """
        Query audit events.
        
        Args:
            filters: Optional filters to apply
            start_time: Optional start time for time range
            end_time: Optional end time for time range
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            handler_index: Optional index of specific handler to query
            
        Returns:
            List of matching audit events
        """
        if handler_index is not None:
            if 0 <= handler_index < len(self._handlers):
                return self._handlers[handler_index].query_events(
                    filters, start_time, end_time, limit, offset
                )
            else:
                raise AuditError(f"Invalid handler index: {handler_index}")
        
        # Query the first handler by default
        if self._handlers:
            return self._handlers[0].query_events(
                filters, start_time, end_time, limit, offset
            )
        
        return []