
from django.core.management.base import BaseCommand
from products.models import Product, CPUSpecification


class Command(BaseCommand):
    help = "Import CPU specifications"

    def handle(self, *args, **kwargs):

        cpu_data = [
            {
                "name": "Ryzen 9 9950X3D2",
                "socket": "AM5",
                "cores": 16,
                "threads": 32,
                "base_clock": "4.3 GHz",
                "boost_clock": "5.6 GHz",
                "tdp": "200W",
            },
            {
                "name": "Ryzen 9 9950X3D",
                "socket": "AM5",
                "cores": 16,
                "threads": 32,
                "base_clock": "4.3 GHz",
                "boost_clock": "5.7 GHz",
                "tdp": "170W",
            },
            {
                "name": "Ryzen 9 9900X3D",
                "socket": "AM5",
                "cores": 12,
                "threads": 24,
                "base_clock": "4.4 GHz",
                "boost_clock": "5.5 GHz",
                "tdp": "120W",
            },
            {
                "name": "Ryzen 7 9800X3D",
                "socket": "AM5",
                "cores": 8,
                "threads": 16,
                "base_clock": "4.7 GHz",
                "boost_clock": "5.2 GHz",
                "tdp": "120W",
            },
            {
                "name": "Core Ultra 9 285K",
                "socket": "LGA1851",
                "cores": 24,
                "threads": 24,
                "base_clock": "3.7 GHz",
                "boost_clock": "5.7 GHz",
                "tdp": "125W",
            },
            {
                "name": "Core Ultra 7 270K Plus",
                "socket": "LGA1851",
                "cores": 24,
                "threads": 24,
                "base_clock": "3.7 GHz",
                "boost_clock": "5.5 GHz",
                "tdp": "125W",
            },
            {
                "name": "Core Ultra 5 250K Plus",
                "socket": "LGA1851",
                "cores": 18,
                "threads": 18,
                "base_clock": "4.2 GHz",
                "boost_clock": "5.3 GHz",
                "tdp": "125W",
            },
            {
                "name": "Ryzen 7 9700X",
                "socket": "AM5",
                "cores": 8,
                "threads": 16,
                "base_clock": "3.8 GHz",
                "boost_clock": "5.5 GHz",
                "tdp": "65W",
            },
            {
                "name": "Ryzen 5 7600X",
                "socket": "AM5",
                "cores": 6,
                "threads": 12,
                "base_clock": "4.7 GHz",
                "boost_clock": "5.3 GHz",
                "tdp": "105W",
            },
            {
                "name": "Ryzen 5 7600",
                "socket": "AM5",
                "cores": 6,
                "threads": 12,
                "base_clock": "3.8 GHz",
                "boost_clock": "5.1 GHz",
                "tdp": "65W",
            },
        ]

        for data in cpu_data:
            try:
                product = Product.objects.get(name=data["name"])
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Product not found: {data['name']}"
                    )
                )
                continue

            cpu_spec, created = CPUSpecification.objects.update_or_create(
                product=product,
                defaults={
                    "socket": data["socket"],
                    "cores": data["cores"],
                    "threads": data["threads"],
                    "base_clock": data["base_clock"],
                    "boost_clock": data["boost_clock"],
                    "tdp": data["tdp"],
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
            self.style.SUCCESS("CPU specification import completed!")
        )
