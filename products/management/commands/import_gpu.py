from django.core.management.base import BaseCommand
from products.models import Product, GPUSpecification


class Command(BaseCommand):
    help = "Import GPU specifications"

    def handle(self, *args, **kwargs):

        gpu_data = [
            {
                "name": "GeForce RTX 5090 32GB",
                "vram": "32GB GDDR7",
                "power_consumption": "575W",
                "interface": "PCIe 5.0 x16",
                "length": "304 mm",
            },
            {
                "name": "GeForce RTX 5080 16GB",
                "vram": "16GB GDDR7",
                "power_consumption": "360W",
                "interface": "PCIe 5.0 x16",
                "length": "304 mm",
            },
            {
                "name": "GeForce RTX 5070 Ti 16GB",
                "vram": "16GB GDDR7",
                "power_consumption": "300W",
                "interface": "PCIe 5.0 x16",
                "length": "Varies by manufacturer",
            },
            {
                "name": "Radeon RX 9070 XT 16GB",
                "vram": "16GB GDDR6",
                "power_consumption": "304W",
                "interface": "PCIe 5.0 x16",
                "length": "Varies by manufacturer",
            },
            {
                "name": "Radeon RX 9070 16GB",
                "vram": "16GB GDDR6",
                "power_consumption": "220W",
                "interface": "PCIe 5.0 x16",
                "length": "Varies by manufacturer",
            },
            {
                "name": "GeForce RTX 5070 12GB",
                "vram": "12GB GDDR7",
                "power_consumption": "250W",
                "interface": "PCIe 5.0 x16",
                "length": "242 mm",
            },
            {
                "name": "GeForce RTX 5060 Ti 16GB",
                "vram": "16GB GDDR7",
                "power_consumption": "180W",
                "interface": "PCIe 5.0 x8",
                "length": "Varies by manufacturer",
            },
            {
                "name": "Radeon RX 9060 XT 16GB",
                "vram": "16GB GDDR6",
                "power_consumption": "160W",
                "interface": "PCIe 5.0 x16",
                "length": "Varies by manufacturer",
            },
            {
                "name": "GeForce RTX 5060 8GB",
                "vram": "8GB GDDR7",
                "power_consumption": "145W",
                "interface": "PCIe 5.0 x8",
                "length": "Varies by manufacturer",
            },
            {
                "name": "GeForce RTX 5050 8GB",
                "vram": "8GB GDDR6",
                "power_consumption": "130W",
                "interface": "PCIe 5.0 x8",
                "length": "Varies by manufacturer",
            },
        ]

        for data in gpu_data:

            try:
                product = Product.objects.get(name=data["name"])

            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Product not found: {data['name']}"
                    )
                )
                continue

            gpu_spec, created = GPUSpecification.objects.update_or_create(
                product=product,
                defaults={
                    "vram": data["vram"],
                    "power_consumption": data["power_consumption"],
                    "interface": data["interface"],
                    "length": data["length"],
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
                "GPU specification import completed!"
            )
        )

