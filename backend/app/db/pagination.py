"""
Pagination utilities for database queries.

This module provides helper functions and utilities for implementing
pagination in database queries using SQLAlchemy.
"""

from typing import TypeVar, Generic, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from math import ceil

T = TypeVar("T")


def paginate(
    query,
    skip: int = 0,
    limit: int = 20,
    max_limit: int = 100,
) -> Tuple[List[T], int]:
    """
    Apply pagination to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object
        skip: Number of items to skip
        limit: Maximum number of items to return
        max_limit: Maximum allowed limit to prevent abuse

    Returns:
        Tuple of (items, total_count)
    """
    # Validate and enforce limits
    if limit > max_limit:
        limit = max_limit

    # Get total count before applying limits
    total = query.count()

    # Apply offset and limit
    items = query.offset(skip).limit(limit).all()

    return items, total


def get_pagination_metadata(
    skip: int,
    limit: int,
    total: int,
) -> dict:
    """
    Calculate pagination metadata.

    Args:
        skip: Number of items skipped
        limit: Maximum items per page
        total: Total number of items

    Returns:
        Dictionary with pagination metadata
    """
    pages = ceil(total / limit) if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1

    return {
        "skip": skip,
        "limit": limit,
        "total": total,
        "page": page,
        "pages": pages,
    }


class PaginationHelper(Generic[T]):
    """
    Helper class for managing pagination in queries.

    Provides convenient methods for applying pagination and retrieving
    metadata for paginated responses.
    """

    def __init__(
        self,
        session: Session,
        model_class: type,
        skip: int = 0,
        limit: int = 20,
        max_limit: int = 100,
    ):
        """
        Initialize pagination helper.

        Args:
            session: SQLAlchemy session
            model_class: Model class to query
            skip: Number of items to skip
            limit: Maximum items per page
            max_limit: Maximum allowed limit
        """
        self.session = session
        self.model_class = model_class
        self.skip = skip
        self.limit = min(limit, max_limit)
        self.max_limit = max_limit

    def get_page(self, query=None):
        """
        Get a page of results.

        Args:
            query: Optional custom query; defaults to all records

        Returns:
            Tuple of (items, metadata)
        """
        if query is None:
            query = self.session.query(self.model_class)

        items, total = paginate(query, self.skip, self.limit, self.max_limit)
        metadata = get_pagination_metadata(self.skip, self.limit, total)

        return items, metadata


# TODO: Add cursor pagination support
# TODO: Add filtering utilities
# TODO: Add sorting utilities
