"""Curated ground-truth dataset for stress-testing product matching precision and recall.

Contains 55+ cross-retailer test pairs categorized into positive, adversarial negative,
and ambiguous review-required cases.
"""

# 1. POSITIVE CROSS-RETAILER PAIRS (Identical Product Variant from Different Retailers)
POSITIVE_PAIRS: list[tuple[str, str, str]] = [
    # Apple
    (
        (
            "Apple 2026 MacBook Air 15″ Laptop with M5 chip: AI and Apple Intelligence, "
            "15.3-inch Liquid Retina Display, 16GB Unified Memory, 512GB SSD Storage"
        ),
        ("Apple Macbook Air (M5, 2026) M5 - (16 GB/512 GB SSD/macOS) 15-inch Space Grey"),
        "Apple MacBook Air M5 16/512 15-inch",
    ),
    (
        "Apple 2024 MacBook Air 13″ Laptop with M3 chip, 8GB RAM, 256GB SSD, Midnight",
        "Apple MacBook Air M3 - (8 GB/256 GB SSD/macOS Sonoma) 13.6 Inch Midnight",
        "Apple MacBook Air M3 8/256 13.6-inch",
    ),
    (
        (
            "Apple MacBook Pro 16″ (M3 Pro chip, 18GB Unified Memory, 512GB SSD) "
            "Space Black (Late 2023)"
        ),
        "Apple MacBook Pro M3 Pro - (18 GB/512 GB SSD/macOS Sonoma) 16.2 inch Space Black",
        "Apple MacBook Pro 16 M3 Pro 18/512",
    ),
    # HP
    (
        (
            "HP Victus, 13th Gen Intel Core i5-13420H, 6GB RTX 3050, 16GB DDR4, "
            "512GB SSD, FHD IPS 144Hz Gaming Laptop (15-fa1145TX)"
        ),
        (
            "HP Victus Gaming (13th Gen) Intel Core i5 13420H - "
            "(16 GB/512 GB SSD/Windows 11 Home/6 GB Graphics/NVIDIA GeForce RTX 3050)"
        ),
        "HP Victus i5-13420H 16/512 RTX 3050",
    ),
    (
        (
            "HP 15s, 12th Gen Intel Core i3-1215U, 8GB DDR4, 512GB SSD, "
            "15.6-inch (39.6 cm) FHD, Anti-Glare, Windows 11 Home (15s-fq5007TU)"
        ),
        "HP 15s Intel Core i3 12th Gen 1215U - (8 GB/512 GB SSD/Windows 11 Home)",
        "HP 15s i3-1215U 8/512",
    ),
    (
        (
            "HP Pavilion Plus 14, AMD Ryzen 7 7840H, 16GB LPDDR5x, 1TB SSD, "
            "14-inch (35.6 cm) 2.8K OLED Display (14-ey0024AU)"
        ),
        (
            "HP Pavilion Plus AMD Ryzen 7 Octa Core 7840H - "
            "(16 GB/1 TB SSD/Windows 11 Home/14 inch 2.8K OLED)"
        ),
        "HP Pavilion Plus Ryzen 7 7840H 16/1TB",
    ),
    (
        (
            "HP OmniBook 5 OLED, Snapdragon X Plus Processor "
            "(16GB LPDDR5x, 512GB SSD, 14-inch 2.2K OLED)"
        ),
        ("HP Omnibook Snapdragon X Plus - (16 GB/512 GB SSD/Windows 11 Home/14 inch OLED)"),
        "HP OmniBook Snapdragon X 16/512",
    ),
    # ASUS
    (
        (
            "ASUS Vivobook 15 (2026) Intel Core 5 120U - "
            "(8 GB/512 GB SSD/Windows 11 Home) Thin and Light Laptop"
        ),
        (
            "ASUS Vivobook 15, Intel Core 5 120U, 15.6-inch FHD, 8GB RAM, "
            "512GB SSD, Windows 11 Home, Quiet Blue"
        ),
        "ASUS Vivobook 15 Core 5 120U 8/512",
    ),
    (
        (
            "ASUS TUF Gaming A15 (2025), AMD Ryzen 7 7445HS, 16GB DDR5, "
            "512GB SSD, RTX 3050, 15.6-inch 144Hz"
        ),
        ("ASUS TUF Gaming A15 AMD Ryzen 7 7445HS - (16 GB/512 GB SSD/Windows 11 Home/RTX 3050)"),
        "ASUS TUF A15 Ryzen 7 7445HS 16/512",
    ),
    (
        (
            'ASUS ROG Strix G16 (2024), 16" FHD+ 165Hz, Intel Core i7-13650HX, '
            "NVIDIA GeForce RTX 4060, 16GB DDR5, 1TB PCIe SSD (G614JV-AS74)"
        ),
        (
            "ASUS ROG Strix G16 Intel Core i7 13th Gen 13650HX - "
            "(16 GB/1 TB SSD/Windows 11 Home/8 GB Graphics/NVIDIA GeForce RTX 4060)"
        ),
        "ASUS ROG Strix G16 i7-13650HX 16/1TB RTX 4060",
    ),
    (
        (
            "ASUS Zenbook 14 OLED, Intel Core Ultra 7 155H, Built-in AI, "
            '14" (35.56 cm) 3K OLED, 16GB LPDDR5X, 1TB SSD (UX3405MA)'
        ),
        (
            "ASUS Zenbook 14 OLED Intel Core Ultra 7 155H - "
            "(16 GB/1 TB SSD/Windows 11 Home/14 inch 3K OLED)"
        ),
        "ASUS Zenbook 14 OLED Core Ultra 7 16/1TB",
    ),
    # Lenovo
    (
        (
            'Lenovo LOQ Intel Core i7-13650HX 15.6" (39.6cm) 144Hz 300Nits Gaming Laptop '
            "(16GB/512GB SSD/Win 11/NVIDIA RTX 3050 6GB)"
        ),
        (
            "Lenovo LOQ Intel Core i7 13th Gen 13650HX - "
            "(16 GB/512 GB SSD/Windows 11 Home/6 GB Graphics/NVIDIA GeForce RTX 3050)"
        ),
        "Lenovo LOQ i7-13650HX 16/512 RTX 3050",
    ),
    (
        (
            "Lenovo IdeaPad Slim 3 13th Gen Intel Core i5-13420H 15.3 inch "
            "(16GB/512GB SSD/Win 11/MSO)"
        ),
        (
            "Lenovo IdeaPad Slim 3 Intel Core i5 13th Gen 13420H - "
            "(16 GB/512 GB SSD/Windows 11 Home)"
        ),
        "Lenovo IdeaPad Slim 3 i5-13420H 16/512",
    ),
    (
        (
            'Lenovo IdeaPad Slim 1 AMD Ryzen 3 7320U 15.6" HD Thin and Light Laptop '
            "(8GB/512GB SSD/Windows 11 Home/Cloud Grey/1.58Kg)"
        ),
        "Lenovo IdeaPad 1 AMD Ryzen 3 Quad Core 7320U - (8 GB/512 GB SSD/Windows 11 Home)",
        "Lenovo IdeaPad 1 Ryzen 3 7320U 8/512",
    ),
    (
        (
            'Lenovo Legion 5 Pro Intel Core i7-14650HX 16" (40.64cm) WQXGA 165Hz Gaming Laptop '
            "(16GB/1TB SSD/Win 11/RTX 4060 8GB)"
        ),
        (
            "Lenovo Legion Pro 5 Intel Core i7 14th Gen 14650HX - "
            "(16 GB/1 TB SSD/Windows 11 Home/8 GB Graphics/NVIDIA GeForce RTX 4060)"
        ),
        "Lenovo Legion 5 Pro i7-14650HX 16/1TB RTX 4060",
    ),
    (
        (
            'Lenovo ThinkBook 14 Gen 6 AMD Ryzen 7 7730U 14" (35.56 cm) WUXGA IPS Laptop '
            "(16GB/512GB SSD/Windows 11 Home/Arctic Grey/1.38 kg)"
        ),
        "Lenovo ThinkBook 14 AMD Ryzen 7 7730U - (16 GB/512 GB SSD/Windows 11 Home)",
        "Lenovo ThinkBook 14 Ryzen 7 7730U 16/512",
    ),
    # Acer
    (
        (
            "Acer Aspire Lite, 13th Gen Intel Core i3-1305U, 8GB RAM, 512GB SSD, "
            '15.6" Full HD Display, Steel Gray'
        ),
        ("Acer Aspire Lite Intel Core i3 13th Gen 1305U - (8 GB/512 GB SSD/Windows 11 Home)"),
        "Acer Aspire Lite i3-1305U 8/512",
    ),
    (
        (
            "Acer Nitro V 15 Gaming Laptop 13th Gen Intel Core i5-13420H with RTX 4050 Graphics "
            '(16GB DDR5/512GB SSD/15.6" FHD 144Hz/Win 11 Home)'
        ),
        (
            "Acer Nitro V Intel Core i5 13th Gen 13420H - "
            "(16 GB/512 GB SSD/Windows 11 Home/6 GB Graphics/NVIDIA GeForce RTX 4050)"
        ),
        "Acer Nitro V 15 i5-13420H 16/512 RTX 4050",
    ),
    (
        (
            "Acer Swift Go 14 OLED, Intel Core Ultra 5 125H Processor Laptop "
            '(16GB LPDDR5X/512GB SSD/Intel Arc Graphics/14.0" 2.8K OLED 90Hz)'
        ),
        (
            "Acer Swift Go 14 Intel Core Ultra 5 125H - "
            "(16 GB/512 GB SSD/Windows 11 Home/14 inch 2.8K OLED)"
        ),
        "Acer Swift Go 14 Core Ultra 5 16/512",
    ),
    # Dell
    (
        (
            "Dell 15 Laptop, Intel Core 13th Gen i5-1334U, 8GB DDR4, 512GB SSD, "
            "15.6\" (39.62cm) FHD, Win 11 + MSO'21"
        ),
        ("DELL Inspiron 15 Intel Core i5 13th Gen 1334U - (8 GB/512 GB SSD/Windows 11 Home)"),
        "Dell Inspiron 15 i5-1334U 8/512",
    ),
    (
        (
            "Dell Inspiron 3520 Laptop, Intel Core i3-1215U, 8GB RAM, 512GB SSD, "
            '15.6" (39.62cm) FHD 120Hz Display, Carbon Black'
        ),
        "DELL Inspiron 3520 Intel Core i3 12th Gen 1215U - (8 GB/512 GB SSD/Windows 11 Home)",
        "Dell Inspiron 3520 i3-1215U 8/512",
    ),
    (
        (
            "Dell G15-5530 Gaming Laptop, Intel Core i5-13450HX, 16GB DDR5, 1TB SSD, "
            'NVIDIA RTX 3050 6GB, 15.6" (39.62cm) FHD 120Hz'
        ),
        (
            "DELL G15 Intel Core i5 13th Gen 13450HX - "
            "(16 GB/1 TB SSD/Windows 11 Home/6 GB Graphics/NVIDIA GeForce RTX 3050)"
        ),
        "Dell G15 i5-13450HX 16/1TB RTX 3050",
    ),
    # Samsung & Primebook
    (
        (
            'Samsung Galaxy Book4 (Gray, 16GB RAM, 512GB SSD) | 15.6" Full HD | '
            "Intel Core 5 120U Processor | Windows 11 Home | MS Office 2021"
        ),
        "Samsung Galaxy Book4 Intel Core 5 120U - (16 GB/512 GB SSD/Windows 11 Home)",
        "Samsung Galaxy Book4 Core 5 120U 16/512",
    ),
    (
        (
            'Samsung Galaxy Book4 Pro 360 Intel Core Ultra 7 155H 16" Touchscreen 2-in-1 Laptop '
            "(16GB/512GB SSD/Win 11/Moonstone Gray/1.66 kg)"
        ),
        "Samsung Galaxy Book4 Pro 360 Intel Core Ultra 7 155H - (16 GB/512 GB SSD/Windows 11 Home)",
        "Samsung Galaxy Book4 Pro 360 Core Ultra 7 16/512",
    ),
    (
        (
            "Primebook 4G Android 11 Based PrimeOS Laptop, MediaTek MT8788 Processor, "
            '4GB LPDDR4 RAM, 64GB eMMC Storage, 11.6" HD Display'
        ),
        "Primebook 4G MediaTek MT8788 - (4 GB/64 GB EMMC/Prime OS) 11.6 Inch",
        "Primebook 4G MT8788 4/64",
    ),
    (
        (
            "Primebook S Wi-Fi Android 11 Based PrimeOS Laptop, MediaTek MT8183 Processor, "
            '4GB LPDDR4X RAM, 128GB eMMC Storage, 11.6" HD IPS Display'
        ),
        "Primebook S MediaTek MT8183 - (4 GB/128 GB EMMC/Prime OS)",
        "Primebook S MT8183 4/128",
    ),
]


