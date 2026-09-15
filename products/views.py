import re

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db.models import F, Sum
from django.db import transaction

from .models import Profile, Category, Product, PreBuiltPC, CartItem, Order, OrderItem, Accessory, WishlistItem


# Emoji used as a placeholder image on accessory cards that have no
# uploaded photo yet — purely cosmetic, matches the pattern already used
# for the Pre-Built "PC Visual" placeholder.
ACCESSORY_EMOJI = {
    "monitor": "🖥️",
    "keyboard": "⌨️",
    "mouse": "🖱️",
    "gaming": "🎮",
    "audio": "🎧",
    "desk": "🪑",
}


BUILD_SESSION_KEY = "pc_build"     # {"CPU": product_id, "Motherboard": product_id, ...}

# The order components are chosen in. PSU is last because the wattage
# check depends on the CPU + GPU that were already picked.
BUILD_STEPS = ["CPU", "Motherboard", "RAM", "GPU", "Cooler", "Storage", "Cabinet", "PSU"]

# Maps a Category's name (however it's worded) to one of the BUILD_STEPS keys.
CATEGORY_KEYWORDS = {
    "CPU": ["cpu", "processor"],
    "Motherboard": ["motherboard", "mobo"],
    "RAM": ["ram", "memory"],
    "GPU": ["gpu", "graphics"],
    "Cooler": ["cooler", "cooling"],
    "Storage": ["storage", "ssd", "hdd"],
    "Cabinet": ["cabinet", "case"],
    "PSU": ["psu", "power supply"],
}

# The OneToOne related_name that holds each category's spec model on Product.
SPEC_RELATED_NAME = {
    "CPU": "cpu_spec",
    "Motherboard": "motherboard_spec",
    "RAM": "ram_spec",
    "GPU": "gpu_spec",
    "Cooler": "cooler_spec",
    "Storage": "storage_spec",
    "Cabinet": "case_spec",
    "PSU": "psu_spec",
}

# Which spec fields to show on the back of a flipped product card,
# in order, with a friendly label for each.
SPEC_FIELD_LABELS = {
    "CPU": [("socket", "Socket"), ("cores", "Cores"), ("threads", "Threads"),
            ("base_clock", "Base Clock"), ("boost_clock", "Boost Clock"), ("tdp", "TDP")],
    "GPU": [("vram", "VRAM"), ("power_consumption", "Power Draw"),
            ("interface", "Interface"), ("length", "Length")],
    "RAM": [("capacity", "Capacity"), ("memory_type", "Type"), ("speed", "Speed"),
            ("cas_latency", "CAS Latency"), ("voltage", "Voltage")],
    "Motherboard": [("socket", "Socket"), ("chipset", "Chipset"), ("form_factor", "Form Factor"),
                     ("ram_support", "RAM Type"), ("max_ram", "Max RAM"),
                     ("m2_slots", "M.2 Slots"), ("pcie", "PCIe")],
    "Storage": [("capacity", "Capacity"), ("storage_type", "Type"), ("interface", "Interface"),
                ("read_speed", "Read Speed"), ("write_speed", "Write Speed"), ("form_factor", "Form Factor")],
    "PSU": [("wattage", "Wattage"), ("efficiency", "Efficiency"), ("form_factor", "Form Factor"),
            ("modular", "Modular"), ("atx_version", "ATX Version")],
    "Cabinet": [("form_factor", "Form Factor"), ("motherboard_support", "Motherboard Support"),
                ("gpu_length", "Max GPU Length"), ("cpu_cooler_height", "Max Cooler Height"),
                ("radiator_support", "Radiator Support")],
    "Cooler": [("cooler_type", "Type"), ("tdp_rating", "TDP Rating"), ("radiator_size", "Radiator Size"),
               ("fan_size", "Fan Size"), ("height", "Height")],
}

TIER_SCORE = {"Low": 40, "Mid": 70, "High": 95}
PERFORMANCE_WEIGHTS = {"CPU": 0.35, "GPU": 0.45, "RAM": 0.1, "Storage": 0.1}


# ---------------------------------------------------------
# Small helpers used by the builder + product pages
# ---------------------------------------------------------

def classify_category(category):
    """Turn a Category (e.g. 'Cabinet') into one of the BUILD_STEPS keys."""
    if not category:
        return None
    name = category.name.lower()
    for key, keywords in CATEGORY_KEYWORDS.items():
        if any(word in name for word in keywords):
            return key
    return None


def get_step_category_map():
    """{'CPU': <Category CPU>, 'Motherboard': <Category Motherboard>, ...}"""
    mapping = {}
    for category in Category.objects.all():
        key = classify_category(category)
        if key and key not in mapping:
            mapping[key] = category
    return mapping


def get_spec(product, category_key):
    if not product or not category_key:
        return None
    related_name = SPEC_RELATED_NAME.get(category_key)
    return getattr(product, related_name, None) if related_name else None


