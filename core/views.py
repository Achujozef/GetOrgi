from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Category, Product, OrgiUser, CartItem, Delivery,Address,Order, OrderItem

def landing_page(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    cart_quantities = {}

    if "mobile" in request.session:
        user = OrgiUser.objects.get(mobile=request.session["mobile"])
        cart_items = CartItem.objects.filter(user=user)
        cart_quantities = {item.product.id: item.quantity for item in cart_items}
        print("cart_quantities",cart_quantities)
        cart_count = cart_items.count()
    else:
        print("User Not Found")
        cart_count = 0

    return render(request, 'landing.html', {
        'categories': categories,
        'products': products,
        'cart_quantities': cart_quantities,
        'cart_count': cart_count
    })



def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    similar_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:10]
    return render(request, 'product_detail.html', {
        'product': product,
        'similar_products': similar_products,
    })

def cart_view(request):

    if "mobile" in request.session:
        user_mobile = request.session["mobile"]
        user = OrgiUser.objects.get(mobile=user_mobile)


        cart_items = CartItem.objects.filter(user=user)


        total = sum([item.product.price * item.quantity for item in cart_items])


        delivery_charge = Delivery.objects.first().charge


        final_total = total + delivery_charge

        return render(request, 'cart.html', {
            'cart_items': cart_items,
            'total': total,
            'delivery_charge': delivery_charge,
            'final_total': final_total
        })
    else:
        messages.error(request, "Please login with your mobile number to continue shopping.")
        return redirect('login') 


def update_cart(request):
    if request.method == "POST":
        cart_item_id = request.POST.get('cart_item_id')
        action = request.POST.get('action')

        cart_item = CartItem.objects.get(id=cart_item_id)

        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease" and cart_item.quantity > 1:
            cart_item.quantity -= 1

        cart_item.save()

        return JsonResponse({'status': 'success', 'new_quantity': cart_item.quantity, 'new_total': cart_item.product.price * cart_item.quantity})
    
def login_view(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile', '').strip()

        if not mobile:
            messages.error(request, "Mobile number is required.")
            return redirect('login')

        if not mobile.isdigit() or len(mobile) < 10:
            messages.error(request, "Enter a valid mobile number.")
            return redirect('login')

        user, created = OrgiUser.objects.get_or_create(mobile=mobile)

        request.session['user_id'] = user.id
        request.session['mobile'] = user.mobile  

        messages.success(request, f"Welcome, {mobile}! Continue shopping.")
        return redirect('cart')

    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('login')

def address_list_view(request):
    if 'mobile' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = OrgiUser.objects.get(mobile=request.session['mobile'])

    # Fetch the user's addresses
    addresses = Address.objects.filter(user=user)

    # If no address exists, show a message and allow the user to add a new one
    if not addresses:
        return render(request, 'address_list.html', {'addresses': addresses, 'no_addresses': True})

    return render(request, 'address_list.html', {'addresses': addresses})

def save_address(request):
    if 'mobile' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = OrgiUser.objects.get(mobile=request.session['mobile'])

    if request.method == 'POST':
        Address.objects.create(
            user=user,
            latitude=request.POST.get('latitude'),
            longitude=request.POST.get('longitude'),
            full_address=request.POST.get('full_address'),
            customer_name=request.POST.get('customer_name'),
            Landmark = request.POST.get('landmark', ''),
            phone=request.POST.get('phone')
        )
        messages.success(request, "Address saved!")
        return redirect('address_list')  # or wherever you want to redirect

    return render(request, 'save_address.html')

def address_detail(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    return render(request, 'address_detail.html', {'address': address})



from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
@csrf_exempt
def update_cart_ajax(request):
    if request.method == "POST" and "mobile" in request.session:
        product_id = request.POST.get("product_id")
        action = request.POST.get("action")

        user = OrgiUser.objects.get(mobile=request.session["mobile"])
        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)

        if action == "increase":
            if created:
                cart_item.quantity = 1
            else:
                cart_item.quantity += 1
            cart_item.save()

        elif action == "decrease":
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                cart_item.delete()
                new_quantity = 0
            else:
                cart_item.save()
                new_quantity = cart_item.quantity
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid action'})

        # Subtotal for this item
        item_subtotal = cart_item.quantity * product.price if action != "decrease" or cart_item.quantity > 0 else 0

        # 🧮 Recalculate total cart value for the user
        cart_items = CartItem.objects.filter(user=user)
        total = sum(item.product.price * item.quantity for item in cart_items)

        # 🧮 Updated cart count (number of items, not total quantity)
        cart_count = cart_items.count()

        return JsonResponse({
            'status': 'success',
            'new_quantity': new_quantity if action == 'decrease' else cart_item.quantity,
            'item_subtotal': item_subtotal,
            'total': total,
            'cart_count': cart_count
        })

    return JsonResponse({'status': 'error'})

# @login_required
def place_order_from_cart(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    if not cart_items:
        return redirect('cart')

    address = Address.objects.filter(user=user).first()  # Get first address for now

    total = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(user=user, address=address, total_amount=total)

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    cart_items.delete()

    return render(request, 'order_success.html', {'order': order})

@login_required
def buy_now(request, product_id):
    user = request.user
    product = Product.objects.get(id=product_id)
    address = Address.objects.filter(user=user).first()

    order = Order.objects.create(user=user, address=address, total_amount=product.price)

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )

    return render(request, 'order_success.html', {'order': order})

import razorpay
from django.conf import settings

from .models import Address

def order_summary(request):
    user = OrgiUser.objects.get(mobile=request.session["mobile"])
    cart_items = CartItem.objects.filter(user=user)
    delivery_charge = Delivery.objects.first().charge if Delivery.objects.exists() else 0
    total = sum([item.subtotal() for item in cart_items])
    grand_total = total + delivery_charge

    selected_address_id = request.session.get("selected_address_id")
    selected_address = Address.objects.get(id=selected_address_id) if selected_address_id else None

    # Razorpay order setup
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
    payment = client.order.create({
        "amount": int(grand_total * 100),
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "cart_items": cart_items,
        "total": total,
        "delivery": delivery_charge,
        "grand_total": grand_total,
        "razorpay_order_id": payment["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "selected_address": selected_address,
    }
    return render(request, "order_summary.html", context)

import json
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature"]
            })
            # Create Order from cart items here
            # Clear cart if needed
            return JsonResponse({"status": "success"})
        except:
            return JsonResponse({"status": "failed"})

    return JsonResponse({"status": "invalid"})

from django.shortcuts import redirect
from django.contrib import messages
from .models import Address

def set_selected_address(request):
    if request.method == "POST":
        address_id = request.POST.get("address_id")
        request.session["selected_address_id"] = address_id
        return redirect("order_summary")
    messages.error(request, "Please select a valid address.")
    return redirect("address_list")
