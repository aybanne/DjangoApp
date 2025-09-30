# store/context_processors.py
from .models import Order

def active_order(request):
    """
    Adds the current user's active (unpaid) order to the template context.
    """
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, paid=False).first()
    else:
        order = None

    return {'active_order': order}