def build_spec_pairs(product, category_key):
    """Label/value pairs for the back of a flip card, e.g. [('Socket', 'AM5'), ...]."""
    spec = get_spec(product, category_key)
    if not spec:
        return []
    pairs = []
    for field_name, label in SPEC_FIELD_LABELS.get(category_key, []):
        value = getattr(spec, field_name, None)
        if value not in (None, ""):
            pairs.append((label, value))
    return pairs


def extract_number(value):
    """Pull the first number out of strings like '200W', '435 mm', '1500W'."""
    if not value:
        return None
    match = re.search(r"[\d,]+(?:\.\d+)?", str(value))
    if not match:
        return None
    return float(match.group().replace(",", ""))


def format_inr(value):
    """Format a number using Indian digit grouping, e.g. 149999 -> '1,49,999'."""
    try:
        value = int(round(float(value)))
    except (TypeError, ValueError):
        return value
    sign = "-" if value < 0 else ""
    digits = str(abs(value))
    if len(digits) <= 3:
        return f"{sign}{digits}"
    last_three = digits[-3:]
    rest = digits[:-3]
    groups = []
    while len(rest) > 2:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.insert(0, rest)
    return f"{sign}{','.join(groups)},{last_three}"


def _cart_count(request):
    """Total item quantity in the CURRENT USER's cart. Anonymous visitors
    have no DB cart, so this is 0 until they log in."""
    if not request.user.is_authenticated:
        return 0
    total = CartItem.objects.filter(user=request.user).aggregate(total=Sum("quantity"))
    return total["total"] or 0


def get_build_products(request):
    """Turn the session's {category_key: product_id} map into {category_key: Product}.
    This is what makes the build 'belong' to the current user: it's the current
    session's data only, so one user's picks never appear in another user's session."""
    raw = request.session.get(BUILD_SESSION_KEY, {})
    products = {}
    if raw:
        ids = [pid for pid in raw.values() if pid]
        found = Product.objects.select_related(
            "cpu_spec", "gpu_spec", "ram_spec", "motherboard_spec",
            "storage_spec", "psu_spec", "case_spec", "cooler_spec",
        ).in_bulk(ids)
        for key, pid in raw.items():
            products[key] = found.get(pid)
    return products


def check_candidate_compatibility(category_key, product, build_products):
    """Compare ONE candidate product against whatever is already selected.
    Returns a list of short warning strings; empty = no problems found."""
    problems = []
    spec = get_spec(product, category_key)

    cpu = build_products.get("CPU")
    mobo = build_products.get("Motherboard")
    gpu = build_products.get("GPU")
    cabinet = build_products.get("Cabinet")
    cooler = build_products.get("Cooler")

    if category_key == "CPU" and mobo and spec:
        mobo_spec = get_spec(mobo, "Motherboard")
        if mobo_spec and spec.socket.strip().upper() != mobo_spec.socket.strip().upper():
            problems.append(f"Socket mismatch with your motherboard ({mobo_spec.socket}).")

    if category_key == "Motherboard" and spec:
        if cpu:
            cpu_spec = get_spec(cpu, "CPU")
            if cpu_spec and spec.socket.strip().upper() != cpu_spec.socket.strip().upper():
                problems.append(f"Socket mismatch with your CPU ({cpu_spec.socket}).")
        if cabinet:
            cabinet_spec = get_spec(cabinet, "Cabinet")
            if cabinet_spec and spec.form_factor.strip().upper() not in cabinet_spec.motherboard_support.upper():
                problems.append("Form factor may not be supported by your cabinet.")

    if category_key == "RAM" and mobo and spec:
        mobo_spec = get_spec(mobo, "Motherboard")
        if mobo_spec and spec.memory_type.strip().upper() != mobo_spec.ram_support.strip().upper():
            problems.append(f"Memory type not supported by your motherboard ({mobo_spec.ram_support}).")

    if category_key == "GPU" and cabinet and spec:
        cabinet_spec = get_spec(cabinet, "Cabinet")
        gpu_len = extract_number(spec.length)
        case_len = extract_number(cabinet_spec.gpu_length) if cabinet_spec else None
        if gpu_len and case_len and gpu_len > case_len:
            problems.append(f"May not fit your cabinet (max {cabinet_spec.gpu_length}).")

    if category_key == "Cabinet" and spec:
        if gpu:
            gpu_spec = get_spec(gpu, "GPU")
            gpu_len = extract_number(gpu_spec.length) if gpu_spec else None
            case_len = extract_number(spec.gpu_length)
            if gpu_len and case_len and gpu_len > case_len:
                problems.append(f"Your GPU ({gpu_spec.length}) may not fit (max {spec.gpu_length}).")
        if mobo:
            mobo_spec = get_spec(mobo, "Motherboard")
            if mobo_spec and mobo_spec.form_factor.strip().upper() not in spec.motherboard_support.upper():
                problems.append("May not support your motherboard's form factor.")
        if cooler:
            cooler_spec = get_spec(cooler, "Cooler")
            if cooler_spec:
                if cooler_spec.cooler_type.strip().lower() == "air":
                    cooler_h, case_h = extract_number(cooler_spec.height), extract_number(spec.cpu_cooler_height)
                    if cooler_h and case_h and cooler_h > case_h:
                        problems.append("Your cooler may not fit (height clearance).")
                else:
                    rad, case_rad = extract_number(cooler_spec.radiator_size), extract_number(spec.radiator_support)
                    if rad and case_rad and rad > case_rad:
                        problems.append("Your cooler's radiator may not fit.")

    if category_key == "Cooler" and spec:
        if cpu:
            cpu_spec = get_spec(cpu, "CPU")
            cpu_tdp = extract_number(cpu_spec.tdp) if cpu_spec else None
            cooler_tdp = extract_number(spec.tdp_rating)
            if cpu_tdp and cooler_tdp and cooler_tdp < cpu_tdp:
                problems.append(f"May not sufficiently cool your CPU ({cpu_spec.tdp}).")
        if cabinet:
            cabinet_spec = get_spec(cabinet, "Cabinet")
            if cabinet_spec:
                if spec.cooler_type.strip().lower() == "air":
                    cooler_h, case_h = extract_number(spec.height), extract_number(cabinet_spec.cpu_cooler_height)
                    if cooler_h and case_h and cooler_h > case_h:
                        problems.append("May not fit your cabinet's height clearance.")
                else:
                    rad, case_rad = extract_number(spec.radiator_size), extract_number(cabinet_spec.radiator_support)
                    if rad and case_rad and rad > case_rad:
                        problems.append("Radiator may not fit your cabinet.")

    if category_key == "PSU" and spec:
        cpu_spec = get_spec(cpu, "CPU") if cpu else None
        gpu_spec = get_spec(gpu, "GPU") if gpu else None
        draw = (extract_number(cpu_spec.tdp) if cpu_spec else 0) or 0
        draw += (extract_number(gpu_spec.power_consumption) if gpu_spec else 0) or 0
        draw += 120  # headroom for board, fans, storage, etc.
        psu_watt = extract_number(spec.wattage)
        if psu_watt and psu_watt < draw:
            problems.append(f"Wattage may be too low for your build (~{int(draw)}W needed).")

    return problems


