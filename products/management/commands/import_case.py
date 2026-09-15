from django.core.management.base import BaseCommand
from products.models import Product, CaseSpecification


class Command(BaseCommand):
    help = "Import PC case specifications"

    def handle(self, *args, **kwargs):

        case_data = [
            {
                "id": 62,
                "form_factor": "Full Tower",
                "motherboard_support": "E-ATX, ATX, Micro-ATX, Mini-ITX",
                "gpu_length": "435 mm",
                "cpu_cooler_height": "185 mm",
                "radiator_support": "Up to 420 mm",
            },
            {
                "id": 63,
                "form_factor": "Mid Tower",
                "motherboard_support": "E-ATX, ATX, Micro-ATX, Mini-ITX",
                "gpu_length": "423 mm",
                "cpu_cooler_height": "167 mm",
                "radiator_support": "Up to 420 mm",
            },
            {
                "id": 64,
                "form_factor": "Full Tower",
                "motherboard_support": "E-ATX, ATX, Micro-ATX, Mini-ITX",
                "gpu_length": "413 mm",
                "cpu_cooler_height": "185 mm",
                "radiator_support": "Up to 420 mm",
            },
            {
                "id": 65,
                "form_factor": "Full Tower",
                "motherboard_support": "E-ATX, ATX, Micro-ATX, Mini-ITX",
                "gpu_length": "461 mm",
                "cpu_cooler_height": "188 mm",
                "radiator_support": "Up to 420 mm",
            },
            {
                "id": 66,
                "form_factor": "Mid Tower",
                "motherboard_support": "E-ATX, ATX, Micro-ATX, Mini-ITX",
                "gpu_length": "435 mm",
                "cpu_cooler_height": "187 mm",
                "radiator_support": "Up to 420 mm",
            },
            {
                "id": 67,
                "form_factor": "Mid Tower",
                "motherboard_support": "ATX, Micro-ATX, Mini-ITX",
                "gpu_length": "392 mm",
                "cpu_cooler_height": "180.5 mm",
                "radiator_support": "Up to 360 mm",
            },
            {
                "id": 68,
                "form_factor": "Mid Tower",
                "motherboard_support": "ATX, Micro-ATX, Mini-ITX",
                "gpu_length": "355 mm",
                "cpu_cooler_height": "170 mm",
                "radiator_support": "Up to 360 mm",
            },
            {
                "id": 69,
                "form_factor": "Mid Tower",
                "motherboard_support": "ATX, Micro-ATX, Mini-ITX",
                "gpu_length": "420 mm",
                "cpu_cooler_height": "170 mm",
                "radiator_support": "Up to 360 mm",
            },
            {
                "id": 70,
                "form_factor": "Mid Tower",
                "motherboard_support": "ATX, Micro-ATX, Mini-ITX",
                "gpu_length": "360 mm",
                "cpu_cooler_height": "170 mm",
                "radiator_support": "Up to 360 mm",
            },
            {
                "id": 71,
                "form_factor": "Mid Tower",
                "motherboard_support": "ATX, Micro-ATX, Mini-ITX",
                "gpu_length": "372 mm",
                "cpu_cooler_height": "162 mm",
                "radiator_support": "Up to 360 mm",
            },
        ]

        for data in case_data:

            try:
                product = Product.objects.get(id=data["id"])

            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Product not found: {data['id']}"
                    )
                )
                continue

            case_spec, created = CaseSpecification.objects.update_or_create(
                product=product,
                defaults={
                    "form_factor": data["form_factor"],
                    "motherboard_support": data["motherboard_support"],
                    "gpu_length": data["gpu_length"],
                    "cpu_cooler_height": data["cpu_cooler_height"],
                    "radiator_support": data["radiator_support"],
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
                "PC case specification import completed!"
            )
        )

