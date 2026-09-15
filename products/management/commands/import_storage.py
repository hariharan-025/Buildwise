from django.core.management.base import BaseCommand
from products.models import Product, StorageSpecification


class Command(BaseCommand):
    help = "Import storage specifications"

    def handle(self, *args, **kwargs):

        storage_data = [
            {
                "id": 42,
                "capacity": "2TB",
                "storage_type": "NVMe SSD",
                "interface": "PCIe 5.0 x4",
                "read_speed": "14,900 MB/s",
                "write_speed": "14,000 MB/s",
                "form_factor": "M.2 2280",
            },
            {
                "id": 43,
                "capacity": "2TB",
                "storage_type": "NVMe SSD",
                "interface": "PCIe 5.0 x4",
                "read_speed": "14,700 MB/s",
                "write_speed": "13,400 MB/s",
                "form_factor": "M.2 2280",
            },
            {
                "id": 44,
                "capacity": "2TB",
                "storage_type": "NVMe SSD",
                "interface": "PCIe 5.0 x4",
                "read_speed": "14,700 MB/s",
                "write_speed": "13,000 MB/s",
                "form_factor": "M.2 2280",
            },
            {
                "id": 45,
                "capacity": "2TB",
                "storage_type": "NVMe SSD",
                "interface": "PCIe 5.0 x4",
                "read_speed": "14,500 MB/s",
                "write_speed": "12,700 MB/s",
                "form_factor": "M.2 2280",
            },
            {
                "id": 46,
                "capacity": "2TB",
                "storage_type": "NVMe SSD",
                "interface": "PCIe 4.0 x4",
                "read_speed": "7,450 MB/s",
                "write_speed": "6,900 MB/s",
                "form_factor": "M.2 2280",
            },
            {
                "id": 47,
                "capacity": "2TB",
                "storage_type": "NVMe SSD",
                "interface": "PCIe 4.0 x4",
                "read_speed": "7,300 MB/s",
                "write_speed": "6,600 MB/s",
                "form_factor": "M.2 2280",
            },
            {
                "id": 48,
                "capacity": "2TB",
                "storage_type": "NVMe SSD",
                "interface": "PCIe 4.0 x4",
                "read_speed": "7,400 MB/s",
                "write_speed": "7,000 MB/s",
                "form_factor": "M.2 2280",
            },
            {
                "id": 49,
                "capacity": "2TB",
                "storage_type": "NVMe SSD",
                "interface": "PCIe 4.0 x4",
                "read_speed": "7,000 MB/s",
                "write_speed": "7,000 MB/s",
                "form_factor": "M.2 2280",
            },
            {
                "id": 50,
                "capacity": "2TB",
                "storage_type": "NVMe SSD",
                "interface": "PCIe 4.0 x4 / 5.0 x2",
                "read_speed": "7,250 MB/s",
                "write_speed": "6,300 MB/s",
                "form_factor": "M.2 2280",
            },
            {
                "id": 51,
                "capacity": "1TB",
                "storage_type": "NVMe SSD",
                "interface": "PCIe 4.0 x4",
                "read_speed": "4,150 MB/s",
                "write_speed": "4,150 MB/s",
                "form_factor": "M.2 2280",
            },
        ]

        for data in storage_data:

            try:
                product = Product.objects.get(id=data["id"])

            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Product not found: {data['id']}"
                    )
                )
                continue

            storage_spec, created = (
                StorageSpecification.objects.update_or_create(
                    product=product,
                    defaults={
                        "capacity": data["capacity"],
                        "storage_type": data["storage_type"],
                        "interface": data["interface"],
                        "read_speed": data["read_speed"],
                        "write_speed": data["write_speed"],
                        "form_factor": data["form_factor"],
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
                "Storage specification import completed!"
            )
        )