def analyze_build(build_products):
    """Full build-wide compatibility + price check, shared by Builder and My Configuration."""
    issues = []
    warnings = []
    total_price = 0

    for product in build_products.values():
        if product:
            total_price += product.price

    cpu = build_products.get("CPU")
    mobo = build_products.get("Motherboard")
    ram = build_products.get("RAM")
    gpu = build_products.get("GPU")
    cooler = build_products.get("Cooler")
    cabinet = build_products.get("Cabinet")
    psu = build_products.get("PSU")

    cpu_spec = get_spec(cpu, "CPU")
    mobo_spec = get_spec(mobo, "Motherboard")
    ram_spec = get_spec(ram, "RAM")
    gpu_spec = get_spec(gpu, "GPU")
    cooler_spec = get_spec(cooler, "Cooler")
    cabinet_spec = get_spec(cabinet, "Cabinet")
    psu_spec = get_spec(psu, "PSU")

    if cpu_spec and mobo_spec and cpu_spec.socket.strip().upper() != mobo_spec.socket.strip().upper():
        issues.append(f"CPU socket ({cpu_spec.socket}) does not match motherboard socket ({mobo_spec.socket}).")

    if ram_spec and mobo_spec and ram_spec.memory_type.strip().upper() != mobo_spec.ram_support.strip().upper():
        issues.append(f"RAM type ({ram_spec.memory_type}) is not supported by the motherboard ({mobo_spec.ram_support}).")

    if mobo_spec and cabinet_spec and mobo_spec.form_factor.strip().upper() not in cabinet_spec.motherboard_support.upper():
        issues.append(f"Motherboard form factor ({mobo_spec.form_factor}) may not be supported by the cabinet.")

    if gpu_spec and cabinet_spec:
        gpu_len, case_len = extract_number(gpu_spec.length), extract_number(cabinet_spec.gpu_length)
        if gpu_len and case_len and gpu_len > case_len:
            warnings.append(f"GPU length ({gpu_spec.length}) may not fit in the cabinet (max {cabinet_spec.gpu_length}).")

    if cooler_spec and cpu_spec:
        cpu_tdp, cooler_tdp = extract_number(cpu_spec.tdp), extract_number(cooler_spec.tdp_rating)
        if cpu_tdp and cooler_tdp and cooler_tdp < cpu_tdp:
            warnings.append(f"Cooler TDP rating ({cooler_spec.tdp_rating}) may be insufficient for the CPU ({cpu_spec.tdp}).")

    if cooler_spec and cabinet_spec:
        if cooler_spec.cooler_type.strip().lower() == "air":
            cooler_h, case_h = extract_number(cooler_spec.height), extract_number(cabinet_spec.cpu_cooler_height)
            if cooler_h and case_h and cooler_h > case_h:
                warnings.append(f"Cooler height ({cooler_spec.height}) may exceed the cabinet's clearance (max {cabinet_spec.cpu_cooler_height}).")
        else:
            rad, case_rad = extract_number(cooler_spec.radiator_size), extract_number(cabinet_spec.radiator_support)
            if rad and case_rad and rad > case_rad:
                warnings.append(f"Radiator size ({cooler_spec.radiator_size}) may exceed the cabinet's support (max {cabinet_spec.radiator_support}).")

    estimated_draw = (extract_number(cpu_spec.tdp) if cpu_spec else 0) or 0
    estimated_draw += (extract_number(gpu_spec.power_consumption) if gpu_spec else 0) or 0
    estimated_draw += 120

    if psu_spec:
        psu_watt = extract_number(psu_spec.wattage) or 0
        if psu_watt < estimated_draw:
            issues.append(f"PSU wattage ({psu_spec.wattage}) may not be sufficient. Estimated draw is about {int(estimated_draw)}W.")
        elif psu_watt < estimated_draw * 1.2:
            warnings.append(f"PSU wattage ({psu_spec.wattage}) is close to the estimated draw ({int(estimated_draw)}W). Consider more headroom.")
    elif estimated_draw > 120:
        warnings.append(f"Estimated system draw is about {int(estimated_draw)}W — pick a PSU with enough headroom.")

    return {"issues": issues, "warnings": warnings, "total_price": total_price, "estimated_draw": estimated_draw}