# 2. ADVERSARIAL NEGATIVE PAIRS (Subtle Differences that MUST NEVER Match)
NEGATIVE_ADVERSARIAL_PAIRS: list[tuple[str, str, str]] = [
    # GPU Mismatches on identical chassis
    (
        "HP Victus Gaming Laptop, Intel Core i5-13420H, 16GB RAM, 512GB SSD, NVIDIA RTX 2050 4GB",
        "HP Victus Gaming Laptop, Intel Core i5-13420H, 16GB RAM, 512GB SSD, NVIDIA RTX 3050 6GB",
        "GPU conflict RTX 2050 vs RTX 3050 on HP Victus",
    ),
    (
        "ASUS TUF Gaming A15, AMD Ryzen 7 7445HS, 16GB RAM, 512GB SSD, RTX 3050 Graphics",
        "ASUS TUF Gaming A15, AMD Ryzen 7 7445HS, 16GB RAM, 512GB SSD, RTX 4050 Graphics",
        "GPU conflict RTX 3050 vs RTX 4050 on ASUS TUF",
    ),
    (
        "Lenovo LOQ Intel Core i7-13650HX 16GB 512GB RTX 3050 6GB",
        "Lenovo LOQ Intel Core i7-13650HX 16GB 512GB RTX 4060 8GB",
        "GPU conflict RTX 3050 vs RTX 4060 on Lenovo LOQ",
    ),
    (
        "Acer Nitro V 15, Intel Core i5-13420H, 16GB RAM, 512GB SSD, RTX 3050 6GB",
        "Acer Nitro V 15, Intel Core i5-13420H, 16GB RAM, 512GB SSD, RTX 4050 6GB",
        "GPU conflict RTX 3050 vs RTX 4050 on Acer Nitro V",
    ),
    # Processor Sub-SKU Mismatches
    (
        'Lenovo IdeaPad 1 AMD Ryzen 5 7520U 15.6" Laptop (16GB/512GB SSD/Windows 11)',
        'Lenovo IdeaPad 1 AMD Ryzen 5 7530U 15.6" Laptop (16GB/512GB SSD/Windows 11)',
        "Sub-SKU conflict Ryzen 5 7520U (Zen 2) vs Ryzen 5 7530U (Zen 3)",
    ),
    (
        "Dell Inspiron 15 Intel Core i5 12th Gen 1235U - (8 GB/512 GB SSD)",
        "Dell Inspiron 15 Intel Core i5 13th Gen 1335U - (8 GB/512 GB SSD)",
        "Processor Gen conflict i5-1235U vs i5-1335U on Dell Inspiron",
    ),
    (
        "Lenovo Legion 5 Pro Intel Core i7 13th Gen 13650HX 16GB 1TB RTX 4060",
        "Lenovo Legion 5 Pro Intel Core i7 14th Gen 14650HX 16GB 1TB RTX 4060",
        "Processor Gen conflict i7-13650HX vs i7-14650HX on Legion",
    ),
    (
        "ASUS Zenbook 14 OLED, Intel Core Ultra 5 125H, 16GB RAM, 1TB SSD",
        "ASUS Zenbook 14 OLED, Intel Core Ultra 7 155H, 16GB RAM, 1TB SSD",
        "Processor Tier conflict Core Ultra 5 125H vs Core Ultra 7 155H",
    ),
    (
        "Apple MacBook Pro 14″ with M3 Pro chip (18GB RAM, 512GB SSD)",
        "Apple MacBook Pro 14″ with M3 Max chip (36GB RAM, 1TB SSD)",
        "Apple Chip conflict M3 Pro vs M3 Max",
    ),
    (
        "Apple MacBook Air 13″ Laptop with M2 chip, 8GB RAM, 256GB SSD",
        "Apple MacBook Air 13″ Laptop with M3 chip, 8GB RAM, 256GB SSD",
        "Apple Chip conflict M2 vs M3 on MacBook Air",
    ),
    (
        "Apple MacBook Air 15″ Laptop with M4 chip, 16GB RAM, 512GB SSD",
        "Apple MacBook Air 15″ Laptop with M5 chip, 16GB RAM, 512GB SSD",
        "Apple Chip conflict M4 vs M5 on MacBook Air 15",
    ),
    # Product Family Mismatches
    (
        "Apple MacBook Air 15″ M5 16GB 512GB SSD",
        "Apple MacBook Pro 15″ M5 16GB 512GB SSD",
        "Family conflict MacBook Air vs MacBook Pro",
    ),
    (
        "ASUS Vivobook 15 Intel Core i5-13420H 16GB 512GB SSD",
        "ASUS Zenbook 15 Intel Core i5-13420H 16GB 512GB SSD",
        "Family conflict Vivobook vs Zenbook",
    ),
    (
        "ASUS Vivobook 15 Intel Core i5 16GB 512GB",
        "ASUS TUF Gaming 15 Intel Core i5 16GB 512GB",
        "Family conflict Vivobook vs TUF Gaming",
    ),
    (
        "HP Victus 15 Intel Core i5-13420H 16GB 512GB",
        "HP Omen 15 Intel Core i5-13420H 16GB 512GB",
        "Family conflict Victus vs Omen",
    ),
    (
        "HP Pavilion 15 Intel Core i5-1334U 16GB 512GB",
        "HP Envy 15 Intel Core i5-1334U 16GB 512GB",
        "Family conflict Pavilion vs Envy",
    ),
    (
        "Lenovo IdeaPad Slim 3 Intel Core i5-13420H 16GB 512GB",
        "Lenovo ThinkPad E14 Intel Core i5-13420H 16GB 512GB",
        "Family conflict IdeaPad vs ThinkPad",
    ),
    (
        "Lenovo LOQ Intel Core i7-13650HX 16GB 512GB RTX 3050",
        "Lenovo Legion Pro 5 Intel Core i7-13650HX 16GB 512GB RTX 3050",
        "Family conflict LOQ vs Legion",
    ),
    (
        "Dell Inspiron 15 Intel Core i5-1334U 8GB 512GB",
        "Dell Vostro 15 Intel Core i5-1334U 8GB 512GB",
        "Family conflict Inspiron vs Vostro",
    ),
    (
        "Dell Inspiron 15 Intel Core i7 16GB 512GB",
        "Dell XPS 15 Intel Core i7 16GB 512GB",
        "Family conflict Inspiron vs XPS",
    ),
    (
        "Acer Aspire 5 Intel Core i5-13420H 16GB 512GB",
        "Acer Nitro 5 Intel Core i5-13420H 16GB 512GB",
        "Family conflict Aspire vs Nitro",
    ),
    (
        "Acer Swift Go 14 Intel Core Ultra 5 16GB 512GB",
        "Acer Predator Helios 16 Intel Core Ultra 5 16GB 512GB",
        "Family conflict Swift vs Predator",
    ),
    # Screen Size Mismatches (> 0.7 inch difference)
    (
        "Apple MacBook Air 13″ M3 (8GB RAM, 256GB SSD) 13.6 inch Liquid Retina",
        "Apple MacBook Air 15″ M3 (8GB RAM, 256GB SSD) 15.3 inch Liquid Retina",
        "Screen size conflict 13.6-inch vs 15.3-inch MacBook Air",
    ),
    (
        "Lenovo IdeaPad Slim 3 14-inch Intel Core i5-13420H (16GB/512GB SSD)",
        "Lenovo IdeaPad Slim 3 15.6-inch Intel Core i5-13420H (16GB/512GB SSD)",
        "Screen size conflict 14.0-inch vs 15.6-inch IdeaPad",
    ),
    # Memory & Storage Mismatches
    (
        "Apple MacBook Air M5 - (16 GB/256 GB SSD)",
        "Apple MacBook Air M5 - (16 GB/512 GB SSD)",
        "Storage conflict 256GB vs 512GB SSD",
    ),
    (
        "ASUS Vivobook 15 Intel Core 5 120U - (8 GB/512 GB SSD)",
        "ASUS Vivobook 15 Intel Core 5 120U - (16 GB/512 GB SSD)",
        "RAM conflict 8GB vs 16GB RAM",
    ),
]


