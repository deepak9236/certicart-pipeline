"""Product-category definitions and registry."""

from categories.contracts import AttributeValue, CategoryDefinition, SubcategoryDefinition
from categories.handler import CategoryHandler
from categories.registry import (
    LAPTOP,
    MOBILE,
    SUPPORTED_RETAILER_CATEGORIES,
    get_category,
    get_category_handler,
    get_department_categories,
    get_subcategory,
    is_category_supported,
    list_departments,
    register_category_handler,
    supported_categories,
)

__all__ = [
    "LAPTOP",
    "MOBILE",
    "SUPPORTED_RETAILER_CATEGORIES",
    "AttributeValue",
    "CategoryDefinition",
    "CategoryHandler",
    "SubcategoryDefinition",
    "get_category",
    "get_category_handler",
    "get_department_categories",
    "get_subcategory",
    "is_category_supported",
    "list_departments",
    "register_category_handler",
    "supported_categories",
]
