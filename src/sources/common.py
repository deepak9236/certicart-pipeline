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
        if (
            "processor name" in norm_specs
            or "cpu model" in norm_specs
            or "processor type" in norm_specs
        ):
            p_name = (
                norm_specs.get("processor name")
                or norm_specs.get("cpu model")
                or norm_specs.get("processor type", "")
            )
            p_var = norm_specs.get("processor variant", "")
            p_brand = norm_specs.get("processor brand", "")
            full_cpu = f"{p_name} {p_var}".strip()
            if p_brand and p_brand.lower() not in full_cpu.lower():
                full_cpu = f"{p_brand} {full_cpu}".strip()
            attributes["cpu_model"] = full_cpu
        else:
            for cpu_key in (
                "processor type",
                "processor",
                "cpu",
                "processor variant",
                "processor brand",
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
            "gpu model",
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
            "display size (in inches)",
            "screen size (in inches)",
            "screen size (in cm)",
            "display size (in cms)",
            "screen dimensions",
        ):
            if sc_key in norm_specs:
                raw_sc = norm_specs[sc_key]
                inch_m = re.search(r"(\d{2}(?:\.\d{1,2})?)\s*(?:inch|inches|\")", raw_sc, re.I)
                if inch_m:
                    with contextlib.suppress(ValueError):
                        attributes["screen_size_inches"] = float(inch_m.group(1))
                        break
                num_m = re.search(r"(\d+(?:\.\d+)?)", raw_sc)
                if num_m:
                    with contextlib.suppress(ValueError):
                        val = float(num_m.group(1))
                        if val > 25.0:
                            val = round(val / 2.54, 1)
                        if 9.0 <= val <= 24.0:
                            attributes["screen_size_inches"] = val
                            break
        if "screen_size_inches" not in attributes:
            sc_match = re.search(r"(\d{2}(?:\.\d{1,2})?)\s*(?:inch|inches|\"|-inch)", title, re.I)
            if sc_match:
                with contextlib.suppress(ValueError):
                    attributes["screen_size_inches"] = float(sc_match.group(1))

        # Additional Laptop fields
        for rt_key in ("ram type", "type of ram", "memory technology"):
            if rt_key in norm_specs:
                attributes["ram_type"] = norm_specs[rt_key].upper()
                break

        if "operating system" in norm_specs:
            attributes["operating_system"] = norm_specs["operating system"].strip()
        elif "os" in norm_specs:
            attributes["operating_system"] = norm_specs["os"].strip()

        if "brand color" in norm_specs:
            attributes["color"] = norm_specs["brand color"].strip()
        elif "color" in norm_specs:
            attributes["color"] = norm_specs["color"].strip()

        if "display type" in norm_specs:
            dt_val = norm_specs["display type"].lower()
            if "oled" in dt_val:
                attributes["display_type"] = "OLED"
            elif "ips" in dt_val:
                attributes["display_type"] = "IPS LCD"

        if "backlit keyboard" in norm_specs:
            b_val = norm_specs["backlit keyboard"].lower()
            if b_val in ("yes", "true", "1"):
                attributes["keyboard_backlight"] = True
            elif b_val in ("no", "false", "0"):
                attributes["keyboard_backlight"] = False
        elif (
            "type of keyboard" in norm_specs and "backlit" in norm_specs["type of keyboard"].lower()
        ) or ("keyboard" in norm_specs and "backlit" in norm_specs["keyboard"].lower()):
            attributes["keyboard_backlight"] = True

        for cam_key in (
            "web camera",
            "camera resolution",
            "camera",
            "webcam",
            "laptop camera type",
        ):
            if cam_key in norm_specs:
                w_val = norm_specs[cam_key].lower()
                if "1080p" in w_val or "fhd" in w_val:
                    attributes["webcam_resolution"] = "1080p FHD"
                    break
                elif "720p" in w_val or "hd" in w_val:
                    attributes["webcam_resolution"] = "720p HD"
                    break

        for w_key in ("weight", "product weight", "item weight"):
            if w_key in norm_specs:
                w_m = re.search(r"(\d+(?:\.\d+)?)\s*kg", norm_specs[w_key].lower())
                if w_m:
                    with contextlib.suppress(ValueError):
                        weight_float = float(w_m.group(1))
                        if 0.5 <= weight_float <= 10.0:
                            attributes["weight_kg"] = weight_float
                            break

        for b_key in (
            "battery cell",
            "battery",
            "battery capacity",
            "standard battery life",
            "laptop battery",
        ):
            if b_key in norm_specs:
                b_m = re.search(
                    r"(\d{2,3}(?:\.\d)?)\s*(?:wh|watt\s*hours)", norm_specs[b_key].lower()
                )
                if b_m:
                    with contextlib.suppress(ValueError):
                        battery_wh_float = float(b_m.group(1))
                        if 10.0 <= battery_wh_float <= 150.0:
                            attributes["battery_wh"] = battery_wh_float
                            break

        for wlan_key in (
            "wireless lan",
            "wifi specifications",
            "wi-fi specifications",
            "network connectivity",
        ):
            if wlan_key in norm_specs:
                w_lan = norm_specs[wlan_key].lower()
                if "wi-fi 7" in w_lan or "wifi 7" in w_lan:
                    attributes["wifi_standard"] = "Wi-Fi 7"
                    break
                elif "wi-fi 6e" in w_lan or "wifi 6e" in w_lan:
                    attributes["wifi_standard"] = "Wi-Fi 6E"
                    break
                elif "wi-fi 6" in w_lan or "wifi 6" in w_lan:
                    attributes["wifi_standard"] = "Wi-Fi 6"
                    break
                elif "wi-fi 5" in w_lan or "wifi 5" in w_lan or "802.11ac" in w_lan:
                    attributes["wifi_standard"] = "Wi-Fi 5"
                    break

        for res_key in (
            "screen resolution",
            "screen resolution type",
            "display resolution",
            "additional screen specifications",
        ):
            if res_key in norm_specs:
                r_val = norm_specs[res_key].lower()
                if "4k" in r_val or "3840" in r_val:
                    attributes["display_resolution"] = "4K UHD"
                    break
                if "2.8k" in r_val or "2880" in r_val:
                    attributes["display_resolution"] = "2.8K"
                    break
                if "2.5k" in r_val or "2560" in r_val:
                    attributes["display_resolution"] = "2.5K QHD"
                    break
                if "wuxga" in r_val or "1920 x 1200" in r_val or "1920x1200" in r_val:
                    attributes["display_resolution"] = "WUXGA"
                    break
                if "1080" in r_val or "fhd" in r_val or "full hd" in r_val:
                    attributes["display_resolution"] = "FHD"
                    break

        if "model number" in norm_specs:
            attributes["model_number"] = norm_specs["model number"].strip()
        elif "model name" in norm_specs:
            attributes["model_number"] = norm_specs["model name"].strip()

        if "part number" in norm_specs:
            attributes["mpn"] = norm_specs["part number"].strip()

    # Mobile category extraction
    elif category.casefold() in ("mobile", "smartphone", "phone"):
        for ram_key in ("ram", "ram capacity", "internal memory"):
            if ram_key in norm_specs:
                with contextlib.suppress(ValueError):
                    attributes["ram_gb"] = normalize_capacity_gb(
                        clean_capacity_str(norm_specs[ram_key])
                    )
                    break
        for st_key in ("storage", "internal storage", "rom", "storage capacity"):
            if st_key in norm_specs:
                with contextlib.suppress(ValueError):
                    attributes["storage_gb"] = normalize_capacity_gb(
                        clean_capacity_str(norm_specs[st_key])
                    )
                    break
        for proc_key in ("processor", "processor type", "chipset", "processor name"):
            if proc_key in norm_specs:
                attributes["chipset"] = norm_specs[proc_key].strip()
                break
        if "color" in norm_specs:
            attributes["color"] = norm_specs["color"].strip()
        if "battery capacity" in norm_specs or "battery" in norm_specs:
            b_text = norm_specs.get("battery capacity") or norm_specs.get("battery", "")
            b_m = re.search(r"(\d{3,5})\s*mah", b_text.lower())
            if b_m:
                with contextlib.suppress(ValueError):
                    attributes["battery_mah"] = int(b_m.group(1))
        for cam_key in ("primary camera", "rear camera", "main camera"):
            if cam_key in norm_specs:
                c_m = re.search(r"(\d{1,3})\s*mp", norm_specs[cam_key].lower())
                if c_m:
                    with contextlib.suppress(ValueError):
                        attributes["primary_camera_mp"] = int(c_m.group(1))
                        break
        for sc_key in ("screen size", "display size"):
            if sc_key in norm_specs:
                sc_m = re.search(r"(\d+(?:\.\d+)?)", norm_specs[sc_key])
                if sc_m:
                    with contextlib.suppress(ValueError):
                        val = float(sc_m.group(1))
                        if 1.5 <= val <= 8.5:
                            attributes["screen_size_inches"] = val
                            break

    return attributes
