"""Explicit category registry; add categories without changing pipeline core."""

from categories.contracts import CategoryDefinition, SubcategoryDefinition
from categories.handler import CategoryHandler

LAPTOP = CategoryDefinition(
    department_code="electronics",
    code="laptop",
    label="Laptop",
    subcategories=(
        SubcategoryDefinition(code="gaming_laptop", label="Gaming laptop"),
        SubcategoryDefinition(code="business_laptop", label="Business laptop"),
        SubcategoryDefinition(code="thin_and_light_laptop", label="Thin and light laptop"),
        SubcategoryDefinition(code="two_in_one_laptop", label="2-in-1 laptop"),
        SubcategoryDefinition(code="student_laptop", label="Student laptop"),
        SubcategoryDefinition(code="chromebook", label="Chromebook"),
    ),
    identity_attributes=(
        "cpu_model",
        "gpu_model",
        "ram_gb",
        "storage_gb",
    ),
    review_aspects=(
        "performance",
        "battery",
        "thermals",
        "display",
        "build",
        "reliability",
        "keyboard",
        "trackpad",
        "weight",
        "fan_noise",
        "webcam",
        "speakers",
        "ports",
        "gaming",
        "upgradeability",
    ),
)

MOBILE = CategoryDefinition(
    department_code="electronics",
    code="mobile",
    label="Mobile Phone",
    subcategories=(
        SubcategoryDefinition(code="flagship", label="Flagship smartphone"),
        SubcategoryDefinition(code="mid_range", label="Mid-range smartphone"),
        SubcategoryDefinition(code="budget", label="Budget smartphone"),
        SubcategoryDefinition(code="foldable", label="Foldable phone"),
        SubcategoryDefinition(code="gaming_phone", label="Gaming phone"),
    ),
    identity_attributes=(
        "chipset",
        "ram_gb",
        "storage_gb",
        "color",
    ),
    review_aspects=(
        "camera",
        "battery",
        "performance",
        "display",
        "build",
        "software",
        "charging",
        "audio",
    ),
)

_CATEGORIES: dict[str, CategoryDefinition] = {
    LAPTOP.code: LAPTOP,
    MOBILE.code: MOBILE,
}

_CATEGORY_HANDLERS: dict[str, CategoryHandler] = {}

SUPPORTED_RETAILER_CATEGORIES: dict[str, set[str]] = {
    "amazon": {"laptop", "mobile"},
    "flipkart": {"laptop", "mobile"},
    "croma": {"laptop", "mobile"},
}


def get_category(code: str) -> CategoryDefinition:
    normalized = code.casefold().strip()
    try:
        return _CATEGORIES[normalized]
    except KeyError as error:
        raise ValueError(f"unsupported category: {code!r}") from error


def get_category_handler(code: str) -> CategoryHandler:
    """Retrieve domain intelligence handler for a given category code."""
    normalized = code.casefold().strip()
    if normalized not in _CATEGORY_HANDLERS:
        if normalized == "laptop":
            from categories.electronics.laptop.handler import LaptopCategoryHandler

            _CATEGORY_HANDLERS["laptop"] = LaptopCategoryHandler()
        elif normalized == "mobile":
            from categories.electronics.mobile.handler import MobileCategoryHandler

            _CATEGORY_HANDLERS["mobile"] = MobileCategoryHandler()
        else:
            raise ValueError(f"no registered handler for category: {code!r}")
    return _CATEGORY_HANDLERS[normalized]


def register_category_handler(code: str, handler: CategoryHandler) -> None:
    """Register a new domain intelligence category handler."""
    normalized = code.casefold().strip()
    _CATEGORY_HANDLERS[normalized] = handler


def is_category_supported(retailer: str, category: str) -> bool:
    """Check whether a category is supported for a given retailer."""
    ret = retailer.casefold().strip()
    cat = category.casefold().strip()
    return cat in SUPPORTED_RETAILER_CATEGORIES.get(ret, set())


def supported_categories() -> tuple[str, ...]:
    return tuple(sorted(_CATEGORIES))


def list_departments() -> tuple[str, ...]:
    """List all registered top-level departments (e.g. electronics, appliances)."""
    return tuple(sorted({cat.department_code for cat in _CATEGORIES.values()}))


def get_department_categories(department_code: str) -> tuple[str, ...]:
    """List all registered category codes belonging to a given department."""
    dept = department_code.casefold().strip()
    return tuple(sorted(cat.code for cat in _CATEGORIES.values() if cat.department_code == dept))


def get_subcategory(category_code: str, subcategory_code: str) -> SubcategoryDefinition:
    category = get_category(category_code)
    normalized = subcategory_code.casefold().strip()
    for subcategory in category.subcategories:
        if subcategory.code == normalized:
            return subcategory
    raise ValueError(f"unsupported {category.code} subcategory: {subcategory_code!r}")