def estimate_performance(build_products):
    """A transparent weighted average of each part's tier (Low/Mid/High). Plain arithmetic, not AI."""
    weighted_total = 0
    weight_used = 0
    for key, weight in PERFORMANCE_WEIGHTS.items():
        product = build_products.get(key)
        if product:
            weighted_total += TIER_SCORE.get(product.tier, 60) * weight
            weight_used += weight
    if weight_used == 0:
        return None
    return round(weighted_total / weight_used)


def build_recommendation(issues, performance):
    if issues:
        return "NEEDS ATTENTION", "bad"
    if performance is None:
        return "INCOMPLETE BUILD", "warn"
    if performance >= 85:
        return "EXCELLENT BUILD", "good"
    if performance >= 65:
        return "GOOD BUILD", "good"
    return "BASIC BUILD", "warn"


def _get_build_context(request):
    """Assemble the step list + compatibility analysis + performance + recommendation
    for the CURRENT SESSION's build. Both the Builder page and the My Configuration
    page call this, so they always show the exact same, always-current data —
    there's nothing to keep in sync manually."""
    step_category_map = get_step_category_map()
    build = get_build_products(request)

    steps = []
    for step_key in BUILD_STEPS:
        product = build.get(step_key)
        steps.append({
            "key": step_key,
            "category": step_category_map.get(step_key),
            "product": product,
        })

    analysis = analyze_build(build)
    performance = estimate_performance(build)
    recommendation, recommendation_level = build_recommendation(analysis["issues"], performance)
    selected_count = sum(1 for step in steps if step["product"])
    total_steps = len(BUILD_STEPS)
    progress_percent = round((selected_count / total_steps) * 100) if total_steps else 0

    return {
        "steps": steps,
        "analysis": analysis,
        "performance": performance,
        "recommendation": recommendation,
        "recommendation_level": recommendation_level,
        "selected_count": selected_count,
        "total_steps": total_steps,
        "progress_percent": progress_percent,
    }


# ---------------------------------------------------------
# Pages
# ---------------------------------------------------------

def home(request):
    return render(request, "index.html", {
        "categories": Category.objects.all(),
        "cart_count": _cart_count(request),
    })


def about(request):
    return render(request, "about.html", {"cart_count": _cart_count(request)})


