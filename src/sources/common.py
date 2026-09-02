"""Common extraction and parsing utilities shared across all retailer sources."""

from __future__ import annotations

import contextlib
import json
import re
from typing import Any

from parsel import Selector

from categories.contracts import AttributeValue
from normalization import normalize_capacity_gb, normalize_text

PRICE_CLEAN_PATTERN = re.compile(r"[^\d.]")

KNOWN_BRANDS: tuple[str, ...] = (
    "apple",
    "lenovo",
    "hp",
    "dell",
    "asus",
    "acer",
    "samsung",
    "msi",
    "infinix",
    "xiaomi",
    "redmibook",
    "realme",
    "honor",
    "microsoft",
    "lg",
    "primebook",
    "oneplus",
    "motorola",
    "nothing",
    "google",
    "sony",
    "boat",
    "noise",
    "boult",
)


def extract_digits_to_paise(raw_text: str | None) -> int | None:
    """Extract numeric price string and convert to integer paise."""
    if not raw_text:
        return None
    # Reject discount percentages or rating badges (e.g. "8% off", "(2)")
    if ("%" in raw_text or "off" in raw_text.casefold()) and "₹" not in raw_text:
        return None
    cleaned = PRICE_CLEAN_PATTERN.sub("", raw_text)
    if not cleaned:
        return None
    try:
        amount_float = float(cleaned)
        # Reject single-digit badge numbers if no rupee symbol
        if amount_float < 50.0 and "₹" not in raw_text:
            return None
        return int(amount_float * 100)
    except ValueError:
        return None


def infer_brand(
    title: str,
    specs_brand: str | None = None,
    known_brands: tuple[str, ...] = KNOWN_BRANDS,
) -> str:
    """Infer brand from specs metadata or product title."""
    if specs_brand and specs_brand.strip():
        return specs_brand.strip().title()
    normalized_title = title.casefold()
    for brand in known_brands:
        if brand in normalized_title:
            return brand.title()
    parts = title.strip().split()
    return parts[0] if parts else "Generic"


def clean_capacity_str(raw: str) -> str:
    """Extract standard capacity expression (e.g. '16 GB', '512 GB', '1 TB') from raw string."""
    match = re.search(r"(\d+(?:\.\d+)?\s*(?:tb|gb))", raw, re.IGNORECASE)
    return match.group(1) if match else raw


def extract_json_ld_products(html_or_selector: str | Selector) -> list[dict[str, Any]]:
    """Extract all schema.org Product structures from JSON-LD script elements."""
    sel = Selector(text=html_or_selector) if isinstance(html_or_selector, str) else html_or_selector
    products: list[dict[str, Any]] = []

    for script_text in sel.css("script[type='application/ld+json']::text").getall():
        cleaned = script_text.strip()
        if not cleaned:
            continue
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            continue

        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            item_type = str(item.get("@type", "")).casefold()
            if item_type in ("product", "individualproduct"):
                products.append(item)
            elif "@graph" in item and isinstance(item["@graph"], list):
                for graph_item in item["@graph"]:
                    if isinstance(graph_item, dict) and str(
                        graph_item.get("@type", "")
                    ).casefold() in ("product", "individualproduct"):
                        products.append(graph_item)

    return products


