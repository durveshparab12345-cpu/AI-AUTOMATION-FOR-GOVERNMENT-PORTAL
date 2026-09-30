"""
Pagination schemas for API responses.

This module defines Pydantic models for paginated API responses,
providing consistent pagination metadata across all list endpoints.
"""

from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.

    Wraps list responses with pagination metadata including total count,
    skip/limit parameters, and pagination links.

    Attributes:
        items: List of items in the current page
        total: Total number of items across all pages
        skip: Number of items skipped
        limit: Maximum number of items per page
        page: Current page number
        pages: Total number of pages
    """

    items: List[T]
    total: int = Field(..., ge=0, description="Total number of items")
    skip: int = Field(0, ge=0, description="Number of items skipped")
    limit: int = Field(20, ge=1, le=100, description="Items per page")
    page: int = Field(1, ge=1, description="Current page number")
    pages: int = Field(..., ge=1, description="Total number of pages")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "items": [{"id": "item1", "name": "Example Item"}],
                "total": 100,
                "skip": 0,
                "limit": 20,
                "page": 1,
                "pages": 5,
            }
        }


class PaginationParams(BaseModel):
    """
    Standard pagination parameters for list queries.

    Attributes:
        skip: Number of items to skip from the beginning
        limit: Maximum number of items to return
    """

    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(20, ge=1, le=100, description="Maximum items to return")


class CursorPaginationParams(BaseModel):
    """
    Cursor-based pagination parameters for large result sets.

    Attributes:
        cursor: Opaque cursor identifying the position in the result set
        limit: Maximum number of items to return
    """

    cursor: str = Field(None, description="Pagination cursor")
    limit: int = Field(20, ge=1, le=100, description="Maximum items to return")


class SortParams(BaseModel):
    """
    Sorting parameters for list queries.

    Attributes:
        sort_by: Field name to sort by
        order: Sort order (asc or desc)
    """

    sort_by: str = Field("created_at", description="Field to sort by")
    order: str = Field("desc", regex="^(asc|desc)$", description="Sort order")
