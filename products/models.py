from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    TIER_CHOICES = [
        ('Low', 'Low'),
        ('Mid', 'Mid'),
        ('High', 'High'),
    ]
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='Mid')

    def __str__(self):
        return self.name


class CPUSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='cpu_spec'
    )
    socket = models.CharField(max_length=50)
    cores = models.PositiveIntegerField()
    threads = models.PositiveIntegerField()
    base_clock = models.CharField(max_length=20)
    boost_clock = models.CharField(max_length=20)
    tdp = models.CharField(max_length=20)

    def __str__(self):
        return self.product.name


class GPUSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='gpu_spec'
    )
    vram = models.CharField(max_length=50)
    power_consumption = models.CharField(max_length=50)
    interface = models.CharField(max_length=50)
    length = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name


class RAMSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='ram_spec'
    )
    capacity = models.CharField(max_length=50)
    memory_type = models.CharField(max_length=50)
    speed = models.CharField(max_length=50)
    cas_latency = models.CharField(max_length=50)
    voltage = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name


class MotherboardSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='motherboard_spec'
    )
    socket = models.CharField(max_length=50)
    chipset = models.CharField(max_length=50)
    form_factor = models.CharField(max_length=50)
    ram_support = models.CharField(max_length=50)
    max_ram = models.CharField(max_length=50)
    m2_slots = models.PositiveIntegerField()
    pcie = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name


class StorageSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='storage_spec'
    )
    capacity = models.CharField(max_length=50)
    storage_type = models.CharField(max_length=50)
    interface = models.CharField(max_length=50)
    read_speed = models.CharField(max_length=50)
    write_speed = models.CharField(max_length=50)
    form_factor = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name


class PSUSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='psu_spec'
    )
    wattage = models.CharField(max_length=20)
    efficiency = models.CharField(max_length=50)
    form_factor = models.CharField(max_length=50)
    modular = models.CharField(max_length=50)
    atx_version = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name


class CaseSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='case_spec'
    )
    form_factor = models.CharField(max_length=50)
    motherboard_support = models.CharField(max_length=100)
    gpu_length = models.CharField(max_length=50)
    cpu_cooler_height = models.CharField(max_length=50)
    radiator_support = models.CharField(max_length=100)

    def __str__(self):
        return self.product.name


class CoolerSpecification(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='cooler_spec'
    )
    cooler_type = models.CharField(max_length=50)
    tdp_rating = models.CharField(max_length=50)
    radiator_size = models.CharField(max_length=50)
    fan_size = models.CharField(max_length=50)
    height = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# pre build
class PreBuiltPC(models.Model):

    CATEGORY_CHOICES = [
        ("ai_ml", "AI / ML & Data Science"),
        ("gaming", "Gaming & Streaming"),
        ("entry", "Entry-Level"),
        ("mid", "Mid-Level"),
        ("creator", "Content Creation"),
    ]

    name = models.CharField(max_length=100)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.TextField()

    cpu = models.CharField(max_length=100)
    gpu = models.CharField(max_length=100)
    motherboard = models.CharField(max_length=100)
    ram = models.CharField(max_length=100)
    storage = models.CharField(max_length=100)
    psu = models.CharField(max_length=100)
    cooler = models.CharField(max_length=100)
    cabinet = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to="prebuilt_pcs/",
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    """A single line in a user's cart. Each row belongs to exactly one user
    (unlike the old session-based cart, this persists per account and is
    visible across devices/browsers). Exactly one of `product` /
    `prebuilt_pc` is set on any given row — never both, never neither."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cart_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    prebuilt_pc = models.ForeignKey(
        PreBuiltPC, on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    accessory = models.ForeignKey(
        "Accessory", on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(product__isnull=False, prebuilt_pc__isnull=True, accessory__isnull=True)
                    | models.Q(product__isnull=True, prebuilt_pc__isnull=False, accessory__isnull=True)
                    | models.Q(product__isnull=True, prebuilt_pc__isnull=True, accessory__isnull=False)
                ),
                name="cartitem_exactly_one_target",
            ),
        ]
        unique_together = [("user", "product"), ("user", "prebuilt_pc"), ("user", "accessory")]

    def __str__(self):
        return f"{self.user.username} - {self.item_name} x{self.quantity}"

    @property
    def item(self):
        """Whichever product this row actually points to."""
        return self.product or self.prebuilt_pc or self.accessory

    @property
    def item_name(self):
        return self.item.name if self.item else "Unknown item"

    @property
    def unit_price(self):
        return self.item.price if self.item else 0

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class Order(models.Model):
    """A placed order. Shipping details are captured directly on the order
    (not the Profile) so historical orders stay accurate even if the user
    later updates their profile."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    placed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-placed_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    @property
    def total(self):
        """Template alias — order_confirmation/history/detail templates
        use `order.total`, but the real field is `total_amount`."""
        return self.total_amount


class OrderItem(models.Model):
    """One line of a placed order. `product` / `prebuilt_pc` are kept as
    SET_NULL (not CASCADE) so deleting a catalog item later never deletes
    order history — name_snapshot and unit_price preserve what was
    actually bought, at the price it was bought at."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    prebuilt_pc = models.ForeignKey(
        PreBuiltPC, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    accessory = models.ForeignKey(
        "Accessory", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    name_snapshot = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    @property
    def price_snapshot(self):
        """Template alias — order_detail.html uses `line.price_snapshot`,
        but the real field is `unit_price`."""
        return self.unit_price

    def __str__(self):
        return f"{self.name_snapshot} x{self.quantity}"

class Accessory(models.Model):

    CATEGORY_CHOICES = [
        ("monitor", "Monitors"),
        ("keyboard", "Keyboards"),
        ("mouse", "Mouse"),
        ("gaming", "Gaming Accessories"),
        ("audio", "Audio"),
        ("desk", "Desk & Setup"),
    ]

    name = models.CharField(max_length=100)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    brand = models.CharField(max_length=100)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to="accessories/",
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
class WishlistItem(models.Model):
    """A saved-for-later item, kept separate from CartItem. Same pattern:
    exactly one of product / prebuilt_pc / accessory is set on any row."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    prebuilt_pc = models.ForeignKey(
        PreBuiltPC, on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    accessory = models.ForeignKey(
        Accessory, on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(product__isnull=False, prebuilt_pc__isnull=True, accessory__isnull=True)
                    | models.Q(product__isnull=True, prebuilt_pc__isnull=False, accessory__isnull=True)
                    | models.Q(product__isnull=True, prebuilt_pc__isnull=True, accessory__isnull=False)
                ),
                name="wishlistitem_exactly_one_target",
            ),
        ]
        unique_together = [("user", "product"), ("user", "prebuilt_pc"), ("user", "accessory")]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} - {self.item_name}"

    @property
    def item(self):
        return self.product or self.prebuilt_pc or self.accessory

    @property
    def item_name(self):
        return self.item.name if self.item else "Unknown item"