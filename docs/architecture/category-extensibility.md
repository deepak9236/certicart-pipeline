# Category Extensibility & Hierarchical Taxonomy

Certikart is a generic product-intelligence platform, not a laptop-only catalog. Laptop is the first fully implemented category domain plugin. Mobile phones, televisions, headphones, appliances, and tools can be added cleanly without changing the shared pipeline core.

---

## 2-Tier Hierarchical Taxonomy

```text
src/categories/
├── contracts.py                  # CategoryDefinition, SubcategoryDefinition, AttributeValue
├── handler.py                    # CategoryHandler Protocol interface
├── registry.py                   # Multi-tier Registry (departments, categories, handlers)
│
└── electronics/                  # Top-Level Category (Department)
    ├── __init__.py
    └── laptop/                   # Category Domain Plugin
        ├── __init__.py           # Package exports
        ├── handler.py            # LaptopCategoryHandler (implements CategoryHandler)
        ├── normalizer.py         # LaptopIdentityNormalizer
        └── rules.py              # check_laptop_hard_conflicts & ConflictReason
```

### Hierarchy Breakdown:
1. **Department / Top Category**: `electronics`, `appliances`, `home`, etc.
2. **Category / Domain**: `laptop`, `mobile`, `television`, `audio`.
3. **Subcategories (Merchandising)**: `gaming_laptop`, `business_laptop`, `thin_and_light_laptop`, `student_laptop`, etc.

---

## CategoryHandler Protocol

Every category domain plugin implements the `CategoryHandler` protocol defined in [`src/categories/handler.py`](file:///Users/ashishjangde/programing/certikart-pipeline/src/categories/handler.py):

```python
class CategoryHandler(Protocol):
    @property
    def category_code(self) -> str: ...

    def normalize(self, product: ParsedProduct) -> ProductFingerprint:
        """Extract structured attributes and build canonical domain product fingerprint."""
        ...

    def check_hard_conflicts(
        self,
        left: ProductFingerprint,
        right: ProductFingerprint,
    ) -> tuple[bool, str | None]:
        """Deterministic hard conflict elimination (e.g. chip, RAM, GPU, screen)."""
        ...

    def compute_similarity(
        self,
        left: ProductFingerprint,
        right: ProductFingerprint,
    ) -> float:
        """Domain-weighted attribute similarity score (0.0 to 1.0)."""
        ...
```

---

## Adding a New Product Category

To add a new category (e.g., `mobile` under `electronics`):

1. **Define Taxonomy Definition**:
   Register category under `src/categories/registry.py`:
   ```python
   MOBILE = CategoryDefinition(
       department_code="electronics",
       code="mobile",
       label="Mobile Phone",
       subcategories=(
           SubcategoryDefinition(code="flagship", label="Flagship"),
           SubcategoryDefinition(code="budget", label="Budget"),
       ),
       identity_attributes=("chipset", "ram_gb", "storage_gb", "color"),
       review_aspects=("camera", "battery", "performance", "display", "build"),
   )
   ```
2. **Create Category Domain Package**:
   Create directory `src/categories/electronics/mobile/`:
   - `handler.py`: Implements `MobileCategoryHandler(CategoryHandler)`.
   - `normalizer.py`: Extracts `chipset`, `ram_gb`, `storage_gb`, `color`, and canonical model name.
   - `rules.py`: Implements `check_mobile_hard_conflicts` (e.g., storage capacity differences, 4G vs 5G variants).
3. **Wire in Category Registry**:
   Add lazy handler loader to `get_category_handler("mobile")` in `src/categories/registry.py`.
4. **Unit Tests**:
   Add test suite under `tests/categories/` covering domain normalization, hard conflict rejections, and cross-retailer matching.
