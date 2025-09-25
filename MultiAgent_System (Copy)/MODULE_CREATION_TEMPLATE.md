# Module Creation Template - Prompt Rule Base

## Overview
When creating a new module, follow this template structure to maintain consistency with the existing codebase. Each module should follow the **Route → Service → Repository → Database** flow with proper separation of concerns.

## File Structure Template
```
api/src/{module_name}/
├── __init__.py
├── models.py
├── schemas.py
├── repository.py
├── service.py
└── routes.py
```

## 1. MODELS.PY - Database Models

### Template Structure:
```python
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, UniqueConstraint, Boolean, Index
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.postgresql import ENUM
import enum
from sqlalchemy.orm import relationship
from ...core.database import Base

# ===== Main Entity Model =====
class MainEntity(Base):
    __tablename__ = "tbl_{entity_name}"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    # Add other fields as needed
    
    # Relationships - Only load when explicitly requested
    related_entity = relationship("RelatedEntity", back_populates="main_entity", lazy="select")
    # Heavy relationships - use noload by default
    heavy_relations = relationship("HeavyEntity", back_populates="main_entity", lazy="noload")
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_entity_status_field', 'status', 'field_name'),
    )
```

### Key Rules:
- **Naming**: Use PascalCase for class names, snake_case for table names
- **Table prefix**: Always use `tbl_` prefix for table names
- **Indexing**: Add indexes on frequently queried fields
- **Relationships**: Use `lazy="select"` for light relationships, `lazy="noload"` for heavy ones
- **Constraints**: Add appropriate unique constraints and foreign keys
- **Documentation**: Add clear comments for complex relationships

## 2. SCHEMAS.PY - Data Validation & Serialization

### Template Structure:
```python
from datetime import datetime, date
from typing import Any, Optional, List, Dict
import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

# ===== Pagination Schemas =====
class PaginatedResponse(BaseModel):
    """Base schema for paginated responses."""
    items: list[Any]
    total_items: int
    page: int
    limit: int
    total_pages: int

# ===== Main Entity Schemas =====
class MainEntityBase(BaseModel):
    """Base schema for MainEntity data."""
    name: str = Field(..., min_length=1, max_length=255, description="Entity name")
    # Add other base fields

class MainEntityCreate(MainEntityBase):
    """Schema for creating a new entity."""

class MainEntityUpdate(BaseModel):
    """Schema for updating an existing entity."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    # Add other optional fields

class MainEntityResponse(MainEntityBase):
    """Schema for entity responses."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

class MainEntityResponseWithRelations(MainEntityResponse):
    """Schema for entity responses with related data."""
    related_entity: Optional[RelatedEntityInfo] = None

class PaginatedMainEntityResponse(PaginatedResponse):
    """Schema for paginated entity responses."""
    items: list[MainEntityResponseWithRelations]

# ===== Filter Schemas =====
class MainEntityFilters(BaseModel):
    """Schema for entity filters."""
    status: Optional[str] = None
    search_name: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
```

### Key Rules:
- **Schema Hierarchy**: Always create Base → Create → Update → Response hierarchy
- **Field Validation**: Use Pydantic Field with proper validation rules
- **Documentation**: Add docstrings for all schemas
- **ConfigDict**: Use `ConfigDict(from_attributes=True)` for response schemas
- **Optional Fields**: Make update fields optional
- **Pagination**: Include pagination schemas for list endpoints
- **Relations**: Create separate schemas for responses with related data

## 3. REPOSITORY.PY - Data Access Layer

