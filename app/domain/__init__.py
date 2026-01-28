"""
Domain Knowledge Module
Provides specialized knowledge for different database domains.
"""

from .olist_ecommerce import (
    OLIST_SCHEMA,
    OLIST_METRICS,
    OLIST_ANALYTICAL_PATTERNS,
    OLIST_QUERY_EXAMPLES
)

__all__ = [
    'OLIST_SCHEMA',
    'OLIST_METRICS', 
    'OLIST_ANALYTICAL_PATTERNS',
    'OLIST_QUERY_EXAMPLES'
]