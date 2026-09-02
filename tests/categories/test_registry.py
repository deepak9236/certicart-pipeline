import pytest

from categories import (
    get_category,
    get_department_categories,
    get_subcategory,
    list_departments,
    supported_categories,
)


def test_supported_categories_and_departments() -> None:
    assert supported_categories() == ("laptop", "mobile")
    assert list_departments() == ("electronics",)
    assert get_department_categories("electronics") == ("laptop", "mobile")
    assert get_department_categories("appliances") == ()

    laptop = get_category(" Laptop ")
    assert laptop.department_code == "electronics"
    assert laptop.code == "laptop"
    assert get_subcategory("laptop", " Gaming_Laptop ").label == "Gaming laptop"

    mobile = get_category(" Mobile ")
    assert mobile.department_code == "electronics"
    assert mobile.code == "mobile"
    assert get_subcategory("mobile", " Flagship ").label == "Flagship smartphone"


def test_unknown_category_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported category"):
        get_category("television")


def test_unknown_subcategory_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported laptop subcategory"):
        get_subcategory("laptop", "desktop")
