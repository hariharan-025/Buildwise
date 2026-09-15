from django.core.management.base import BaseCommand
from products.models import Product, RAMSpecification


class Command(BaseCommand):
    help = "Import RAM specifications"

    def handle(self, *args, **kwargs):

        ram_data = [
            {
                "id": 22,
                "name": "Dominator Titanium DDR5 64GB",
                "capacity": "64GB",
                "memory_type": "DDR5",
                "speed": "6000 MT/s",
                "cas_latency": "CL30",
                "voltage": "1.40V",
            },
            {
                "id": 23,
                "name": "Trident Z5 RGB DDR5 64GB",
                "capacity": "64GB",
                "memory_type": "DDR5",
                "speed": "6000 MT/s",
                "cas_latency": "CL30",
                "voltage": "1.40V",
            },
            {
                "id": 24,
                "name": "Trident Z5 Neo RGB DDR5 32GB",
                "capacity": "32GB",
                "memory_type": "DDR5",
                "speed": "6000 MT/s",
                "cas_latency": "CL30",
                "voltage": "1.35V",
            },
            {
                "id": 25,
                "name": "Dominator Platinum RGB DDR5 32GB",
                "capacity": "32GB",
                "memory_type": "DDR5",
                "speed": "6000 MT/s",
                "cas_latency": "CL30",
                "voltage": "1.40V",
            },
            {
                "id": 26,
                "name": "Fury Renegade DDR5 32GB",
                "capacity": "32GB",
                "memory_type": "DDR5",
                "speed": "6000 MT/s",
                "cas_latency": "CL32",
                "voltage": "1.35V",
            },
            {
                "id": 27,
                "name": "T-Force Delta RGB DDR5 32GB",
                "capacity": "32GB",
                "memory_type": "DDR5",
                "speed": "6000 MT/s",
                "cas_latency": "CL38",
                "voltage": "1.25V",
            },
            {
                "id": 28,
                "name": "Fury Beast RGB DDR5 32GB",
                "capacity": "32GB",
                "memory_type": "DDR5",
                "speed": "6000 MT/s",
                "cas_latency": "CL36",
                "voltage": "1.35V",
            },
            {
                "id": 29,
                "name": "Corsair Vengeance DDR5 32GB",
                "capacity": "32GB",
                "memory_type": "DDR5",
                "speed": "6000 MT/s",
                "cas_latency": "CL36",
                "voltage": "1.35V",
            },
            {
                "id": 30,
                "name": "Crucial Pro DDR5 32GB",
                "capacity": "32GB",
                "memory_type": "DDR5",
                "speed": "6000 MT/s",
                "cas_latency": "CL36",
                "voltage": "1.35V",
            },
            {
                "id": 31,
                "name": "T-Force Vulcan DDR5 32GB",
                "capacity": "32GB",
                "memory_type": "DDR5",
                "speed": "6000 MT/s",
                "cas_latency": "CL38",
                "voltage": "1.25V",
            },
        ]

        for data in ram_data:

            try:
                product = Product.objects.get(id=data["id"])

            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Product not found: {data['name']} (ID: {data['id']})"
                    )
                )
                continue

            ram_spec, created = RAMSpecification.objects.update_or_create(
                product=product,
                defaults={
                    "capacity": data["capacity"],
                    "memory_type": data["memory_type"],
                    "speed": data["speed"],
                    "cas_latency": data["cas_latency"],
                    "voltage": data["voltage"],
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Added: {product.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Updated: {product.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "RAM specification import completed!"
            )
        )