@login_required(login_url="login")
def profile_view(request):
    """Was previously a dead link ('/profile/') on every page — this view
    finally backs it. Lets the user see their account info and update the
    phone number saved on their Profile."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    message = None

    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        profile.phone = phone
        profile.save(update_fields=["phone"])
        message = "Profile updated."

    return render(request, "profile.html", {
        "profile": profile,
        "message": message,
        "order_count": Order.objects.filter(user=request.user).count(),
        "cart_count": _cart_count(request),
    })


def product_list(request):
    products = Product.objects.select_related(
        "category", "cpu_spec", "gpu_spec", "ram_spec", "motherboard_spec",
        "storage_spec", "psu_spec", "case_spec", "cooler_spec",
    ).all()

    selected_category = None
    category_id = request.GET.get("category")
    if category_id:
        selected_category = Category.objects.filter(id=category_id).first()
        products = products.filter(category_id=category_id)

    build_mode = request.GET.get("build") == "1"
    category_key = classify_category(selected_category) if selected_category else None
    build_products = get_build_products(request) if build_mode else {}

    # Hard-filter only the cases where mismatch is a guaranteed dead end.
    if build_mode and category_key:
        if category_key == "Motherboard" and build_products.get("CPU"):
            cpu_spec = get_spec(build_products["CPU"], "CPU")
            if cpu_spec:
                products = products.filter(motherboard_spec__socket__iexact=cpu_spec.socket)
        elif category_key == "CPU" and build_products.get("Motherboard"):
            mobo_spec = get_spec(build_products["Motherboard"], "Motherboard")
            if mobo_spec:
                products = products.filter(cpu_spec__socket__iexact=mobo_spec.socket)
        elif category_key == "RAM" and build_products.get("Motherboard"):
            mobo_spec = get_spec(build_products["Motherboard"], "Motherboard")
            if mobo_spec:
                products = products.filter(ram_spec__memory_type__iexact=mobo_spec.ram_support)

    products = list(products)

    wishlist_map = {}
    if request.user.is_authenticated:
        wishlist_map = dict(
            WishlistItem.objects.filter(user=request.user, product__isnull=False)
            .values_list("product_id", "id")
        )

    for product in products:
        product.spec_pairs = build_spec_pairs(product, classify_category(product.category))
        product.wishlist_item_id = wishlist_map.get(product.id)
        if build_mode and category_key:
            product.compat_issues = check_candidate_compatibility(category_key, product, build_products)
            selected_product = build_products.get(category_key)
            product.is_selected_in_build = bool(selected_product and selected_product.id == product.id)

    return render(request, "products.html", {
        "products": products,
        "selected_category": selected_category,
        "cart_count": _cart_count(request),
        "build_mode": build_mode,
        "category_key": category_key,
    })


@login_required(login_url="login")
def builder(request):
    context = _get_build_context(request)
    context["cart_count"] = _cart_count(request)
    return render(request, "builder.html", context)


@login_required(login_url="login")
def my_configuration(request):
    """Read-only-ish view of the current session's build, for the logged-in user
    to review, adjust, or send to their cart. Uses the exact same data as the
    Builder page (via _get_build_context), so it's always live/real-time and
    never needs a separate database record to stay in sync."""
    context = _get_build_context(request)
    context["cart_count"] = _cart_count(request)
    return render(request, "my_configuration.html", context)


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        error = None

        if not username or not email or not password1 or not password2:
            error = "All fields are required."

        if not error:
            try:
                validate_email(email)
            except ValidationError:
                error = "Enter a valid email address."

        if not error and password1 != password2:
            error = "Passwords do not match."

        if not error:
            try:
                validate_password(password1, user=User(username=username, email=email))
            except ValidationError as e:
                error = " ".join(e.messages)

        if not error and User.objects.filter(username=username).exists():
            error = "That username is already taken."

        if not error and User.objects.filter(email=email).exists():
            error = "An account with that email already exists."

        if error:
            return render(request, "signup.html", {
                "error": error,
                "old_username": username,
                "old_email": email,
                "old_phone": phone,
                "cart_count": _cart_count(request),
            })

        user = User.objects.create_user(username=username, email=email, password=password1)
        Profile.objects.create(user=user, phone=phone)

        login(request, user)
        return redirect("home")

    return render(request, "signup.html", {"cart_count": _cart_count(request)})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    next_url = request.GET.get("next") or request.POST.get("next") or "home"

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url)

        return render(request, "login.html", {
            "error": "Invalid username or password.",
            "old_username": username,
            "next": next_url,
            "cart_count": _cart_count(request),
        })

    return render(request, "login.html", {"next": next_url, "cart_count": _cart_count(request)})


def logout_view(request):
    logout(request)
    return redirect("home")


# ---------------------------------------------------------
# Per-user database-backed cart
# ---------------------------------------------------------

def _add_or_increment(user, **target):
    """get_or_create a CartItem for this user + product/prebuilt_pc kwarg,
    incrementing quantity if a row already exists. `target` should be
    exactly one of product=<Product> or prebuilt_pc=<PreBuiltPC>."""
    item, created = CartItem.objects.get_or_create(
        user=user, defaults={"quantity": 1}, **target
    )
    if not created:
        item.quantity = F("quantity") + 1
        item.save(update_fields=["quantity"])
    return item


@login_required(login_url="login")
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        _add_or_increment(request.user, product=product)

    next_url = request.POST.get("next") or "/products/"
    return redirect(next_url)


@login_required(login_url="login")
def view_cart(request):
    items = (
        CartItem.objects.filter(user=request.user)
        .select_related("product", "prebuilt_pc")
        .order_by("-added_at")
    )

    cart_items = []
    total = 0
    total_items = 0
    for cart_item in items:
        subtotal = cart_item.subtotal
        total += subtotal
        total_items += cart_item.quantity
        stock = cart_item.item.stock if cart_item.item else 0
        cart_items.append({
            "cart_item_id": cart_item.id,
            "product": cart_item.item,          # Product, PreBuiltPC, or Accessory — same attribute names (name/price/image/stock)
            "is_prebuilt": cart_item.prebuilt_pc_id is not None,
            "is_accessory": cart_item.accessory_id is not None,
            "quantity": cart_item.quantity,
            "subtotal": subtotal,
            "at_max_stock": bool(stock) and cart_item.quantity >= stock,
        })

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total,
        "total_items": total_items,
        "cart_count": _cart_count(request),
    })


@login_required(login_url="login")
def update_cart_item(request, cart_item_id):
    """Increase or decrease a single cart line's quantity. Clamped between
    1 and the item's available stock; dropping to 0 removes the line."""
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        action = request.POST.get("action")

        new_qty = cart_item.quantity + 1 if action == "increase" else cart_item.quantity - 1

        stock = cart_item.item.stock if cart_item.item else None
        if stock:
            new_qty = min(new_qty, stock)

        if new_qty <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = new_qty
            cart_item.save(update_fields=["quantity"])

    return redirect("view_cart")


