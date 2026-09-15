from django.core.management.base import BaseCommand
from products.models import Product, MotherboardSpecification


class Command(BaseCommand):
    help = "Import motherboard specifications"

    def handle(self, *args, **kwargs):

        motherboard_data = [
            {
                "id": 32,
                "socket": "AM5",
                "chipset": "X870E",
                "form_factor": "E-ATX",
                "ram_support": "DDR5",
                "max_ram": "256GB",
                "m2_slots": 5,
                "pcie": "PCIe 5.0",
            },
            {
                "id": 33,
                "socket": "AM5",
                "chipset": "X870E",
                "form_factor": "ATX",
                "ram_support": "DDR5",
                "max_ram": "192GB",
                "m2_slots": 5,
                "pcie": "PCIe 5.0",
            },
            {
                "id": 34,
                "socket": "AM5",
                "chipset": "X870E",
                "form_factor": "ATX",
                "ram_support": "DDR5",
                "max_ram": "256GB",
                "m2_slots": 4,
                "pcie": "PCIe 5.0",
            },
            {
                "id": 35,
                "socket": "AM5",
                "chipset": "X870E",
                "form_factor": "ATX",
                "ram_support": "DDR5",
                "max_ram": "256GB",
                "m2_slots": 5,
                "pcie": "PCIe 5.0",
            },
            {
                "id": 36,
                "socket": "AM5",
                "chipset": "X870E",
                "form_factor": "ATX",
                "ram_support": "DDR5",
                "max_ram": "256GB",
                "m2_slots": 4,
                "pcie": "PCIe 5.0",
            },
            {
                "id": 37,
                "socket": "AM5",
                "chipset": "X870E",
                "form_factor": "ATX",
                "ram_support": "DDR5",
                "max_ram": "192GB",
                "m2_slots": 5,
                "pcie": "PCIe 5.0",
            },
            {
                "id": 38,
                "socket": "AM5",
                "chipset": "X870",
                "form_factor": "ATX",
                "ram_support": "DDR5",
                "max_ram": "256GB",
                "m2_slots": 4,
                "pcie": "PCIe 5.0",
            },
            {
                "id": 39,
                "socket": "AM5",
                "chipset": "X870",
                "form_factor": "ATX",
                "ram_support": "DDR5",
                "max_ram": "256GB",
                "m2_slots": 4,
                "pcie": "PCIe 5.0",
            },
            {
                "id": 40,
                "socket": "AM5",
                "chipset": "B850",
                "form_factor": "ATX",
                "ram_support": "DDR5",
                "max_ram": "256GB",
                "m2_slots": 3,
                "pcie": "PCIe 5.0",
            },
            {
                "id": 41,
                "socket": "AM5",
                "chipset": "B850",
                "form_factor": "ATX",
                "ram_support": "DDR5",
                "max_ram": "256GB",
                "m2_slots": 4,
                "pcie": "PCIe 5.0",
            },
        ]

        for data in motherboard_data:

            try:
                product = Product.objects.get(id=data["id"])

            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Product not found: {data['id']}"
                    )
                )
                continue

            motherboard_spec, created = (
                MotherboardSpecification.objects.update_or_create(
                    product=product,
                    defaults={
                        "socket": data["socket"],
                        "chipset": data["chipset"],
                        "form_factor": data["form_factor"],
                        "ram_support": data["ram_support"],
                        "max_ram": data["max_ram"],
                        "m2_slots": data["m2_slots"],
                        "pcie": data["pcie"],
                    },
                )
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
                "Motherboard specification import completed!"
            )
        )

