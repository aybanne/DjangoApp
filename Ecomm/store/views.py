from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.utils.timezone import now
from datetime import timedelta
from .models import Product, Order, OrderItem


# ------------------------------
# HOME / PRODUCT LISTING
# ------------------------------
def home(request):
    products = Product.objects.all()

    # Distinct category list (id, name)
    categories = Product.objects.values_list("category__id", "category__name").distinct()

    # Get filters from query params
    query = request.GET.get("q", "")
    selected_categories = [c for c in request.GET.getlist("category") if c]  # ignore empty "None"
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # Apply search filter
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # Apply category filter
    if selected_categories:
        products = products.filter(category__id__in=selected_categories)

    # Apply price range filter
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        "products": products,
        "categories": categories,
        "selected_categories": selected_categories,
        "query": query,
        "min_price": min_price,
        "max_price": max_price,
    }
    return render(request, "store/home.html", context)


# ------------------------------
# CART / ADD TO CART
# ------------------------------
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get or create active order for the user
    order, created = Order.objects.get_or_create(user=request.user, paid=False)

    # Read quantity from POST (default = 1)
    quantity = int(request.POST.get("quantity", 1))

    # Get or create order item
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={'price': product.price, 'quantity': quantity}
    )

    if not created:
        # If item already exists, increase its quantity
        order_item.quantity += quantity
        order_item.save()

    return redirect('cart')


# ------------------------------
# VIEW CART
# ------------------------------
@login_required
def cart_view(request):
    order = Order.objects.filter(user=request.user, paid=False).first()
    return render(request, "store/cart.html", {"order": order})


# ------------------------------
# UPDATE CART ITEM QUANTITY
# ------------------------------
@login_required
def update_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__paid=False)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "increase":
            item.quantity += 1
            item.save()
        elif action == "decrease":
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()  # remove item if quantity goes to 0

    return redirect("cart")


# ------------------------------
# REMOVE ITEM FROM CART
# ------------------------------
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__paid=False)
    item.delete()
    return redirect('cart')


# ------------------------------
# CHECKOUT
# ------------------------------
@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, paid=False).first()
    if not order or not order.items.exists():
        return redirect('home')

    if request.method == "POST":
        # Integrate payment gateway here if needed
        order.paid = True
        order.shipping_address = request.POST.get("shipping_address", "")
        order.save()
        return redirect('order_success')

    return render(request, "store/checkout.html", {"order": order})


# ------------------------------
# ORDER SUCCESS
# ------------------------------
@login_required
def order_success(request):
    return render(request, "store/order_success.html")


# ------------------------------
# DASHBOARD
# ------------------------------
@login_required
def dashboard(request):
    # Filters
    status = request.GET.get("status")  # paid/unpaid
    category = request.GET.get("category")
    days = request.GET.get("days")

    # Base Query
    orders = Order.objects.all()
    products = Product.objects.all()

    # Filter by order status
    if status == "paid":
        orders = orders.filter(paid=True)
    elif status == "unpaid":
        orders = orders.filter(paid=False)

    # Filter products by category
    if category:
        products = products.filter(category__name=category)

    # Filter orders by recent days
    if days:
        try:
            days = int(days)
            start_date = now() - timedelta(days=days)
            orders = orders.filter(created_at__gte=start_date)
        except ValueError:
            pass

    # Dashboard summary
    total_sales = orders.filter(paid=True).aggregate(total=Sum("items__price"))["total"] or 0
    total_orders = orders.count()
    total_products = products.count()

    context = {
        "orders": orders,
        "products": products,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "total_products": total_products,
    }
    return render(request, "store/dashboard.html", context)

@login_required
def manage_orders(request):
    # Get orders for the logged-in user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        "orders": orders,
    }
    return render(request, "store/manage_orders.html", context)