def build_category_attributes(
    category: str,
    title: str,
    raw_specs: dict[str, str],
) -> dict[str, AttributeValue]:
    """Construct structured domain attributes using category handler while preserving specs."""
    attributes: dict[str, AttributeValue] = {}

    # Store normalized raw specifications
    for k, v in raw_specs.items():
        clean_key = normalize_text(k)
        if clean_key:
            attributes[clean_key] = v.strip()

    norm_specs = {normalize_text(k): v for k, v in raw_specs.items()}

    # Laptop category extraction
    if category.casefold() == "laptop":
        # Extract RAM
        for ram_key in ("ram", "ram size", "system memory", "ram capacity", "internal memory"):
            if ram_key in norm_specs:
                with contextlib.suppress(ValueError):
                    attributes["ram_gb"] = normalize_capacity_gb(
                        clean_capacity_str(norm_specs[ram_key])
                    )
                    break
        if "ram_gb" not in attributes:
            ram_match = re.search(
                r"(\d+\s*(?:GB|TB))\s+(?:RAM|DDR|LPDDR|Memory)", title, re.IGNORECASE
            )
            if ram_match:
                with contextlib.suppress(ValueError):
                    attributes["ram_gb"] = normalize_capacity_gb(ram_match.group(1))

        # Extract Storage
        for st_key in (
            "storage",
            "ssd capacity",
            "hard drive size",
            "hdd capacity",
            "ssd",
            "emmc capacity",
            "hard disk description",
            "hard disk size",
            "storage capacity",
            "hard drive capacity",
        ):
            if st_key in norm_specs:
                with contextlib.suppress(ValueError):
                    attributes["storage_gb"] = normalize_capacity_gb(
                        clean_capacity_str(norm_specs[st_key])
                    )
                    break
        if "storage_gb" not in attributes:
            st_match = re.search(
                r"(\d+\s*(?:GB|TB))\s+(?:SSD|HDD|ROM|NVMe|Storage|EMMC)", title, re.IGNORECASE
            )
            if st_match:
                with contextlib.suppress(ValueError):
                    attributes["storage_gb"] = normalize_capacity_gb(st_match.group(1))

        # Extract CPU
        for cpu_key in (
            "cpu model",
            "processor type",
            "processor brand",
            "processor",
            "cpu",
            "processor name",
            "processor variant",
            "processor speed",
            "chipset",
        ):
            if cpu_key in norm_specs:
                attributes["cpu_model"] = norm_specs[cpu_key].strip()
                break
        if "cpu_model" not in attributes:
            cpu_match = re.search(
                r"\b(Apple\s+M[1-5](?:\s+(?:Pro|Max|Ultra))?|M[1-5](?:\s+(?:Pro|Max|Ultra))?(?:\s+chip)?|Intel\s+Core\s+(?:Ultra\s+)?[i3579]-?\w*|AMD\s+Ryzen\s+[3579]-?\w+|Snapdragon\s+X\s+\w+|MediaTek\s+\w+)\b",
                title,
                re.IGNORECASE,
            )
            if cpu_match:
                raw_cpu = cpu_match.group(1).strip()
                attributes["cpu_model"] = re.sub(
                    r"\s+chip$", "", raw_cpu, flags=re.IGNORECASE
                ).strip()
            elif "macbook" in title.casefold() or "apple" in title.casefold():
                m_match = re.search(r"\b(M[1-5](?:\s+(?:Pro|Max|Ultra))?)\b", title, re.IGNORECASE)
                if m_match:
                    attributes["cpu_model"] = f"Apple {m_match.group(1).strip()}"

        # Extract GPU
        for gpu_key in (
            "graphic processor",
            "graphics processor",
            "graphics coprocessor",
            "graphics card description",
            "gpu",
            "graphics",
            "dedicated graphic memory capacity",
            "dedicated graphic card",
            "graphics description",
        ):
            if gpu_key in norm_specs:
                attributes["gpu_model"] = norm_specs[gpu_key].strip()
                break
        if "gpu_model" not in attributes:
            gpu_match = re.search(
                r"\b(NVIDIA\s+GeForce\s+RTX\s+\d+(?:\s*Ti)?|NVIDIA\s+RTX\s+\d+|Intel\s+Arc\s+\w+|Intel\s+Iris\s+Xe|AMD\s+Radeon\s+\w+)\b",
                title,
                re.IGNORECASE,
            )
            if gpu_match:
                attributes["gpu_model"] = gpu_match.group(1).strip()
            elif "apple" in title.casefold() or "macbook" in title.casefold():
                m_chip = attributes.get("cpu_model")
                if m_chip and re.search(r"M[1-5]", str(m_chip), re.IGNORECASE):
                    attributes["gpu_model"] = f"{m_chip} GPU"
                else:
                    attributes["gpu_model"] = "Apple Integrated GPU"

        # Extract Screen Size
        for sc_key in (
            "screen size",
            "display size",
            "screen size (in cm)",
            "screen size (in inches)",
            "screen dimensions",
        ):
            if sc_key in norm_specs:
                with contextlib.suppress(ValueError):
                    sc_match = re.search(r"(\d+(?:\.\d+)?)", norm_specs[sc_key])
                    if sc_match:
                        attributes["screen_size_inches"] = float(sc_match.group(1))
                        break
        if "screen_size_inches" not in attributes:
            sc_match = re.search(r"(\d{2}(?:\.\d{1,2})?)\s*(?:inch|inches|\"|-inch)", title, re.I)
            if sc_match:
                with contextlib.suppress(ValueError):
                    attributes["screen_size_inches"] = float(sc_match.group(1))

    return attributes
