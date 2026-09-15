from django.core.management.base import BaseCommand
from products.models import Product, PSUSpecification


class Command(BaseCommand):
    help = "Import PSU specifications"

    def handle(self, *args, **kwargs):

        psu_data = [
            {
                "id": 52,
                "wattage": "1500W",
                "efficiency": "80 PLUS Platinum",
                "form_factor": "ATX",
                "modular": "Fully Modular",
                "atx_version": "ATX 3.1",
            },
            {
                "id": 53,
                "wattage": "1600W",
                "efficiency": "80 PLUS Titanium",
                "form_factor": "ATX",
                "modular": "Fully Modular",
                "atx_version": "ATX 3.1",
            },
            {
                "id": 54,
                "wattage": "1300W",
                "efficiency": "80 PLUS Titanium",
                "form_factor": "ATX",
                "modular": "Fully Modular",
                "atx_version": "ATX 3.0",
            },
            {
                "id": 55,
                "wattage": "1200W",
                "efficiency": "80 PLUS Gold",
                "form_factor": "ATX",
                "modular": "Fully Modular",
                "atx_version": "ATX 3.1",
            },
            {
                "id": 56,
                "wattage": "1000W",
                "efficiency": "80 PLUS Gold",
                "form_factor": "ATX",
                "modular": "Fully Modular",
                "atx_version": "ATX 3.1",
            },
            {
                "id": 57,
                "wattage": "1000W",
                "efficiency": "80 PLUS Gold",
                "form_factor": "ATX",
                "modular": "Fully Modular",
                "atx_version": "ATX 3.0",
            },
            {
                "id": 58,
                "wattage": "850W",
                "efficiency": "80 PLUS Gold",
                "form_factor": "ATX",
                "modular": "Fully Modular",
                "atx_version": "ATX 3.1",
            },
            {
                "id": 59,
                "wattage": "850W",
                "efficiency": "80 PLUS Gold",
                "form_factor": "ATX",
                "modular": "Fully Modular",
                "atx_version": "ATX 3.0",
            },
            {
                "id": 60,
                "wattage": "750W",
                "efficiency": "80 PLUS Gold",
                "form_factor": "ATX",
                "modular": "Fully Modular",
                "atx_version": "ATX 3.0",
            },
            {
                "id": 61,
                "wattage": "650W",
                "efficiency": "80 PLUS Bronze",
                "form_factor": "ATX",
                "modular": "Non-Modular",
                "atx_version": "ATX 3.0",
            },
        ]

        for data in psu_data:

            try:
                product = Product.objects.get(id=data["id"])

            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Product not found: {data['id']}"
                    )
                )
                continue

            psu_spec, created = PSUSpecification.objects.update_or_create(
                product=product,
                defaults={
                    "wattage": data["wattage"],
                    "efficiency": data["efficiency"],
                    "form_factor": data["form_factor"],
                    "modular": data["modular"],
                    "atx_version": data["atx_version"],
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
                "PSU specification import completed!"
            )
        )