### Template Structure:
```python
from sqlalchemy import delete, select, update, and_, or_, func, extract
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid
from datetime import datetime, date, UTC
from typing import Optional, List, Dict, Any
import math

from api.core.exceptions import AlreadyExistsException, NotFoundException, ValidationException
from api.src.{module_name}.models import MainEntity, RelatedEntity
from api.src.{module_name}.schemas import MainEntityCreate, MainEntityUpdate, MainEntityFilters

# ===== Main Entity Repository =====
class MainEntityRepository:
    """Repository for handling main entity database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity_data: MainEntityCreate, user_id: str) -> MainEntity:
        """Create a new entity."""
        entity_dict = entity_data.model_dump()
        entity_dict["created_by"] = user_id
        
        entity = MainEntity(**entity_dict)
        try:
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistsException(
                f"Entity with name {entity_data.name} already exists"
            )

    async def get_by_id(self, entity_id: int) -> MainEntity:
        """Get entity by ID."""
        query = select(MainEntity).where(MainEntity.id == entity_id)
        result = await self.session.execute(query)
        entity = result.scalar_one_or_none()

        if not entity:
            raise NotFoundException(f"Entity with id {entity_id} not found")
        return entity

    async def get_all(self) -> list[MainEntity]:
        """Get all entities."""
        query = select(MainEntity)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_all_with_filters_and_pagination(
        self,
        filters: MainEntityFilters,
    ) -> tuple[list[MainEntity], int]:
        """Get entities with filters and pagination."""
        query = select(MainEntity)
        
        # Apply filters
        if filters.status:
            query = query.where(MainEntity.status == filters.status)
        
        if filters.search_name:
            query = query.where(MainEntity.name.ilike(f"%{filters.search_name}%"))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.session.scalar(count_query)
        
        # Apply pagination
        offset = (filters.page - 1) * filters.limit
        query = query.offset(offset).limit(filters.limit)
        
        # Execute query
        result = await self.session.execute(query)
        entities = list(result.scalars().all())
        
        return entities, total_count

    async def update(self, entity_id: int, entity_data: MainEntityUpdate, user_id: str) -> MainEntity:
        """Update entity by ID."""
        update_data = entity_data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("No fields to update")

        update_data["updated_by"] = user_id
        
        query = update(MainEntity).where(MainEntity.id == entity_id).values(**update_data)
        result = await self.session.execute(query)

        if result.rowcount == 0:
            raise NotFoundException(f"Entity with id {entity_id} not found")

        await self.session.commit()
        return await self.get_by_id(entity_id)

    async def delete(self, entity_id: int) -> None:
        """Delete entity by ID."""
        query = delete(MainEntity).where(MainEntity.id == entity_id)
        result = await self.session.execute(query)

        if result.rowcount == 0:
            raise NotFoundException(f"Entity with id {entity_id} not found")

        await self.session.commit()
```

### Key Rules:
- **Error Handling**: Always handle IntegrityError and raise custom exceptions
- **Transaction Management**: Use proper commit/rollback patterns
- **Query Optimization**: Use selectinload for eager loading when needed
- **Pagination**: Implement proper offset/limit pagination
- **Filtering**: Support multiple filter conditions
- **User Tracking**: Always track created_by/updated_by
- **Documentation**: Add docstrings for all methods

## 4. SERVICE.PY - Business Logic Layer

