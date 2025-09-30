from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem

# Home view
def home(request):
    products = Product.objects.all()  # get all products from DB
    return render(request, "store/home.html", {"products": products})

# Add product to cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Get or create active order for the user
    order, created = Order.objects.get_or_create(user=request.user, paid=False)
    # Get or create order item
    order_item, created = OrderItem.objects.get_or_create(
        order=order, product=product, defaults={'price': product.price}
    )
    if not created:
        order_item.quantity += 1
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
