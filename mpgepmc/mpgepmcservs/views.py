from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from decimal import Decimal
from .models import ServiceClass, Service, Package, PaymentMethod, Order

CART_SESSION_KEY = 'cart'

# --- Cart Helpers (Using Session) ---

def get_cart(request):
    """Retrieves the cart dictionary from the session."""
    return request.session.get(CART_SESSION_KEY, {})

def save_cart(request, cart):
    """Saves the updated cart dictionary back to the session."""
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True

def calculate_cart_total(cart):
    """Calculates the total minimum and maximum price for items in the cart."""
    min_total = Decimal('0.00')
    max_total = Decimal('0.00')
    for package_id, quantity in cart.items():
        try:
            package = Package.objects.get(id=package_id)
            min_total += package.min_price_usd * quantity
            max_total += package.max_price_usd * quantity
        except Package.DoesNotExist:
            continue
    return min_total, max_total

# --- Page Views ---

def service_class_list(request):
    """Index Page: Lists all Service Classes."""
    classes = ServiceClass.objects.all().prefetch_related('services')
    return render(request, 'mpgepmcservs/index.html', {'classes': classes})

def service_class_detail(request, class_slug):
    """Class Detail Page: Lists all Services within a specific Service Class."""
    service_class = get_object_or_404(ServiceClass, slug=class_slug)
    services = Service.objects.filter(service_class=service_class)
    return render(request, 'mpgepmcservs/service_class_detail.html', {
        'service_class': service_class, 
        'services': services
    })

def service_detail(request, class_slug, service_slug):
    """Service Detail Page: Lists all Packages for a specific Service."""
    service = get_object_or_404(Service, slug=service_slug, service_class__slug=class_slug)
    packages = Package.objects.filter(service=service, is_active=True).prefetch_related('features')
    
    # Get the current cart to highlight 'Add to Cart' status
    cart = get_cart(request)
    
    return render(request, 'mpgepmcservs/service_detail.html', {
        'service': service, 
        'packages': packages,
        'class_slug': class_slug,
        'cart': cart
    })

# --- Cart Views ---

def add_to_cart(request, package_id):
    """Adds a package to the session cart."""
    package = get_object_or_404(Package, id=package_id, is_active=True)
    cart = get_cart(request)
    
    # Check if the button type allows adding to cart
    if package.button_type == 'CART':
        quantity = cart.get(str(package_id), 0)
        cart[str(package_id)] = quantity + 1
        save_cart(request, cart)
        
    # Redirect back to the service detail page or a confirmation message
    return redirect(request.META.get('HTTP_REFERER', reverse('index')))

def remove_from_cart(request, package_id):
    """Removes a package from the session cart."""
    cart = get_cart(request)
    package_id_str = str(package_id)
    
    if package_id_str in cart:
        del cart[package_id_str]
        save_cart(request, cart)
        
    return redirect('cart_detail')

def cart_detail(request):
    """Cart Page: Displays items currently in the session cart."""
    cart = get_cart(request)
    cart_items = []
    
    for package_id_str, quantity in cart.items():
        try:
            package = Package.objects.get(id=int(package_id_str))
            cart_items.append({
                'package': package,
                'quantity': quantity,
                'line_min_total': package.min_price_usd * quantity,
                'line_max_total': package.max_price_usd * quantity,
            })
        except Package.DoesNotExist:
            # Clean up cart if package no longer exists
            del cart[package_id_str]
            save_cart(request, cart)
            continue

    min_total, max_total = calculate_cart_total(cart)
    
    return render(request, 'mpgepmcservs/cart.html', {
        'cart_items': cart_items, 
        'min_total': min_total, 
        'max_total': max_total
    })

def payment_page(request):
    """Payment Page: Displays payment methods and initiates checkout."""
    cart = get_cart(request)
    cart_items = cart_detail(request).context_data['cart_items'] # Re-use cart data logic
    min_total, max_total = calculate_cart_total(cart)
    
    if not cart_items:
        # Redirect to index if cart is empty
        return redirect('index') 
    
    payment_methods = PaymentMethod.objects.filter(is_visible=True).order_by('sort_order')

    if request.method == 'POST':
        selected_method_code = request.POST.get('payment_method')
        selected_method = get_object_or_404(PaymentMethod, code=selected_method_code)

        if selected_method.is_enabled:
            # For simplicity, we use the max price as the final amount for the order creation
            final_amount = max_total
            
            # 1. Create Order Record (using the max price as the estimate)
            order = Order.objects.create(
                session_key=request.session.session_key, 
                total_amount=final_amount
            )
            
            # 2. Clear the cart
            request.session[CART_SESSION_KEY] = {}
            request.session.modified = True
            
            # 3. Redirect to completion page
            return redirect('checkout_complete')
        else:
            # Add error message (not implemented in this simple example, but good practice)
            pass

    return render(request, 'mpgepmcservs/payment.html', {
        'cart_items': cart_items,
        'min_total': min_total,
        'max_total': max_total,
        'payment_methods': payment_methods
    })

def checkout_complete(request):
    """Order Confirmation Page."""
    return render(request, 'mpgepmcservs/checkout_complete.html')