### Template Structure:
```python
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from api.src.{module_name}.repository import MainEntityRepository
from api.src.{module_name}.schemas import (
    MainEntityCreate,
    MainEntityUpdate,
    MainEntityResponse,
    MainEntityResponseWithRelations,
    MainEntityFilters,
    PaginatedMainEntityResponse,
)

# ===== Main Entity Service =====
class MainEntityService:
    """Service layer for main entity operations."""

    def __init__(self, repository: MainEntityRepository):
        self.repository = repository

    async def create_entity(self, entity_data: MainEntityCreate, user_id: str) -> MainEntityResponse:
        """Create a new entity."""
        entity = await self.repository.create(entity_data, user_id)
        return MainEntityResponse.model_validate(entity)

    async def get_entity(self, entity_id: int) -> MainEntityResponse:
        """Get entity by ID."""
        entity = await self.repository.get_by_id(entity_id)
        return MainEntityResponse.model_validate(entity)

    async def get_all_entities(self) -> list[MainEntityResponse]:
        """Get all entities."""
        entities = await self.repository.get_all()
        return [MainEntityResponse.model_validate(entity) for entity in entities]

    async def get_filtered_and_paginated_entities(
        self,
        filters: MainEntityFilters,
    ) -> PaginatedMainEntityResponse:
        """Get entities with filters and pagination."""
        entities, total_count = await self.repository.get_all_with_filters_and_pagination(filters)
        
        # Calculate pagination info
        total_pages = math.ceil(total_count / filters.limit) if total_count > 0 else 0
        
        # Convert to response models
        entity_responses = []
        for entity in entities:
            entity_response = MainEntityResponse.model_validate(entity)
            # Add related data if available
            if entity.related_entity:
                entity_response_with_relations = MainEntityResponseWithRelations(
                    **entity_response.model_dump(),
                    related_entity=RelatedEntityInfo.model_validate(entity.related_entity)
                )
            else:
                entity_response_with_relations = MainEntityResponseWithRelations(
                    **entity_response.model_dump()
                )
            entity_responses.append(entity_response_with_relations)
        
        return PaginatedMainEntityResponse(
            items=entity_responses,
            total_items=total_count,
            page=filters.page,
            limit=filters.limit,
            total_pages=total_pages
        )

    async def update_entity(self, entity_id: int, entity_data: MainEntityUpdate, user_id: str) -> MainEntityResponse:
        """Update entity by ID."""
        entity = await self.repository.update(entity_id, entity_data, user_id)
        return MainEntityResponse.model_validate(entity)

    async def delete_entity(self, entity_id: int) -> None:
        """Delete entity by ID."""
        await self.repository.delete(entity_id)
```

### Key Rules:
- **Repository Dependency**: Always inject repository in constructor
- **Model Validation**: Use `model_validate()` for Pydantic conversion
- **Business Logic**: Handle complex business rules here
- **Error Propagation**: Let repository exceptions bubble up
- **Data Transformation**: Handle complex data transformations
- **Pagination Logic**: Calculate pagination metadata in service layer

## 5. ROUTES.PY - API Endpoints

### Template Structure:
```python
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from api.core.database import get_session
from api.core.logging import get_logger
from api.src.{module_name}.repository import MainEntityRepository
from api.src.{module_name}.schemas import (
    MainEntityCreate,
    MainEntityUpdate,
    MainEntityResponse,
    MainEntityResponseWithRelations,
    MainEntityFilters,
    PaginatedMainEntityResponse,
)
from api.src.{module_name}.service import MainEntityService

# Set up logger for this module
logger = get_logger(__name__)

router = APIRouter(prefix="/{module_name}")

# ===== Dependencies =====
def get_main_entity_service(session: AsyncSession = Depends(get_session)) -> MainEntityService:
    """Dependency for getting main entity service instance."""
    repository = MainEntityRepository(session)
    return MainEntityService(repository)

# ===== Main Entity Routes =====
@router.get("", response_model=PaginatedMainEntityResponse, tags=["{module_name}"])
async def get_all_entities(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status"),
    search_name: Optional[str] = Query(None, description="Search by name"),
    page: int = Query(1, ge=1, description="Current page"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    service: MainEntityService = Depends(get_main_entity_service),
) -> PaginatedMainEntityResponse:
    """Get all entities with filters and pagination."""
    filters = MainEntityFilters(
        status=status,
        search_name=search_name,
        page=page,
        limit=limit,
    )
    return await service.get_filtered_and_paginated_entities(filters)

@router.get("/{entity_id}", response_model=MainEntityResponse, tags=["{module_name}"])
async def get_entity(
    entity_id: int,
    service: MainEntityService = Depends(get_main_entity_service),
) -> MainEntityResponse:
    """Get entity by ID."""
    return await service.get_entity(entity_id)

@router.post("", response_model=MainEntityResponse, status_code=status.HTTP_201_CREATED, tags=["{module_name}"])
async def create_entity(
    entity_data: MainEntityCreate,
    request: Request,
    service: MainEntityService = Depends(get_main_entity_service),
) -> MainEntityResponse:
    """Create a new entity."""
    # In a real application, you would get the user_id from the authenticated user
    user_id = "system"  # Replace with actual user ID from authentication
    return await service.create_entity(entity_data, user_id)

@router.patch("/{entity_id}", response_model=MainEntityResponse, tags=["{module_name}"])
async def update_entity(
    entity_id: int,
    entity_data: MainEntityUpdate,
    request: Request,
    service: MainEntityService = Depends(get_main_entity_service),
) -> MainEntityResponse:
    """Update entity by ID."""
    # In a real application, you would get the user_id from the authenticated user
    user_id = "system"  # Replace with actual user ID from authentication
    return await service.update_entity(entity_id, entity_data, user_id)

@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["{module_name}"])
async def delete_entity(
    entity_id: int,
    service: MainEntityService = Depends(get_main_entity_service),
) -> None:
    """Delete entity by ID."""
    await service.delete_entity(entity_id)
```

