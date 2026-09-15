"""
URL configuration for buildwise project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from products import views as product_views
from products.views import (
    select_component,
    remove_component,
    reset_build,
    add_build_to_cart,
    add_prebuilt_to_cart,
    remove_prebuilt_from_cart,
    add_accessory_to_cart,
    remove_accessory_from_cart,
    wishlist_view,
    add_to_wishlist,
    add_prebuilt_to_wishlist,
    add_accessory_to_wishlist,
    remove_from_wishlist,
    move_wishlist_item_to_cart,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home & Products
    path("", product_views.home, name="home"),
    path("products/", product_views.product_list, name="products"),
    path("about/", product_views.about, name="about"),

    # PC Builder
    path("builder/", product_views.builder, name="builder"),
    path(
        "builder/select/<int:product_id>/",
        select_component,
        name="select_component",
    ),
    path(
        "builder/remove/<str:category_key>/",
        remove_component,
        name="remove_component",
    ),
    path(
        "builder/reset/",
        reset_build,
        name="reset_build",
    ),
    path(
        "builder/add-to-cart/",
        add_build_to_cart,
        name="add_build_to_cart",
    ),

    # My Configuration (read/manage the current session build)
    path(
        "my-configuration/",
        product_views.my_configuration,
        name="my_configuration",
    ),

    # Authentication
    path("login/", product_views.login_view, name="login"),
    path("logout/", product_views.logout_view, name="logout"),
    path("signup/", product_views.signup_view, name="signup"),
    path("profile/", product_views.profile_view, name="profile"),

    # Cart
    path(
        "add-to-cart/<int:product_id>/",
        product_views.add_to_cart,
        name="add_to_cart",
    ),
    path(
        "cart/",
        product_views.view_cart,
        name="view_cart",
    ),
    path(
        "remove-from-cart/<int:product_id>/",
        product_views.remove_from_cart,
        name="remove_from_cart",
    ),
    path("prebuild/", product_views.prebuild, name="prebuild"),
    path("prebuild/<int:pk>/", product_views.prebuild_details, name="prebuild_details"),
    path(
        "prebuild/<int:pk>/add-to-cart/",
        add_prebuilt_to_cart,
        name="add_prebuilt_to_cart",
    ),
    path(
        "remove-prebuilt-from-cart/<int:pk>/",
        remove_prebuilt_from_cart,
        name="remove_prebuilt_from_cart",
    ),
    path(
        "cart/update/<int:cart_item_id>/",
        product_views.update_cart_item,
        name="update_cart_item",
    ),

    # Checkout & Orders
    path("checkout/", product_views.checkout, name="checkout"),
    path(
        "orders/<int:order_id>/confirmation/",
        product_views.order_confirmation,
        name="order_confirmation",
    ),
    path("orders/", product_views.order_history, name="order_history"),
    path("orders/<int:order_id>/", product_views.order_detail, name="order_detail"),
    path("accessories/", product_views.accessories, name="accessories"),
    path("accessories/<int:pk>/", product_views.accessory_details, name="accessory_details"),
    path(
        "accessories/<int:pk>/add-to-cart/",
        add_accessory_to_cart,
        name="add_accessory_to_cart",
    ),
    path(
        "remove-accessory-from-cart/<int:pk>/",
        remove_accessory_from_cart,
        name="remove_accessory_from_cart",
    ),

        # Wishlist
    path("wishlist/", wishlist_view, name="wishlist"),
    path("wishlist/add/<int:product_id>/", add_to_wishlist, name="add_to_wishlist"),
    path(
        "wishlist/add-prebuilt/<int:pk>/",
        add_prebuilt_to_wishlist,
        name="add_prebuilt_to_wishlist",
    ),
    path(
        "wishlist/add-accessory/<int:pk>/",
        add_accessory_to_wishlist,
        name="add_accessory_to_wishlist",
    ),
    path(
        "wishlist/remove/<int:item_id>/",
        remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    path(
        "wishlist/move-to-cart/<int:item_id>/",
        move_wishlist_item_to_cart,
        name="move_wishlist_item_to_cart",
    ),
]

# Media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )