"""
Federation API for exposing federation services.

This module provides a RESTful API for federation services using FastAPI.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, Header, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from federation.manager import FederationManager
from federation.models import (
    Agency, FederationPolicy, AccessRule, DatasetSchema, 
    SecurityClassification, TrustLevel, SyncMode
)
from federation.exceptions import (
    FederationError, AuthorizationError, SchemaError, 
    ValidationError, GovernanceError
)

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses

class AgencyCreate(BaseModel):
    """Model for creating a new agency."""
    id: str
    endpoint: str
    trust_level: str
    allowed_datasets: List[str] = []
    contact_email: Optional[str] = None
    metadata: Dict[str, Any] = {}


class AgencyResponse(BaseModel):
    """Model for agency response."""
    id: str
    endpoint: str
    trust_level: str
    allowed_datasets: List[str]
    contact_email: Optional[str] = None
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str


class QueryRequest(BaseModel):
    """Model for federated query request."""
    dataset: str
    query: Dict[str, Any] = {}
    target_agencies: List[str] = []
    timeout: float = 30.0
    max_results: Optional[int] = None
    options: Dict[str, Any] = {}


class SyncJobCreate(BaseModel):
    """Model for creating a synchronization job."""
    target_agency: str
    datasets: List[str]
    sync_mode: str = "INCREMENTAL"
    metadata: Dict[str, Any] = {}


class SyncJobResponse(BaseModel):
    """Model for synchronization job response."""
    job_id: str
    source_agency: str
    target_agency: str
    datasets: List[str]
    sync_mode: str
    status: str
    progress: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any]


class PolicyCreate(BaseModel):
    """Model for creating a federation policy."""
    dataset: str
    security_classification: str
    rules: List[Dict[str, Any]] = []
    retention_period: Optional[str] = None
    data_sovereignty: Optional[List[str]] = None


class PolicyResponse(BaseModel):
    """Model for federation policy response."""
    dataset: str
    security_classification: str
    rules: List[Dict[str, Any]]
    retention_period: Optional[str] = None
    data_sovereignty: Optional[List[str]] = None
    created_at: str
    updated_at: str


class SchemaCreate(BaseModel):
    """Model for creating a dataset schema."""
    name: str
    version: str
    fields: Dict[str, Dict[str, Any]]
    security_classification: str
    description: Optional[str] = None
    owner_agency: Optional[str] = None


class SchemaResponse(BaseModel):
    """Model for dataset schema response."""
    name: str
    version: str
    fields: Dict[str, Dict[str, Any]]
    security_classification: str
    description: Optional[str] = None
    owner_agency: Optional[str] = None
    created_at: str
    updated_at: str


class ErrorResponse(BaseModel):
    """Model for error responses."""
    status: str = "error"
    message: str
    error_type: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class FederationAPI:
    """
    API for federation services.
    
    This class provides a FastAPI application for exposing federation services.
    """
    
    def __init__(self, federation_manager: FederationManager):
        """Initialize with federation manager reference."""
        self.federation = federation_manager
        self.app = FastAPI(title="Federation API", description="API for federation services")
        self.security = HTTPBearer()
        
        # Apply middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add exception handlers
        self.app.add_exception_handler(FederationError, self.federation_error_handler)
        self.app.add_exception_handler(Exception, self.general_error_handler)
        
        # Add routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up API routes."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/status")
        async def status():
            """Federation status endpoint."""
            return {
                "status": "online",
                "local_agency": self.federation.local_agency_id,
                "partner_count": len(self.federation.list_partners()),
                "gateway": {
                    "host": self.federation.config.get("gateway", {}).get("host", "0.0.0.0"),
                    "port": self.federation.config.get("gateway", {}).get("port", 8585)
                }
            }
        
        # Agency management endpoints
        
        @self.app.get("/agencies", response_model=List[AgencyResponse])
        async def list_agencies(credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """List all partner agencies."""
            self._validate_token(credentials.credentials)
            agencies = self.federation.list_partners()
            return [agency.to_dict() for agency in agencies]
        
        @self.app.get("/agencies/{agency_id}", response_model=AgencyResponse)
        async def get_agency(agency_id: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Get a specific partner agency."""
            self._validate_token(credentials.credentials)
            agency = self.federation.get_partner(agency_id)
            if not agency:
                raise HTTPException(status_code=404, detail="Agency not found")
            return agency.to_dict()
        
        @self.app.post("/agencies", response_model=AgencyResponse, status_code=201)
        async def create_agency(
            agency: AgencyCreate, 
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Register a new partner agency."""
            self._validate_token(credentials.credentials)
            try:
                new_agency = self.federation.register_partner(
                    agency_id=agency.id,
                    endpoint=agency.endpoint,
                    trust_level=agency.trust_level,
                    allowed_datasets=agency.allowed_datasets,
                    contact_email=agency.contact_email,
                    metadata=agency.metadata
                )
                return new_agency.to_dict()
            except FederationError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Query endpoints
        
        @self.app.post("/query", status_code=200)
        async def execute_query(
            query: QueryRequest, 
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Execute a federated query."""
            self._validate_token(credentials.credentials)
            try:
                query_spec = {
                    "dataset": query.dataset,
                    "query": query.query,
                    "target_agencies": query.target_agencies,
                    "timeout": query.timeout,
                    "max_results": query.max_results,
                    "options": query.options
                }
                
                results = self.federation.query.execute_query(query_spec)
                return results
            except FederationError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Synchronization endpoints
        
        @self.app.post("/sync/jobs", response_model=SyncJobResponse, status_code=201)
        async def create_sync_job(
            job: SyncJobCreate, 
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Create a new synchronization job."""
            self._validate_token(credentials.credentials)
            try:
                sync_job = self.federation.sync.create_job(
                    target_agency=job.target_agency,
                    datasets=job.datasets,
                    sync_mode=job.sync_mode,
                    metadata=job.metadata
                )
                
                return sync_job.to_dict()
            except FederationError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/sync/jobs", response_model=List[SyncJobResponse])
        async def list_sync_jobs(
            status: Optional[str] = None,
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """List synchronization jobs."""
            self._validate_token(credentials.credentials)
            jobs = self.federation.sync.list_jobs(status)
            return [job.to_dict() for job in jobs]
        
        @self.app.get("/sync/jobs/{job_id}", response_model=SyncJobResponse)
        async def get_sync_job(
            job_id: str, 
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Get a specific synchronization job."""
            self._validate_token(credentials.credentials)
            job = self.federation.sync.get_job(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            return job.to_dict()
        
        @self.app.post("/sync/jobs/{job_id}/execute", response_model=SyncJobResponse)
        async def execute_sync_job(
            job_id: str, 
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Execute a synchronization job."""
            self._validate_token(credentials.credentials)
            try:
                job = self.federation.sync.execute_job(job_id)
                return job.to_dict()
            except FederationError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/sync/jobs/{job_id}/cancel", response_model=Dict[str, Any])
        async def cancel_sync_job(
            job_id: str, 
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Cancel a synchronization job."""
            self._validate_token(credentials.credentials)
            cancelled = self.federation.sync.cancel_job(job_id)
            if not cancelled:
                raise HTTPException(status_code=400, detail="Job not found or not running")
            return {"status": "cancelled", "job_id": job_id}
        
        # Policy endpoints
        
        @self.app.get("/policies", response_model=List[PolicyResponse])
        async def list_policies(credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """List all federation policies."""
            self._validate_token(credentials.credentials)
            policies = self.federation.governance.list_policies()
            return [policy.to_dict() for policy in policies]
        
        @self.app.get("/policies/{dataset}", response_model=PolicyResponse)
        async def get_policy(
            dataset: str, 
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Get policy for a specific dataset."""
            self._validate_token(credentials.credentials)
            policy = self.federation.governance.get_policy(dataset)
            if not policy:
                raise HTTPException(status_code=404, detail="Policy not found")
            return policy.to_dict()
        
        @self.app.post("/policies", response_model=PolicyResponse, status_code=201)
        async def create_policy(
            policy_data: PolicyCreate, 
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Create or update a federation policy."""
            self._validate_token(credentials.credentials)
            try:
                # Convert rules from dict to objects
                rules = []
                for rule_data in policy_data.rules:
                    rules.append(AccessRule(**rule_data))
                
                # Create policy object
                policy = FederationPolicy(
                    dataset=policy_data.dataset,
                    security_classification=policy_data.security_classification,
                    rules=rules,
                    retention_period=policy_data.retention_period,
                    data_sovereignty=policy_data.data_sovereignty
                )
                
                # Apply policy
                self.federation.governance.apply_policy(policy.dataset, policy)
                
                return policy.to_dict()
            except GovernanceError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.delete("/policies/{dataset}", status_code=204)
        async def delete_policy(
            dataset: str, 
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Delete a federation policy."""
            self._validate_token(credentials.credentials)
            deleted = self.federation.governance.delete_policy(dataset)
            if not deleted:
                raise HTTPException(status_code=404, detail="Policy not found")
            return {"status": "deleted"}
        
        # Schema endpoints
        
        @self.app.get("/schemas", response_model=List[SchemaResponse])
        async def list_schemas(credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """List all dataset schemas."""
            self._validate_token(credentials.credentials)
            schemas = self.federation.schema_registry.list_schemas()
            return [schema.to_dict() for schema in schemas]
        
        @self.app.get("/schemas/{name}", response_model=SchemaResponse)
        async def get_schema(
            name: str, 
            version: Optional[str] = None,
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Get a specific dataset schema."""
            self._validate_token(credentials.credentials)
            schema = self.federation.schema_registry.get_schema(name, version)
            if not schema:
                raise HTTPException(status_code=404, detail="Schema not found")
            return schema.to_dict()
        
        @self.app.post("/schemas", response_model=SchemaResponse, status_code=201)
        async def create_schema(
            schema_data: SchemaCreate, 
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Register a new dataset schema."""
            self._validate_token(credentials.credentials)
            try:
                # Create schema object
                schema = DatasetSchema(
                    name=schema_data.name,
                    version=schema_data.version,
                    fields=schema_data.fields,
                    security_classification=schema_data.security_classification,
                    description=schema_data.description,
                    owner_agency=schema_data.owner_agency
                )
                
                # Register schema
                self.federation.schema_registry.register_schema(schema)
                
                return schema.to_dict()
            except SchemaError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/schemas/{name}/validate", status_code=200)
        async def validate_data(
            name: str,
            data: Dict[str, Any],
            version: Optional[str] = None,
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Validate data against a schema."""
            self._validate_token(credentials.credentials)
            try:
                self.federation.schema_registry.validate_data(data, name, version)
                return {"status": "valid"}
            except SchemaError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except ValidationError as e:
                raise HTTPException(status_code=400, detail=str(e))
    
    def _validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate authentication token.
        
        Args:
            token: Token to validate
            
        Returns:
            Token claims if valid
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            claims = self.federation.security.validate_token(token)
            return claims
        except AuthorizationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    async def federation_error_handler(self, request: Request, exc: FederationError):
        """Handler for federation-specific errors."""
        error_type = exc.__class__.__name__
        status_code = 400
        
        if isinstance(exc, AuthorizationError):
            status_code = 403
        elif isinstance(exc, SchemaError) or isinstance(exc, NotFoundError):
            status_code = 404
        
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                message=str(exc),
                error_type=error_type
            ).dict()
        )
    
    async def general_error_handler(self, request: Request, exc: Exception):
        """Handler for general exceptions."""
        logger.exception("Unhandled exception in API request")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error",
                error_type=exc.__class__.__name__
            ).dict()
        )
    
    def start(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Start the API server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


# Standalone JSON response class for error handling
from fastapi.responses import JSONResponse