### Key Rules:
- **Router Prefix**: Use module name as router prefix
- **Dependency Injection**: Create dependency functions for each service
- **Route Organization**: Group routes by entity with proper tags
- **HTTP Methods**: Use appropriate HTTP methods (GET, POST, PATCH, DELETE)
- **Status Codes**: Use proper HTTP status codes
- **Query Parameters**: Use Query for optional parameters
- **Documentation**: Add docstrings for all endpoints
- **Authentication**: Add placeholder for user_id (replace with actual auth)

## 6. __INIT__.PY - Module Initialization

### Template Structure:
```python
# Module initialization file
```

### Key Rules:
- Keep it minimal, just for module identification
- Add any module-level imports if needed

## Overall Flow & Architecture

### 1. **Request Flow**:
```
HTTP Request → Route → Service → Repository → Database
Response ← Route ← Service ← Repository ← Database
```

### 2. **Data Flow**:
```
Request Schema → Service → Repository → Model
Model → Repository → Service → Response Schema
```

### 3. **Dependency Flow**:
```
Route depends on Service
Service depends on Repository
Repository depends on Database Session
```

## Important Notes & Best Practices

### 1. **Naming Conventions**:
- **Files**: snake_case (e.g., `main_entity.py`)
- **Classes**: PascalCase (e.g., `MainEntity`)
- **Functions**: snake_case (e.g., `get_entity`)
- **Variables**: snake_case (e.g., `entity_data`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_LIMIT`)

### 2. **Error Handling**:
- Use custom exceptions from `api.core.exceptions`
- Handle database integrity errors properly
- Provide meaningful error messages
- Log errors appropriately

### 3. **Performance Considerations**:
- Use lazy loading for relationships
- Implement proper pagination
- Add database indexes for frequently queried fields
- Use selectinload for eager loading when needed

### 4. **Security**:
- Validate all input data
- Use proper authentication (replace placeholder user_id)
- Sanitize user inputs
- Implement proper authorization

### 5. **Testing**:
- Create unit tests for each layer
- Test repository methods with database
- Test service methods with mocked repository
- Test routes with mocked service

### 6. **Documentation**:
- Add docstrings to all classes and methods
- Use type hints consistently
- Document complex business logic
- Add examples in docstrings

### 7. **Database Migrations**:
- Create Alembic migrations for model changes
- Test migrations on development database
- Include rollback scripts
- Document breaking changes

## Quick Checklist for New Module

- [ ] Create `__init__.py`
- [ ] Define models in `models.py`
- [ ] Create schemas in `schemas.py`
- [ ] Implement repository in `repository.py`
- [ ] Add business logic in `service.py`
- [ ] Create API endpoints in `routes.py`
- [ ] Add module to main router
- [ ] Create database migrations
- [ ] Write unit tests
- [ ] Update documentation

## Example Implementation

For a complete example, see the `keywords` module in `api/src/keywords/` which follows this template structure perfectly.

This template ensures consistency, maintainability, and scalability across all modules in your FastAPI application. 