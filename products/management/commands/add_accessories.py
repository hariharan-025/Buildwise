from django.core.management.base import BaseCommand
from products.models import Accessory


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        accessories = [

            # =========================
            # MONITORS
            # =========================

            {
                "name": "LG UltraGear 24GS60F 24-inch 180Hz Gaming Monitor",
                "category": "monitor",
                "brand": "LG",
                "price": 11999,
                "description": "24-inch Full HD gaming monitor with 180Hz refresh rate and fast response for smooth gaming.",
                "stock": 10,
            },

            {
                "name": "Acer Nitro VG240Y 24-inch 180Hz Gaming Monitor",
                "category": "monitor",
                "brand": "Acer",
                "price": 10999,
                "description": "Affordable 24-inch Full HD gaming monitor with a smooth 180Hz refresh rate.",
                "stock": 10,
            },

            {
                "name": "ASUS TUF Gaming VG249Q3A 24-inch 180Hz",
                "category": "monitor",
                "brand": "ASUS",
                "price": 13999,
                "description": "24-inch Full HD gaming monitor designed for smooth and responsive competitive gaming.",
                "stock": 8,
            },

            {
                "name": "Samsung Odyssey G5 27-inch 165Hz",
                "category": "monitor",
                "brand": "Samsung",
                "price": 22999,
                "description": "27-inch curved QHD gaming monitor with a 165Hz refresh rate for immersive gaming.",
                "stock": 7,
            },

            {
                "name": "LG UltraGear 27GR75Q 27-inch QHD 165Hz",
                "category": "monitor",
                "brand": "LG",
                "price": 24999,
                "description": "27-inch QHD gaming monitor with IPS display and 165Hz refresh rate.",
                "stock": 6,
            },

            {
                "name": "ASUS ProArt PA278QV 27-inch QHD Monitor",
                "category": "monitor",
                "brand": "ASUS",
                "price": 29999,
                "description": "Professional 27-inch QHD monitor suitable for content creation, design and productivity.",
                "stock": 5,
            },


            # =========================
            # KEYBOARDS
            # =========================

            {
                "name": "Redragon K617 Fizz 60% Mechanical Keyboard",
                "category": "keyboard",
                "brand": "Redragon",
                "price": 2499,
                "description": "Compact 60% mechanical gaming keyboard with RGB lighting.",
                "stock": 15,
            },

            {
                "name": "Cosmic Byte CB-GK-18 Firefly Mechanical Keyboard",
                "category": "keyboard",
                "brand": "Cosmic Byte",
                "price": 2299,
                "description": "Budget-friendly mechanical gaming keyboard with RGB backlighting.",
                "stock": 15,
            },

            {
                "name": "Redragon K552 Kumara Mechanical Keyboard",
                "category": "keyboard",
                "brand": "Redragon",
                "price": 2999,
                "description": "Tenkeyless mechanical keyboard designed for gaming and everyday use.",
                "stock": 12,
            },

            {
                "name": "Logitech G213 Prodigy Gaming Keyboard",
                "category": "keyboard",
                "brand": "Logitech",
                "price": 3499,
                "description": "Full-size gaming keyboard with RGB lighting and dedicated media controls.",
                "stock": 10,
            },

            {
                "name": "Keychron K2 Wireless Mechanical Keyboard",
                "category": "keyboard",
                "brand": "Keychron",
                "price": 7499,
                "description": "Compact wireless mechanical keyboard with multi-device connectivity.",
                "stock": 7,
            },

            {
                "name": "Logitech G915 TKL Wireless Gaming Keyboard",
                "category": "keyboard",
                "brand": "Logitech",
                "price": 13999,
                "description": "Premium low-profile wireless mechanical gaming keyboard with a compact layout.",
                "stock": 5,
            },


            # =========================
            # MOUSE
            # =========================

            {
                "name": "Logitech G102 Lightsync Gaming Mouse",
                "category": "mouse",
                "brand": "Logitech",
                "price": 1499,
                "description": "Affordable gaming mouse with accurate tracking and customizable RGB lighting.",
                "stock": 20,
            },

            {
                "name": "Redragon M612 Predator Gaming Mouse",
                "category": "mouse",
                "brand": "Redragon",
                "price": 1799,
                "description": "Feature-rich gaming mouse with programmable buttons and adjustable sensitivity.",
                "stock": 15,
            },

            {
                "name": "Razer DeathAdder Essential Gaming Mouse",
                "category": "mouse",
                "brand": "Razer",
                "price": 1999,
                "description": "Ergonomic gaming mouse designed for comfortable long gaming sessions.",
                "stock": 12,
            },

            {
                "name": "Logitech G304 Lightspeed Wireless Mouse",
                "category": "mouse",
                "brand": "Logitech",
                "price": 2999,
                "description": "Wireless gaming mouse with low-latency Lightspeed connectivity and long battery life.",
                "stock": 10,
            },

            {
                "name": "Razer DeathAdder V3 Gaming Mouse",
                "category": "mouse",
                "brand": "Razer",
                "price": 7999,
                "description": "Lightweight high-performance gaming mouse designed for competitive gaming.",
                "stock": 6,
            },

            {
                "name": "Logitech G Pro X Superlight 2",
                "category": "mouse",
                "brand": "Logitech",
                "price": 12999,
                "description": "Premium lightweight wireless gaming mouse built for competitive players.",
                "stock": 5,
            },


            # =========================
            # GAMING ACCESSORIES
            # =========================

            {
                "name": "Redgear Cosmo 7.1 RGB Gaming Headset",
                "category": "gaming",
                "brand": "Redgear",
                "price": 1799,
                "description": "RGB gaming headset with virtual 7.1 surround sound and built-in microphone.",
                "stock": 15,
            },

            {
                "name": "Cosmic Byte GS430 Gaming Headset",
                "category": "gaming",
                "brand": "Cosmic Byte",
                "price": 1499,
                "description": "Budget gaming headset with microphone and RGB lighting.",
                "stock": 15,
            },

            {
                "name": "Logitech G29 Driving Force Racing Wheel",
                "category": "gaming",
                "brand": "Logitech",
                "price": 24999,
                "description": "Racing wheel and pedal system designed for an immersive PC racing experience.",
                "stock": 4,
            },

            {
                "name": "Redragon P025 RGB Gaming Mouse Pad",
                "category": "gaming",
                "brand": "Redragon",
                "price": 1299,
                "description": "Large RGB gaming mouse pad providing smooth mouse movement and desk coverage.",
                "stock": 15,
            },

            {
                "name": "Xbox Wireless Controller",
                "category": "gaming",
                "brand": "Microsoft",
                "price": 5999,
                "description": "Wireless gaming controller with ergonomic design for PC gaming.",
                "stock": 8,
            },

            {
                "name": "8BitDo Ultimate 2C Wireless Controller",
                "category": "gaming",
                "brand": "8BitDo",
                "price": 3999,
                "description": "Wireless gaming controller with ergonomic design and responsive controls.",
                "stock": 7,
            },


            # =========================
            # AUDIO
            # =========================

            {
                "name": "boAt Immortal IM1000D Gaming Headset",
                "category": "audio",
                "brand": "boAt",
                "price": 1999,
                "description": "Affordable gaming headset with immersive audio and microphone.",
                "stock": 15,
            },

            {
                "name": "HyperX Cloud Stinger 2 Gaming Headset",
                "category": "audio",
                "brand": "HyperX",
                "price": 3999,
                "description": "Lightweight gaming headset with comfortable ear cushions and clear audio.",
                "stock": 10,
            },

            {
                "name": "JBL Quantum 100 Gaming Headset",
                "category": "audio",
                "brand": "JBL",
                "price": 2999,
                "description": "Gaming headset with detachable microphone and clear immersive audio.",
                "stock": 10,
            },

            {
                "name": "HyperX Cloud III Gaming Headset",
                "category": "audio",
                "brand": "HyperX",
                "price": 7999,
                "description": "Premium gaming headset with detailed sound and comfortable design.",
                "stock": 7,
            },

            {
                "name": "Logitech G Pro X Gaming Headset",
                "category": "audio",
                "brand": "Logitech",
                "price": 9999,
                "description": "Professional gaming headset with advanced microphone features and immersive sound.",
                "stock": 5,
            },

            {
                "name": "Creative Pebble V3 Desktop Speakers",
                "category": "audio",
                "brand": "Creative",
                "price": 3499,
                "description": "Compact USB and Bluetooth desktop speakers suitable for PC setups.",
                "stock": 8,
            },


            # =========================
            # DESK & SETUP
            # =========================

            {
                "name": "AmazonBasics Gaming Chair",
                "category": "desk",
                "brand": "AmazonBasics",
                "price": 8999,
                "description": "Comfortable high-back gaming chair designed for long gaming sessions.",
                "stock": 6,
            },

            {
                "name": "Green Soul Monster Ultimate Gaming Chair",
                "category": "desk",
                "brand": "Green Soul",
                "price": 12999,
                "description": "Ergonomic gaming chair with adjustable support for comfortable long sessions.",
                "stock": 6,
            },

            {
                "name": "Green Soul Jupiter Pro Office Chair",
                "category": "desk",
                "brand": "Green Soul",
                "price": 9999,
                "description": "Comfortable ergonomic office chair suitable for work, study and gaming.",
                "stock": 7,
            },

            {
                "name": "IKEA MATCHSPEL Gaming Chair",
                "category": "desk",
                "brand": "IKEA",
                "price": 14999,
                "description": "Adjustable gaming chair designed with ergonomic support for extended use.",
                "stock": 5,
            },

            {
                "name": "AmazonBasics Adjustable Monitor Arm",
                "category": "desk",
                "brand": "AmazonBasics",
                "price": 3499,
                "description": "Adjustable monitor arm that helps create a clean and organized desk setup.",
                "stock": 8,
            },

            {
                "name": "Dyazo Large Extended Gaming Desk Mat",
                "category": "desk",
                "brand": "Dyazo",
                "price": 999,
                "description": "Large extended desk mat providing a smooth surface for keyboard and mouse.",
                "stock": 15,
            },
        ]

        created_count = 0

        for item in accessories:
            accessory, created = Accessory.objects.get_or_create(
                name=item["name"],
                defaults=item
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{created_count} accessories added successfully."
            )
        )