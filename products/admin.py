from django.contrib import admin
from .models import Category, Product,CPUSpecification,GPUSpecification,RAMSpecification,MotherboardSpecification,CaseSpecification,CoolerSpecification,PSUSpecification,StorageSpecification
from .models import PreBuiltPC, Accessory, Profile, CartItem, Order, OrderItem, WishlistItem

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CPUSpecification)
admin.site.register(GPUSpecification)
admin.site.register(RAMSpecification)
admin.site.register(MotherboardSpecification)
admin.site.register(CaseSpecification)
admin.site.register(CoolerSpecification)
admin.site.register(PSUSpecification)
admin.site.register(StorageSpecification)
admin.site.register(PreBuiltPC)
admin.site.register(Accessory)
admin.site.register(Profile)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(WishlistItem)