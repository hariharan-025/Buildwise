from django.core.management.base import BaseCommand
from products.models import Product, CoolerSpecification 


class Command(BaseCommand):
    help = "Import CPU cooler specifications"

    def handle(self, *args, **kwargs):

        cooler_data = [
            {
                "id": 72,
                "cooler_type": "Liquid",
                "tdp_rating": "450W+",
                "radiator_size": "420mm",
                "fan_size": "140mm",
                "height": "27mm radiator",
            },
            {
                "id": 73,
                "cooler_type": "Liquid",
                "tdp_rating": "300W+",
                "radiator_size": "420mm",
                "fan_size": "140mm",
                "height": "38mm radiator",
            },
            {
                "id": 74,
                "cooler_type": "Liquid",
                "tdp_rating": "300W+",
                "radiator_size": "360mm",
                "fan_size": "120mm",
                "height": "38mm radiator",
            },
            {
                "id": 75,
                "cooler_type": "Liquid",
                "tdp_rating": "300W+",
                "radiator_size": "360mm",
                "fan_size": "120mm",
                "height": "27mm radiator",
            },
            {
                "id": 76,
                "cooler_type": "Liquid",
                "tdp_rating": "300W+",
                "radiator_size": "360mm",
                "fan_size": "120mm",
                "height": "27mm radiator",
            },
            {
                "id": 77,
                "cooler_type": "Air",
                "tdp_rating": "250W+",
                "radiator_size": "N/A",
                "fan_size": "140mm",
                "height": "168mm",
            },
            {
                "id": 78,
                "cooler_type": "Air",
                "tdp_rating": "265W",
                "radiator_size": "N/A",
                "fan_size": "120mm",
                "height": "157mm",
            },
            {
                "id": 79,
                "cooler_type": "Air",
                "tdp_rating": "260W",
                "radiator_size": "N/A",
                "fan_size": "120mm",
                "height": "160mm",
            },
            {
                "id": 80,
                "cooler_type": "Air",
                "tdp_rating": "220W",
                "radiator_size": "N/A",
                "fan_size": "120mm",
                "height": "158mm",
            },
            {
                "id": 81,
                "cooler_type": "Air",
                "tdp_rating": "150W",
                "radiator_size": "N/A",
                "fan_size": "120mm",
                "height": "159mm",
            },
        ]

        for data in cooler_data:

            try:
                product = Product.objects.get(id=data["id"])

            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Product not found: {data['id']}"
                    )
                )
                continue

            cooler_spec, created = CoolerSpecification.objects.update_or_create(
                product=product,
                defaults={
                    "cooler_type": data["cooler_type"],
                    "tdp_rating": data["tdp_rating"],
                    "radiator_size": data["radiator_size"],
                    "fan_size": data["fan_size"],
                    "height": data["height"],
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
                "CPU cooler specification import completed!"
            )
        )

