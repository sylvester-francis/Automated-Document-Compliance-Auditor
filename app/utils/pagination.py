"""
Pagination utilities for the application.
"""
import math
from flask import request

class Pagination:
    """Pagination class for MongoDB queries."""
    
    def __init__(self, page, per_page, total_count):
        """
        Initialize pagination.
        
        Args:
            page: Current page number (1-indexed)
            per_page: Number of items per page
            total_count: Total number of items
        """
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
        
    @property
    def pages(self):
        """Total number of pages."""
        return int(math.ceil(self.total_count / float(self.per_page)))
    
    @property
    def has_prev(self):
        """Check if there is a previous page."""
        return self.page > 1
    
    @property
    def has_next(self):
        """Check if there is a next page."""
        return self.page < self.pages
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """
        Iterate through page numbers to render in pagination controls.
        
        Args:
            left_edge: Number of pages at the beginning
            left_current: Number of pages before current page
            right_current: Number of pages after current page
            right_edge: Number of pages at the end
            
        Returns:
            Iterator of page numbers or None for ellipsis
        """
        last = 0
        for num in range(1, self.pages + 1):
            if (num <= left_edge or
                (self.page - left_current - 1 < num < self.page + right_current) or
                num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num

def get_pagination(collection, query=None, page=None, per_page=10, sort_by=None, sort_direction=-1):
    """
    Get paginated results from MongoDB collection.
    
    Args:
        collection: MongoDB collection
        query: Query filter (default: None)
        page: Page number (default: from request args or 1)
        per_page: Items per page (default: 10)
        sort_by: Field to sort by (default: None)
        sort_direction: Sort direction (default: -1 for descending)
        
    Returns:
        Tuple of (items, pagination)
    """
    # Get page from request args if not provided
    if page is None:
        try:
            page = int(request.args.get('page', 1))
        except (TypeError, ValueError):
            page = 1
    
    # Ensure page is at least 1
    page = max(1, page)
    
    # Set up query
    if query is None:
        query = {}
    
    # Count total items
    total = collection.count_documents(query)
    
    # Set up sort
    sort_params = None
    if sort_by:
        sort_params = [(sort_by, sort_direction)]
    
    # Get items for current page
    skip = (page - 1) * per_page
    cursor = collection.find(query)
    
    if sort_params:
        cursor = cursor.sort(sort_params)
    
    items = list(cursor.skip(skip).limit(per_page))
    
    # Create pagination object
    pagination = Pagination(page, per_page, total)
    
    return items, pagination