@login_required(login_url="login")
def remove_from_cart(request, product_id):
    """Removes a Product line from the current user's cart. Unchanged
    signature/behaviour for existing 'remove' buttons on the cart page."""
    if request.method == "POST":
        CartItem.objects.filter(
            user=request.user, product_id=product_id
        ).delete()

    return redirect("view_cart")


@login_required(login_url="login")
def remove_prebuilt_from_cart(request, pk):
    """Removes a Pre-Built PC line from the current user's cart."""
    if request.method == "POST":
        CartItem.objects.filter(
            user=request.user, prebuilt_pc_id=pk
        ).delete()

    return redirect("view_cart")


# ---------------------------------------------------------
# Checkout & Orders
# ---------------------------------------------------------

@login_required(login_url="login")
def checkout(request):
    """Review the cart, collect shipping details, and place the order.
    On success, converts every CartItem into an OrderItem (snapshotting
    name/price so the order stays accurate later), clears the cart, and
    redirects to the confirmation page."""
    cart_qs = (
        CartItem.objects.filter(user=request.user)
        .select_related("product", "prebuilt_pc")
        .order_by("-added_at")
    )

    if not cart_qs.exists():
        return redirect("view_cart")

    cart_items = []
    total = 0
    for cart_item in cart_qs:
        subtotal = cart_item.subtotal
        total += subtotal
        cart_items.append({
            "product": cart_item.item,
            "is_prebuilt": cart_item.prebuilt_pc_id is not None,
            "is_accessory": cart_item.accessory_id is not None,
            "quantity": cart_item.quantity,
            "subtotal": subtotal,
        })

    profile = Profile.objects.filter(user=request.user).first()
    old = {
        "full_name": request.user.get_full_name() or request.user.username,
        "phone": profile.phone if profile else "",
        "address_line": "",
        "city": "",
        "state": "",
        "pincode": "",
    }

    error = None

    if request.method == "POST":
        old = {
            "full_name": request.POST.get("full_name", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "address_line": request.POST.get("address_line", "").strip(),
            "city": request.POST.get("city", "").strip(),
            "state": request.POST.get("state", "").strip(),
            "pincode": request.POST.get("pincode", "").strip(),
        }

        if not all(old.values()):
            error = "Please fill in every shipping field."
        else:
            insufficient = [
                ci for ci in cart_qs if ci.item and ci.item.stock < ci.quantity
            ]
            if insufficient:
                names = ", ".join(ci.item_name for ci in insufficient)
                error = f"Not enough stock for: {names}. Please update the quantity in your cart."
            else:
                with transaction.atomic():
                    order = Order.objects.create(
                        user=request.user,
                        total_amount=total,
                        **old,
                    )
                    for cart_item in cart_qs:
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            prebuilt_pc=cart_item.prebuilt_pc,
                            accessory=cart_item.accessory,
                            name_snapshot=cart_item.item_name,
                            unit_price=cart_item.unit_price,
                            quantity=cart_item.quantity,
                        )
                        # Actually decrement stock so it stays accurate site-wide
                        if cart_item.product_id:
                            Product.objects.filter(id=cart_item.product_id).update(
                                stock=F("stock") - cart_item.quantity
                            )
                        elif cart_item.prebuilt_pc_id:
                            PreBuiltPC.objects.filter(id=cart_item.prebuilt_pc_id).update(
                                stock=F("stock") - cart_item.quantity
                            )
                        elif cart_item.accessory_id:
                            Accessory.objects.filter(id=cart_item.accessory_id).update(
                                stock=F("stock") - cart_item.quantity
                            )
                    cart_qs.delete()

                return redirect("order_confirmation", order_id=order.id)

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "old": old,
        "error": error,
        "cart_count": _cart_count(request),
    })


@login_required(login_url="login")
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "order_confirmation.html", {
        "order": order,
        "cart_count": _cart_count(request),
    })


@login_required(login_url="login")
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "order_history.html", {
        "orders": orders,
        "cart_count": _cart_count(request),
    })


@login_required(login_url="login")
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "order_detail.html", {
        "order": order,
        "cart_count": _cart_count(request),
    })



