# API Framework for Agency Implementation

This standardized API framework provides a consistent structure for implementing APIs across all agency systems. It enforces common patterns and interfaces to ensure maintainability, security, and performance.

## Components

### Application Factory

Create consistent FastAPI applications with standardized configuration:

```python
from agency_implementation.foundation.api_framework import create_app

app = create_app(
    title="My Agency API",
    description="API for agency data access",
    version="1.0.0",
    cors_origins=["https://agency.example.gov"],
    logger_name="my_agency_api"
)
```

### Controllers

Base controller with standard CRUD operations:

```python
from agency_implementation.foundation.api_framework import BaseController
from .models import Item, ItemCreate, ItemUpdate

class ItemController(BaseController[Item, Item, ItemCreate, ItemUpdate]):
    def __init__(self, item_service):
        super().__init__(item_service)
        
    # Add custom controller methods here
```

### Services

Base service with standard data operations:

```python
from agency_implementation.foundation.api_framework import BaseService
from .models import Item, ItemCreate, ItemUpdate
from .repositories import ItemRepository

class ItemService(BaseService[Item, ItemCreate, ItemUpdate, ItemRepository]):
    def __init__(self, item_repository: ItemRepository):
        super().__init__(item_repository)
        
    # Add custom service methods here
```

### Repositories

Base repository and SQLAlchemy implementation:

```python
from agency_implementation.foundation.api_framework import SQLAlchemyRepository
from .models import Item, ItemCreate, ItemUpdate
from .database import get_db

class ItemRepository(SQLAlchemyRepository[Item, ItemCreate, ItemUpdate]):
    def __init__(self, db_session):
        super().__init__(Item, db_session)
        
    # Add custom repository methods here
```

### Router Factory

Create consistent router endpoints:

```python
from agency_implementation.foundation.api_framework import RouterFactory
from .models import Item, ItemCreate, ItemUpdate
from .controllers import ItemController
from .dependencies import get_item_controller, get_current_user

router = RouterFactory.create_router(
    schema=Item,
    create_schema=ItemCreate,
    update_schema=ItemUpdate,
    controller=ItemController,
    prefix="/api/v1/items",
    tags=["items"],
    get_controller=get_item_controller,
    get_current_user=get_current_user
)
```

### Dependency Injection

Centralized dependency management:

```python
from agency_implementation.foundation.api_framework import (
    DependencyProvider, service_provider, repository_provider
)
from .services import ItemService
from .repositories import ItemRepository

# Register dependencies
provider = DependencyProvider()
provider.register_repository(ItemRepository, ItemRepository, db_session=get_db())
provider.register_service(ItemService, ItemService)

# Create provider functions
get_item_repository = repository_provider(ItemRepository)
get_item_service = service_provider(ItemService)
```

### Authentication

JWT-based authentication:

```python
from agency_implementation.foundation.api_framework.auth.jwt import JWTAuth

auth = JWTAuth(
    secret_key="your-secret-key",
    algorithm="HS256",
    access_token_expire_minutes=30
)

# Use in router
get_current_user = auth.get_current_user
```

### Middleware

- **Error Handling**: Standardized error responses
- **Rate Limiting**: Request throttling for API protection

## Usage Example

Here's a complete example of using the API framework:

```python
from fastapi import Depends
from agency_implementation.foundation.api_framework import create_app
from agency_implementation.foundation.api_framework.routers.router_factory import RouterFactory
from agency_implementation.foundation.api_framework.dependencies.dependency_injection import (
    DependencyProvider, service_provider, repository_provider
)
from .models import Item, ItemCreate, ItemUpdate
from .controllers import ItemController
from .services import ItemService
from .repositories import ItemRepository
from .database import get_db, init_db

# Initialize dependency provider
provider = DependencyProvider()
provider.register_repository(ItemRepository, ItemRepository, db_session=Depends(get_db))
provider.register_service(ItemService, ItemService)

# Create provider functions
get_item_repository = repository_provider(ItemRepository)
get_item_service = service_provider(ItemService)

# Create controller provider
def get_item_controller():
    return ItemController(Depends(get_item_service))

# Create router
router = RouterFactory.create_router(
    schema=Item,
    create_schema=ItemCreate,
    update_schema=ItemUpdate,
    controller=ItemController,
    prefix="/api/v1/items",
    tags=["items"],
    get_controller=get_item_controller
)

# Create app
app = create_app(
    title="My Agency API",
    description="API for agency data access",
    version="1.0.0"
)

# Include router
app.include_router(router)

# Add startup event
@app.on_event("startup")
async def startup():
    await init_db()
```

## Best Practices

1. **Consistent Endpoint Structure**: Use the RouterFactory to ensure all APIs follow the same endpoint patterns
2. **Separation of Concerns**: Keep controllers, services, and repositories focused on their specific responsibilities
3. **Dependency Injection**: Use the dependency injection system for loose coupling between components
4. **Authentication**: Always implement authentication using the provided JWT module
5. **Error Handling**: Let the standard error handling middleware process exceptions
6. **Rate Limiting**: Configure appropriate rate limits for resource-intensive endpoints
7. **Documentation**: Provide detailed descriptions for all API endpoints