# 3. AMBIGUOUS / INCOMPLETE PAIRS (Titles missing critical specs that MUST trigger REVIEW)
AMBIGUOUS_REVIEW_PAIRS: list[tuple[str, str, str]] = [
    (
        "Lenovo ThinkBook 14 Laptop (Ryzen 7 Processor, Arctic Grey)",
        "Lenovo ThinkBook 14 Gen 6 Laptop (16GB, 512GB SSD, Ryzen 7 7730U)",
        "Missing RAM/Storage in first title -> REVIEW",
    ),
    (
        "Apple MacBook Air 15-inch M5 Space Grey",
        "Apple MacBook Air 15-inch M5 (16GB RAM, 512GB SSD Storage)",
        "Missing memory configuration in first title -> REVIEW",
    ),
    (
        "HP Victus Gaming Laptop Intel Core i5 13th Gen",
        "HP Victus Gaming Intel Core i5 13420H (16GB/512GB SSD/RTX 3050)",
        "Missing RAM, SSD and GPU in first title -> REVIEW",
    ),
    (
        "ASUS Vivobook 15 Laptop Quiet Blue",
        "ASUS Vivobook 15 Intel Core 5 120U (8GB/512GB SSD)",
        "Missing processor and memory in first title -> REVIEW",
    ),
    (
        "Dell Inspiron 15 FHD Laptop Carbon Black",
        "DELL Inspiron 15 Intel Core i5 13th Gen 1334U (8GB/512GB SSD)",
        "Missing core hardware configuration in first title -> REVIEW",
    ),
]
