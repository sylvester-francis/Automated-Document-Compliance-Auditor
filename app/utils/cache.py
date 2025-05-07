"""
Caching utilities for the application.
"""
import time
import logging
import functools
from flask import current_app

logger = logging.getLogger(__name__)

# Simple in-memory cache
_cache = {}

def cache_document(ttl=3600):
    """
    Cache decorator for document retrieval functions.
    
    Args:
        ttl: Time to live in seconds (default: 1 hour)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(document_id, *args, **kwargs):
            # Skip cache if disabled in config
            if current_app.config.get('DISABLE_CACHE', False):
                return func(document_id, *args, **kwargs)
            
            cache_key = f"document:{document_id}"
            
            # Check if we have a cached version
            cached = _cache.get(cache_key)
            if cached:
                timestamp, data = cached
                # Check if cache is still valid
                if time.time() - timestamp < ttl:
                    logger.debug(f"Cache hit for {cache_key}")
                    return data
            
            # Cache miss, call the original function
            result = func(document_id, *args, **kwargs)
            
            # Cache the result
            _cache[cache_key] = (time.time(), result)
            logger.debug(f"Cache miss for {cache_key}, cached new result")
            
            return result
        return wrapper
    return decorator

def invalidate_cache(document_id):
    """
    Invalidate cache for a specific document.
    
    Args:
        document_id: ID of the document to invalidate
    """
    cache_key = f"document:{document_id}"
    if cache_key in _cache:
        del _cache[cache_key]
        logger.debug(f"Invalidated cache for {cache_key}")

def clear_cache():
    """Clear the entire cache."""
    global _cache
    _cache = {}
    logger.debug("Cleared entire cache")
