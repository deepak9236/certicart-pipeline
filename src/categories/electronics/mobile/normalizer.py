"""Domain-specific identity normalizer for smartphone/mobile products."""

from __future__ import annotations

import contextlib
import re
from typing import TYPE_CHECKING, ClassVar

from categories.contracts import AttributeValue

if TYPE_CHECKING:
    from matching.fingerprint import ProductFingerprint


class MobileIdentityNormalizer:
    """Extracts structured canonical identity from retailer smartphone titles."""

    KNOWN_BRANDS: ClassVar[tuple[str, ...]] = (
        "apple",
        "samsung",
        "oneplus",
        "xiaomi",
        "redmi",
        "poco",
        "realme",
        "vivo",
        "iqoo",
        "oppo",
        "google",
        "motorola",
        "nothing",
        "cmf",
        "infinix",
        "tecno",
        "lava",
        "honor",
        "asus",
        "nokia",
    )

    BRAND_ALIASES: ClassVar[dict[str, str]] = {
        "apple inc": "apple",
        "samsung electronics": "samsung",
        "google pixel": "google",
        "moto": "motorola",
        "nothing phone": "nothing",
        "redmi by xiaomi": "redmi",
        "poco by xiaomi": "poco",
    }

    PRODUCT_FAMILIES: ClassVar[tuple[tuple[str, str], ...]] = (
        (r"iphone\s+1[1-9]\s+pro\s+max", "iphone pro max"),
        (r"iphone\s+1[1-9]\s+pro", "iphone pro"),
        (r"iphone\s+1[1-9]\s+plus", "iphone plus"),
        (r"iphone\s+1[1-9]e?", "iphone"),
        (r"iphone\s+air", "iphone air"),
        (r"iphone\s+se\s*\d*", "iphone se"),
        (r"galaxy\s+s2[0-6]\s+ultra", "galaxy s ultra"),
        (r"galaxy\s+s2[0-6]\s+plus", "galaxy s plus"),
        (r"galaxy\s+s2[0-6]\s+fe", "galaxy s fe"),
        (r"galaxy\s+s2[0-6]", "galaxy s"),
        (r"galaxy\s+z\s+fold\s*\d*", "galaxy z fold"),
        (r"galaxy\s+z\s+flip\s*\d*", "galaxy z flip"),
        (r"galaxy\s+a\d{2}", "galaxy a"),
        (r"galaxy\s+m\d{2}", "galaxy m"),
        (r"galaxy\s+f\d{2}", "galaxy f"),
        (r"pixel\s+[6-9]\s+pro", "pixel pro"),
        (r"pixel\s+[6-9]\s+a", "pixel a"),
        (r"pixel\s+[6-9]", "pixel"),
        (r"oneplus\s+1[1-4]r", "oneplus r"),
        (r"oneplus\s+1[1-4]", "oneplus number"),
        (r"oneplus\s+nord\s+ce\s*\d*", "oneplus nord ce"),
        (r"oneplus\s+nord\s*\d*", "oneplus nord"),
        (r"oneplus\s+open", "oneplus open"),
        (r"redmi\s+note\s+\d+\s+pro\+?", "redmi note pro"),
        (r"redmi\s+note\s+\d+", "redmi note"),
        (r"redmi\s+turbo\s+\d+", "redmi turbo"),
        (r"redmi\s+a\d+\s+pro", "redmi a pro"),
        (r"redmi\s+a\d+", "redmi a"),
        (r"redmi\s+k\d+", "redmi k"),
        (r"redmi\s+\d+[a-z]*", "redmi number"),
        (r"realme\s+gt\s+\d+", "realme gt"),
        (r"realme\s+narzo\s+\d+\s*(?:pro|lite|speed)?", "realme narzo"),
        (r"realme\s+p\d+[a-z]*\s*(?:pro|lite)?", "realme p"),
        (r"realme\s+\d+\s+pro\+?", "realme number pro"),
        (r"realme\s+\d+[a-z]*", "realme number"),
        (r"poco\s+f\d+\s+pro", "poco f pro"),
        (r"poco\s+f\d+", "poco f"),
        (r"poco\s+x\d+\s+pro", "poco x pro"),
        (r"poco\s+x\d+", "poco x"),
        (r"poco\s+m\d+\s*(?:pro|power)?", "poco m"),
        (r"poco\s+c\d+[a-z]*", "poco c"),
        (r"iqoo\s+1[1-9]r?", "iqoo number"),
        (r"iqoo\s+neo\s*\d*", "iqoo neo"),
        (r"iqoo\s+z\d*", "iqoo z"),
        (r"vivo\s+x\d+t?\s*pro\+?", "vivo x pro"),
        (r"vivo\s+x\d+t?", "vivo x"),
        (r"vivo\s+v\d+\s*pro\+?", "vivo v pro"),
        (r"vivo\s+v\d+", "vivo v"),
        (r"vivo\s+t\d+", "vivo t"),
        (r"vivo\s+y\d+", "vivo y"),
        (r"nothing\s+phone\s*\([123a]+\)", "nothing phone"),
        (r"cmf\s+phone\s*\d*", "cmf phone"),
        (r"motorola\s+edge\s+\d+\s*pro", "motorola edge pro"),
        (r"motorola\s+edge\s+\d+\s*(?:fusion|ultra)?", "motorola edge"),
        (r"motorola\s+g\d+\s*(?:power)?", "moto g"),
        (r"moto\s+g\d+\s*(?:power)?", "moto g"),
    )

    @classmethod
    def extract_brand(cls, title: str, specs_brand: str | None = None) -> str:
        if specs_brand:
            clean_specs = specs_brand.strip().casefold()
            clean_specs = cls.BRAND_ALIASES.get(clean_specs, clean_specs)
            if clean_specs in cls.KNOWN_BRANDS:
                return clean_specs

        title_lower = title.casefold()
        for alias, canonical in cls.BRAND_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", title_lower):
                return canonical
        for brand in cls.KNOWN_BRANDS:
            if re.search(rf"\b{re.escape(brand)}\b", title_lower):
                return brand
        return title.split()[0].casefold() if title.split() else "unknown"

    @classmethod
    def extract_family(cls, title: str, model_name: str = "") -> str | None:
        combined = f"{model_name} {title}".casefold()
        for pattern, canonical in cls.PRODUCT_FAMILIES:
            if re.search(pattern, combined):
                return canonical
        return None

    @classmethod
    def extract_ram_gb(cls, title: str, specs: dict[str, str] | None = None) -> int | None:
        title_lower = title.casefold()
        matches = re.findall(r"\b([2468]|12|16|24)\s*gb(?:\s+ram)?\b", title_lower)
        for m in matches:
            val = int(m)
            if val in (2, 3, 4, 6, 8, 12, 16, 24):
                return val

        if specs and "ram" in specs:
            val_match = re.search(r"(\d+)\s*gb", specs["ram"].casefold())
            if val_match:
                return int(val_match.group(1))

        return None

    @classmethod
    def extract_storage_gb(cls, title: str, specs: dict[str, str] | None = None) -> int | None:
        title_lower = title.casefold()

        # Terabyte check
        if "1tb" in title_lower or "1 tb" in title_lower:
            return 1024

        # Gigabyte check
        matches = re.findall(r"\b(32|64|128|256|512)\s*gb(?:\s+(?:rom|storage))?\b", title_lower)
        for m in matches:
            val = int(m)
            if val in (32, 64, 128, 256, 512):
                return val

        if specs and "storage" in specs:
            clean_s = specs["storage"].casefold()
            if "1tb" in clean_s or "1 tb" in clean_s:
                return 1024
            gb_m = re.search(r"(\d+)\s*gb", clean_s)
            if gb_m:
                return int(gb_m.group(1))

        return None

    @classmethod
    def extract_chipset(cls, title: str, specs: dict[str, str] | None = None) -> str | None:
        title_lower = title.casefold()

        # Apple A-series
        apple_a = re.search(r"\b(a1[4-9](?:\s+pro)?(?:\s+bionic)?)\b", title_lower)
        if apple_a:
            return apple_a.group(1).strip()

        # Snapdragon
        snapdragon = re.search(
            r"\b(snapdragon\s+(?:8\s+gen\s+[1-5]|7\s+gen\s+[1-4]|6s?\s+gen\s+\d|4\s+gen\s+\d|8[5-8]\d|7\d{2}[a-z]?|\d{3,4}))\b",
            title_lower,
        )
        if snapdragon:
            return snapdragon.group(1).strip()

        # MediaTek Dimensity
        dimensity = re.search(
            r"\b(dimensity\s+(?:9\d{3}|8\d{3}|7\d{3}|6\d{3}|[1-9]\d{2}[a-z]?))\b",
            title_lower,
        )
        if dimensity:
            return dimensity.group(1).strip()

        # Google Tensor
        tensor = re.search(r"\b(tensor\s+g[1-5])\b", title_lower)
        if tensor:
            return tensor.group(1).strip()

        # Unisoc
        unisoc = re.search(r"\b(unisoc\s+(?:t\d{3,4}|octa-core|\w+))\b", title_lower)
        if unisoc:
            return unisoc.group(1).strip()

        if specs and "processor" in specs:
            return specs["processor"].casefold().strip()

        return None

    @classmethod
    def extract_color(cls, title: str) -> str | None:
        title_lower = title.casefold()
        colors = (
            "desert titanium",
            "natural titanium",
            "white titanium",
            "black titanium",
            "titanium gray",
            "titanium black",
            "phantom black",
            "marble gray",
            "cobalt violet",
            "amber yellow",
            "onyx black",
            "obsidian",
            "porcelain",
            "hazel",
            "bay",
            "rose",
            "midnight",
            "starlight",
            "space black",
            "space gray",
            "emerald green",
            "silver",
            "gold",
            "black",
            "blue",
            "green",
            "purple",
            "pink",
            "white",
            "yellow",
        )
        for c in colors:
            if re.search(rf"\b{re.escape(c)}\b", title_lower):
                return c.title()
        return None

    @classmethod
    def extract_screen_size_inches(
        cls, title: str, specs: dict[str, str] | None = None
    ) -> float | None:
        title_lower = title.casefold()
        # Look for e.g. 6.9in, 6.72", 6.1″, 6.5-inch
        m = re.search(r"\b([2-7](?:\.[0-9]{1,2})?)\s*(?:in|inch|inches|\"|″|-inch)\b", title_lower)
        if m:
            with contextlib.suppress(ValueError):
                return float(m.group(1))

        if specs:
            for k in ("screen size", "display size", "display size (in inches)"):
                if k in specs:
                    m = re.search(r"([2-7](?:\.[0-9]{1,2})?)", specs[k])
                    if m:
                        with contextlib.suppress(ValueError):
                            return float(m.group(1))
        return None

    @classmethod
    def extract_display_type(cls, title: str, specs: dict[str, str] | None = None) -> str | None:
        title_lower = title.casefold()
        if "super retina xdr" in title_lower or (specs and "super retina" in str(specs).casefold()):
            return "Super Retina XDR"
        if "amoled" in title_lower:
            return "AMOLED"
        if "oled" in title_lower:
            return "OLED"
        if "fhd+ ips" in title_lower or "ips" in title_lower:
            return "IPS LCD"
        if "hd+" in title_lower:
            return "HD+ Display"
        return None

    @classmethod
    def extract_refresh_rate_hz(cls, title: str, specs: dict[str, str] | None = None) -> int | None:
        title_lower = title.casefold()
        m = re.search(r"\b(60|90|120|144|165)\s*hz\b", title_lower)
        if m:
            with contextlib.suppress(ValueError):
                return int(m.group(1))
        if specs and "refresh rate" in specs:
            m = re.search(r"\b(60|90|120|144|165)\b", specs["refresh rate"])
            if m:
                with contextlib.suppress(ValueError):
                    return int(m.group(1))
        return None

    @classmethod
    def extract_primary_camera_mp(
        cls, title: str, specs: dict[str, str] | None = None
    ) -> int | None:
        title_lower = title.casefold()
        m = re.search(r"\b(200|108|64|50|48|32|13|12|8|5)\s*mp\b", title_lower)
        if m:
            with contextlib.suppress(ValueError):
                return int(m.group(1))
        if specs:
            for k in ("primary camera", "rear camera", "camera"):
                if k in specs:
                    m = re.search(r"\b(200|108|64|50|48|32|13|12|8|5)\b", specs[k])
                    if m:
                        with contextlib.suppress(ValueError):
                            return int(m.group(1))
        return None

    @classmethod
    def extract_battery_mah(cls, title: str, specs: dict[str, str] | None = None) -> int | None:
        title_lower = title.casefold()
        m = re.search(r"\b([1-9][0-9]{3})\s*mah\b", title_lower)
        if m:
            with contextlib.suppress(ValueError):
                return int(m.group(1))
        if specs and "battery capacity" in specs:
            m = re.search(r"\b([1-9][0-9]{3})\b", specs["battery capacity"])
            if m:
                with contextlib.suppress(ValueError):
                    return int(m.group(1))
        return None

    @classmethod
    def extract_fast_charging_w(cls, title: str, specs: dict[str, str] | None = None) -> int | None:
        title_lower = title.casefold()
        m = re.search(
            r"\b(\d{2,3})\s*w\s*(?:hypercharge|turbopower|fast|charging|supervooc)?\b", title_lower
        )
        if m:
            with contextlib.suppress(ValueError):
                return int(m.group(1))
        return None

    @classmethod
    def extract_operating_system(
        cls, title: str, specs: dict[str, str] | None = None
    ) -> str | None:
        title_lower = title.casefold()
        if "iphone" in title_lower or "apple" in title_lower:
            return "iOS"
        if "android" in title_lower:
            return "Android"
        if specs and "operating system" in specs:
            return specs["operating system"].strip()
        return "Android"

    @classmethod
    def extract_resolution_standard(
        cls, title: str, specs: dict[str, str] | None = None
    ) -> str | None:
        title_lower = title.casefold()
        if "4k" in title_lower:
            return "4K UHD"
        if "qhd+" in title_lower or "2k" in title_lower:
            return "QHD+"
        if "1.5k" in title_lower:
            return "1.5K"
        if "fhd+" in title_lower or "full hd+" in title_lower:
            return "FHD+"
        if "hd+" in title_lower:
            return "HD+"
        if specs and "resolution" in specs:
            r = specs["resolution"].casefold()
            if "3840" in r:
                return "4K UHD"
            if "2560" in r or "3120" in r:
                return "QHD+"
            if "2400" in r or "1080" in r:
                return "FHD+"
            if "720" in r:
                return "HD+"
        return None

    @classmethod
    def extract_camera_setup(cls, title: str, specs: dict[str, str] | None = None) -> str | None:
        title_lower = title.casefold()
        if "quad camera" in title_lower:
            return "Quad Camera"
        if "triple camera" in title_lower:
            return "Triple Camera"
        if "dual camera" in title_lower:
            return "Dual Camera"
        if specs and "camera" in specs:
            c = specs["camera"].casefold()
            if "quad" in c or c.count("+") >= 3:
                return "Quad Camera"
            if "triple" in c or c.count("+") == 2:
                return "Triple Camera"
            if "dual" in c or c.count("+") == 1:
                return "Dual Camera"
        return None

    @classmethod
    def extract_water_resistance(
        cls, title: str, specs: dict[str, str] | None = None
    ) -> str | None:
        title_lower = title.casefold()
        m = re.search(r"\b(ip6[89]|ip6[57]|ip5[45]|ip53)\b", title_lower)
        if m:
            return m.group(1).upper()
        if specs and "water resistance" in specs:
            m = re.search(
                r"\b(ip6[89]|ip6[57]|ip5[45]|ip53)\b", specs["water resistance"].casefold()
            )
            if m:
                return m.group(1).upper()
        return None

    @classmethod
    def extract_screen_protection(
        cls, title: str, specs: dict[str, str] | None = None
    ) -> str | None:
        title_lower = title.casefold()
        if "ceramic shield" in title_lower or "iphone" in title_lower:
            return "Ceramic Shield"
        if "victus 2" in title_lower or (specs and "victus 2" in str(specs).casefold()):
            return "Gorilla Glass Victus 2"
        if "victus" in title_lower or (specs and "victus" in str(specs).casefold()):
            return "Gorilla Glass Victus"
        if "gorilla glass" in title_lower or (specs and "gorilla glass" in str(specs).casefold()):
            return "Gorilla Glass"
        return None

    @classmethod
    def normalize(
        cls,
        title: str,
        *,
        category: str = "mobile",
        brand_raw: str | None = None,
        model_name_raw: str | None = None,
        specs: dict[str, str] | None = None,
        manufacturer_part_number: str | None = None,
        gtin: str | None = None,
        extra_attributes: dict[str, AttributeValue] | None = None,
    ) -> ProductFingerprint:
        """Construct structured canonical ProductFingerprint for smartphone product."""
        from categories.electronics.mobile.schemas import MobileAttributes

        brand = cls.extract_brand(title, brand_raw)
        family = cls.extract_family(title, model_name_raw or "")
        ram_gb = cls.extract_ram_gb(title, specs)
        storage_gb = cls.extract_storage_gb(title, specs)
        chipset = cls.extract_chipset(title, specs)
        color = cls.extract_color(title)
        network_type = "5G" if "5g" in title.casefold() else "4G"
        screen_size = cls.extract_screen_size_inches(title, specs)
        display_type = cls.extract_display_type(title, specs)
        refresh_rate = cls.extract_refresh_rate_hz(title, specs)
        primary_camera = cls.extract_primary_camera_mp(title, specs)
        battery = cls.extract_battery_mah(title, specs)
        charging = cls.extract_fast_charging_w(title, specs)
        os_name = cls.extract_operating_system(title, specs)
        resolution = cls.extract_resolution_standard(title, specs)
        camera_setup = cls.extract_camera_setup(title, specs)
        water_resistance = cls.extract_water_resistance(title, specs)
        screen_protection = cls.extract_screen_protection(title, specs)
        ois_supported = (
            True
            if "ois" in title.casefold() or (specs and "ois" in str(specs).casefold())
            else None
        )

        if extra_attributes and "ram_gb" in extra_attributes:
            with contextlib.suppress(ValueError):
                ram_gb = int(str(extra_attributes["ram_gb"]))
        if extra_attributes and "storage_gb" in extra_attributes:
            with contextlib.suppress(ValueError):
                storage_gb = int(str(extra_attributes["storage_gb"]))

        # Build clean model name: [Brand] [Family/Model] [Storage] [Color]
        parts = [brand.capitalize()]
        if family:
            clean_fam = family
            if clean_fam.lower().startswith(brand.lower()):
                clean_fam = clean_fam[len(brand) :].strip()
            parts.append(clean_fam.title())
        elif model_name_raw and len(model_name_raw) <= 30 and model_name_raw != title:
            parts.append(model_name_raw.title())
        else:
            short_model = re.split(r"\(|\d+\s*gb|\||:", title, flags=re.IGNORECASE)[0].strip()
            if short_model:
                short_model = re.sub(
                    rf"^{re.escape(brand)}\s+", "", short_model, flags=re.IGNORECASE
                ).strip()
                if len(short_model) <= 35:
                    parts.append(short_model.title())

        if ram_gb and storage_gb:
            parts.append(f"({ram_gb}GB / {storage_gb}GB)")
        elif storage_gb:
            parts.append(f"({storage_gb}GB)")
        if color:
            parts.append(color)

        clean_model_name = " ".join(p for p in parts if p).strip()
        clean_model_name = re.sub(
            r"\b(\w+)\s+\1\b", r"\1", clean_model_name, flags=re.IGNORECASE
        ).strip()

        # Build and validate through MobileAttributes Pydantic schema
        extra = dict(extra_attributes or {})
        for explicit_k in (
            "ram_gb",
            "storage_gb",
            "chipset",
            "color",
            "network_type",
            "screen_size_inches",
            "display_type",
            "refresh_rate_hz",
            "primary_camera_mp",
            "battery_mah",
            "fast_charging_w",
            "operating_system",
            "resolution_standard",
            "camera_setup",
            "water_resistance_rating",
            "screen_protection",
            "ois_supported",
            "mpn",
            "gtin",
            "asin",
            "ean",
        ):
            extra.pop(explicit_k, None)

        mobile_schema = MobileAttributes(
            ram_gb=ram_gb,
            storage_gb=storage_gb,
            chipset=chipset,
            color=color,
            network_type=network_type,
            screen_size_inches=screen_size,
            display_type=display_type,
            refresh_rate_hz=refresh_rate,
            primary_camera_mp=primary_camera,
            battery_mah=battery,
            fast_charging_w=charging,
            operating_system=os_name,
            resolution_standard=resolution,
            camera_setup=camera_setup,
            water_resistance_rating=water_resistance,
            screen_protection=screen_protection,
            ois_supported=ois_supported,
            mpn=manufacturer_part_number,
            gtin=gtin,
            **extra,
        )
        attributes = mobile_schema.to_attribute_dict()

        from matching.fingerprint import ProductFingerprint

        return ProductFingerprint(
            category=category,
            brand=brand,
            family=family,
            model_name=clean_model_name,
            chip=chipset,
            ram_gb=ram_gb,
            storage_gb=storage_gb,
            screen_size_inches=screen_size,
            manufacturer_part_number=manufacturer_part_number,
            gtin=gtin,
            attributes=attributes,
        )