# ---------------------------------------------------------
# PC Builder actions
# ---------------------------------------------------------

@login_required(login_url="login")
def select_component(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        category_key = classify_category(product.category)
        if category_key:
            build = request.session.get(BUILD_SESSION_KEY, {})
            build[category_key] = product.id
            request.session[BUILD_SESSION_KEY] = build
            request.session.modified = True

    return redirect("builder")


@login_required(login_url="login")
def remove_component(request, category_key):
    if request.method == "POST":
        build = request.session.get(BUILD_SESSION_KEY, {})
        if category_key in build:
            del build[category_key]
            request.session[BUILD_SESSION_KEY] = build
            request.session.modified = True

    return redirect("builder")


@login_required(login_url="login")
def reset_build(request):
    if request.method == "POST":
        request.session[BUILD_SESSION_KEY] = {}
        request.session.modified = True

    return redirect("builder")


@login_required(login_url="login")
def add_build_to_cart(request):
    if request.method == "POST":
        build = request.session.get(BUILD_SESSION_KEY, {})
        product_ids = [pid for pid in build.values() if pid]
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            _add_or_increment(request.user, product=product)

    return redirect("view_cart")


@login_required(login_url="login")
def add_prebuilt_to_cart(request, pk):
    if request.method == "POST":
        pc = get_object_or_404(PreBuiltPC, pk=pk)
        _add_or_increment(request.user, prebuilt_pc=pc)
        return redirect("view_cart")

    return redirect("prebuild_details", pk=pk)

def prebuild(request):
    """Pre-Built PC catalog, backed by the PreBuiltPC model.

    Supports an optional ?category=<key> filter (matching PreBuiltPC's
    CATEGORY_CHOICES keys, e.g. 'gaming', 'ai_ml'), used both by the
    hero carousel's "Explore Build" links and the filter pills below.
    """
    selected_category = request.GET.get("category") or ""

    prebuilt_pcs = list(PreBuiltPC.objects.all().order_by("category", "price"))

    wishlist_map = {}
    if request.user.is_authenticated:
        wishlist_map = dict(
            WishlistItem.objects.filter(user=request.user, prebuilt_pc__isnull=False)
            .values_list("prebuilt_pc_id", "id")
        )

    for pc in prebuilt_pcs:
        pc.price_display = format_inr(pc.price)
        pc.wishlist_item_id = wishlist_map.get(pc.id)

    return render(request, "prebuild.html", {
        "prebuilt_pcs": prebuilt_pcs,
        "category_choices": PreBuiltPC.CATEGORY_CHOICES,
        "selected_category": selected_category,
        "cart_count": _cart_count(request),
    })


def prebuild_details(request, pk):
    """Full specification page for a single Pre-Built PC."""
    pc = get_object_or_404(PreBuiltPC, pk=pk)
    pc.price_display = format_inr(pc.price)

    pc.wishlist_item_id = None
    if request.user.is_authenticated:
        wi = WishlistItem.objects.filter(user=request.user, prebuilt_pc=pc).first()
        pc.wishlist_item_id = wi.id if wi else None

    spec_pairs = [
        ("CPU", pc.cpu),
        ("GPU", pc.gpu),
        ("Motherboard", pc.motherboard),
        ("RAM", pc.ram),
        ("Storage", pc.storage),
        ("PSU", pc.psu),
        ("Cooler", pc.cooler),
        ("Cabinet", pc.cabinet),
    ]

    related = list(
        PreBuiltPC.objects.filter(category=pc.category).exclude(pk=pc.pk)[:3]
    )
    for item in related:
        item.price_display = format_inr(item.price)

    return render(request, "prebuild_details.html", {
        "pc": pc,
        "spec_pairs": spec_pairs,
        "related": related,
        "cart_count": _cart_count(request),
    })

def accessories(request):
    """Accessories catalog, backed by the Accessory model. Filtering is
    client-side via JS pills (script.js), same pattern as before — this
    just supplies real Accessory rows instead of static placeholder cards,
    plus one 'hero' item per category for the top carousel."""
    accessories_qs = list(Accessory.objects.all().order_by("category", "price"))

    wishlist_map = {}
    if request.user.is_authenticated:
        wishlist_map = dict(
            WishlistItem.objects.filter(user=request.user, accessory__isnull=False)
            .values_list("accessory_id", "id")
        )

    for item in accessories_qs:
        item.price_display = format_inr(item.price)
        item.emoji = ACCESSORY_EMOJI.get(item.category, "🛒")
        item.wishlist_item_id = wishlist_map.get(item.id)

    hero_by_category = []
    for key, label in Accessory.CATEGORY_CHOICES:
        featured = Accessory.objects.filter(category=key).order_by("-stock", "price").first()
        if featured:
            featured.price_display = format_inr(featured.price)
        hero_by_category.append({
            "key": key,
            "label": label,
            "item": featured,
            "emoji": ACCESSORY_EMOJI.get(key, "🛒"),
        })

    return render(request, "accessories.html", {
        "accessories": accessories_qs,
        "category_choices": Accessory.CATEGORY_CHOICES,
        "hero_by_category": hero_by_category,
        "cart_count": _cart_count(request),
    })


def accessory_details(request, pk):
    """Full detail page for a single Accessory."""
    accessory = get_object_or_404(Accessory, pk=pk)
    accessory.price_display = format_inr(accessory.price)
    accessory.emoji = ACCESSORY_EMOJI.get(accessory.category, "🛒")

    accessory.wishlist_item_id = None
    if request.user.is_authenticated:
        wi = WishlistItem.objects.filter(user=request.user, accessory=accessory).first()
        accessory.wishlist_item_id = wi.id if wi else None

    related = list(
        Accessory.objects.filter(category=accessory.category).exclude(pk=accessory.pk)[:3]
    )
    for item in related:
        item.price_display = format_inr(item.price)
        item.emoji = ACCESSORY_EMOJI.get(item.category, "🛒")

    return render(request, "accessory_details.html", {
        "accessory": accessory,
        "related": related,
        "cart_count": _cart_count(request),
    })


@login_required(login_url="login")
def add_accessory_to_cart(request, pk):
    if request.method == "POST":
        accessory = get_object_or_404(Accessory, pk=pk)
        _add_or_increment(request.user, accessory=accessory)

    next_url = request.POST.get("next") or "/accessories/"
    return redirect(next_url)


@login_required(login_url="login")
def remove_accessory_from_cart(request, pk):
    """Removes an Accessory line from the current user's cart."""
    if request.method == "POST":
        CartItem.objects.filter(user=request.user, accessory_id=pk).delete()

    return redirect("view_cart")

# ---------------------------------------------------------
# Wishlist (Phase 7) — saved-for-later items, separate from the cart.
# Mirrors the CartItem pattern: one row per user+item, exactly one of
# product/prebuilt_pc/accessory set. wishlist_count is injected into
# every template automatically via products.context_processors, so no
# view here needs to pass it manually.
# ---------------------------------------------------------

def _add_to_wishlist(user, **target):
    """get_or_create a WishlistItem — unlike the cart, quantity doesn't
    matter here, so a duplicate add is just a no-op."""
    item, _created = WishlistItem.objects.get_or_create(user=user, **target)
    return item


@login_required(login_url="login")
def add_to_wishlist(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        _add_to_wishlist(request.user, product=product)

    next_url = request.POST.get("next") or "/products/"
    return redirect(next_url)

@login_required(login_url="login")
def add_prebuilt_to_wishlist(request, pk):
    if request.method == "POST":
        pc = get_object_or_404(PreBuiltPC, pk=pk)
        _add_to_wishlist(request.user, prebuilt_pc=pc)
        next_url = request.POST.get("next")
        return redirect(next_url) if next_url else redirect("wishlist")

    return redirect("prebuild_details", pk=pk)


@login_required(login_url="login")
def add_accessory_to_wishlist(request, pk):
    if request.method == "POST":
        accessory = get_object_or_404(Accessory, pk=pk)
        _add_to_wishlist(request.user, accessory=accessory)

    next_url = request.POST.get("next") or "/accessories/"
    return redirect(next_url)


@login_required(login_url="login")
def remove_from_wishlist(request, item_id):
    if request.method == "POST":
        WishlistItem.objects.filter(user=request.user, id=item_id).delete()

    next_url = request.POST.get("next")
    return redirect(next_url) if next_url else redirect("wishlist")


@login_required(login_url="login")
def move_wishlist_item_to_cart(request, item_id):
    """Adds the wishlist row's underlying item to the cart, then removes
    it from the wishlist — the standard 'move to cart' action."""
    if request.method == "POST":
        wishlist_item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
        if wishlist_item.product_id:
            _add_or_increment(request.user, product=wishlist_item.product)
        elif wishlist_item.prebuilt_pc_id:
            _add_or_increment(request.user, prebuilt_pc=wishlist_item.prebuilt_pc)
        elif wishlist_item.accessory_id:
            _add_or_increment(request.user, accessory=wishlist_item.accessory)
        wishlist_item.delete()

    return redirect("wishlist")


@login_required(login_url="login")
def wishlist_view(request):
    items = (
        WishlistItem.objects.filter(user=request.user)
        .select_related("product", "prebuilt_pc", "accessory")
    )

    wishlist_items = []
    for wi in items:
        item = wi.item
        price_display = format_inr(item.price) if item else "0"
        wishlist_items.append({
            "wishlist_item_id": wi.id,
            "item": item,
            "is_prebuilt": wi.prebuilt_pc_id is not None,
            "is_accessory": wi.accessory_id is not None,
            "price_display": price_display,
            "in_stock": bool(item and item.stock > 0),
        })

    return render(request, "wishlist.html", {
        "wishlist_items": wishlist_items,
        "cart_count": _cart_count(request),
    })