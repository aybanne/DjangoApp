from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Sum

# Home view
def home(request):
    products = Product.objects.all()

    # Get filters from GET request
    query = request.GET.get("q")
    category = request.GET.get("category")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # Apply filters
    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category__name__icontains=category)  # only works if you have Category model/field

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        "products": products,
    }
    return render(request, "store/home.html", context)

# Add product to cart
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

# View the cart
@login_required
def cart_view(request):
    order = Order.objects.filter(user=request.user, paid=False).first()
    return render(request, "store/cart.html", {"order": order})

# Checkout view
@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, paid=False).first()
    if not order or not order.items.exists():
        return redirect('home')

    if request.method == "POST":
        # You can integrate payment gateway here
        order.paid = True
        order.shipping_address = request.POST.get("shipping_address", "")
        order.save()
        return redirect('order_success')

    return render(request, "store/checkout.html", {"order": order})

# Order success page
@login_required
def order_success(request):
    return render(request, "store/order_success.html")

@login_required
def dashboard(request):
    # Get filters
    status = request.GET.get("status")   # paid/unpaid
    category = request.GET.get("category")
    days = request.GET.get("days")

    # Base Query
    orders = Order.objects.all()
    products = Product.objects.all()

    # Filter by status
    if status == "paid":
        orders = orders.filter(paid=True)
    elif status == "unpaid":
        orders = orders.filter(paid=False)

    # Filter by category
    if category:
        products = products.filter(category__name=category)

    # Filter by recent days
    if days:
        try:
            days = int(days)
            start_date = now() - timedelta(days=days)
            orders = orders.filter(created_at__gte=start_date)
        except:
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
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user,
        order__paid=False
    )
    item.delete()
    return redirect('cart')

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

def home(request):
    products = Product.objects.all()

    # Distinct category list (id, name)
    categories = Product.objects.values_list("category__id", "category__name").distinct()

    # Get selected categories from query params
    selected_categories = request.GET.getlist("category")

    # Filter if any selected, else show all
    if selected_categories:
        products = products.filter(category__id__in=selected_categories)

    context = {
        "products": products,
        "categories": categories,
        "selected_categories": selected_categories,
    }
    return render(request, "store/home.html", context)
