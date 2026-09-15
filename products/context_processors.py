from .models import WishlistItem


def wishlist_count(request):
    """Adds `wishlist_count` to every template's context automatically."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"wishlist_count": 0}
    return {"wishlist_count": WishlistItem.objects.filter(user=user).count()}