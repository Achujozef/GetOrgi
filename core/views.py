from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Category, Product, OrgiUser, CartItem, Delivery,Address,Order, OrderItem, Review
import razorpay
from django.conf import settings
from .models import Address
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.shortcuts import redirect
from django.contrib import messages
import json
from django.db.models import Avg
from django.http import Http404
from django.core.paginator import Paginator

def landing_page(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(name__icontains=search_query) | products.filter(description__icontains=search_query)

    cart_quantities = {}

    if "mobile" in request.session:
        user = OrgiUser.objects.get(mobile=request.session["mobile"])
        cart_items = CartItem.objects.filter(user=user)
        cart_quantities = {item.product.id: item.quantity for item in cart_items}
        # print("cart_quantities",cart_quantities)
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

    cart_item = None
    cart_count = 0
    purchased = False
    already_reviewed = False

    if "mobile" in request.session:
        user_mobile = request.session["mobile"]
        user = OrgiUser.objects.get(mobile=user_mobile)
        cart_item = CartItem.objects.filter(user=user, product=product).first()
        cart_items = CartItem.objects.filter(user=user)
        cart_count = cart_items.count()
        purchased = OrderItem.objects.filter(order__user=user, product=product, order__is_paid=True).exists()
        already_reviewed = Review.objects.filter(user=user, product=product).exists()
        # print("already_reviewed, purchased :",already_reviewed, purchased)
    return render(request, 'product_detail.html', {
        'product': product,
        'similar_products': similar_products,
        'cart_item':cart_item,
        'cart_count':cart_count,
        'purchased': purchased,
        'already_reviewed': already_reviewed,
    })

def cart_view(request):

    if "mobile" in request.session:
        user_mobile = request.session["mobile"]
        user = OrgiUser.objects.get(mobile=user_mobile)


        cart_items = CartItem.objects.filter(user=user)


        total = sum([item.product.price * item.quantity for item in cart_items])


        delivery_charge = Delivery.objects.first().charge


        final_total = total + delivery_charge
        cart_items = CartItem.objects.filter(user=user)
        cart_count = cart_items.count()
        return render(request, 'cart.html', {
            'cart_items': cart_items,
            'total': total,
            'delivery_charge': delivery_charge,
            'final_total': final_total,
            'cart_count':cart_count
        })
    else:
        messages.error(request, "Please login with your mobile number to continue shopping.")
        return redirect('login') 


def update_cart(request):
    if 'mobile' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')
    
    if request.method == "POST":
        # print("Postil kerunnu")
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
        return redirect('/')

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
    cart_items = CartItem.objects.filter(user=user)
    cart_count = cart_items.count()
    # Fetch the user's addresses
    addresses = Address.objects.filter(user=user)

    # If no address exists, show a message and allow the user to add a new one
    if not addresses:
        return render(request, 'address_list.html', {'addresses': addresses, 'no_addresses': True, 'cart_count' : cart_count})

    return render(request, 'address_list.html', {'addresses': addresses, 'cart_count' : cart_count})

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
            phone=request.POST.get('phone'),
            city = request.POST.get('city'),
            pincode = request.POST.get('pincode')
        )
        messages.success(request, "Address saved!")
        return redirect('address_list')  # or wherever you want to redirect

    return render(request, 'save_address.html')

def address_detail(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    return render(request, 'address_detail.html', {'address': address})

def edit_address(request):
    if 'mobile' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = OrgiUser.objects.get(mobile=request.session['mobile'])

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        address = get_object_or_404(Address, id=address_id, user=user)

        address.customer_name = request.POST.get('customer_name')
        address.full_address = request.POST.get('full_address')
        address.Landmark = request.POST.get('landmark', '')
        address.phone = request.POST.get('phone')
        address.city = request.POST.get('city')
        address.pincode = request.POST.get('pincode')
        address.save()

        messages.success(request, "Address updated successfully!")
        return redirect('address_list')

    return redirect('address_list')


@csrf_exempt
def update_cart_ajax(request):
    if 'mobile' not in request.session:
        messages.error(request, "Please login first.")
        return JsonResponse({'status': 'error', 'message': 'Please login first.', 'redirect': 'login'})
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

def place_order_from_cart(request,):
    if "mobile" not in request.session:
        return redirect("login")

    request.session.pop("order_mode", None)
    request.session.pop("buy_now_product_id", None)
    return redirect("address_list")

def buy_now(request, product_id):
    if "mobile" not in request.session:
        return redirect("login")

    request.session["buy_now_product_id"] = product_id
    request.session["order_mode"] = "buy_now"  # this flag helps distinguish
    return redirect("address_list")



def order_summary(request):
    user = OrgiUser.objects.get(mobile=request.session["mobile"])
    delivery_charge = Delivery.objects.first().charge if Delivery.objects.exists() else 0
    selected_address_id = request.session.get("selected_address_id")
    selected_address = Address.objects.get(id=selected_address_id) if selected_address_id else None

    if request.session.get("order_mode") and request.session.get("order_mode") == "buy_now":
        product_id = request.session.get("buy_now_product_id")
        product = get_object_or_404(Product, id=product_id)
        quantity = 1
        total = product.price * quantity
        cart_items = [{
            'product': product,
            'quantity': quantity,
            'subtotal': total
        }]
    else:
        cart_items = CartItem.objects.filter(user=user)
        total = sum([item.subtotal() for item in cart_items])

    grand_total = total + delivery_charge

    # Razorpay
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
    payment = client.order.create({
        "amount": int(grand_total * 100),
        "currency": "INR",
        "payment_capture": "1"
    })
    cart_items_for_cart_icon = CartItem.objects.filter(user=user)
    cart_count = cart_items_for_cart_icon.count()
    context = {
        "cart_items": cart_items,
        "total": total,
        "delivery": delivery_charge,
        "grand_total": grand_total,
        "razorpay_order_id": payment["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "selected_address": selected_address,
        "order_mode": request.session.get("order_mode"),
        'cart_count' : cart_count
    }
    return render(request, "order_summary.html", context)


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
            user = OrgiUser.objects.get(mobile=request.session["mobile"])
            address = Address.objects.get(id=request.session["selected_address_id"])
            order_mode = request.session.get("order_mode")

            if order_mode == "buy_now":
                product_id = request.session.get("buy_now_product_id")
                product = Product.objects.get(id=product_id)
                order = Order.objects.create(user=user, address=address, total_amount=product.price,is_paid=True)
                OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)
                product.purchase_count += 1
                product.save()
                # Clear session flags
                del request.session["order_mode"]
                del request.session["buy_now_product_id"]
            else:
                cart_items = CartItem.objects.filter(user=user)
                total = sum(item.product.price * item.quantity for item in cart_items)
                order = Order.objects.create(user=user, address=address, total_amount=total)
                for item in cart_items:
                    OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
                    item.product.purchase_count += item.quantity
                    item.product.save()
                cart_items.delete()
                del request.session["order_mode"]

            return JsonResponse({"status": "success"})
        except:
            return JsonResponse({"status": "failed"})

    return JsonResponse({"status": "invalid"})

def set_selected_address(request):
    if request.method == "POST":
        address_id = request.POST.get("address_id")
        request.session["selected_address_id"] = address_id

        if request.session.get("order_mode") == "buy_now":
            return redirect("order_summary")  # redirect to single item summary
        return redirect("order_summary")  # or cart-based summary
    messages.error(request, "Please select a valid address.")
    return redirect("address_list")

@csrf_exempt
def submit_review(request):
    if request.method == "POST":
        try:
            user_mobile = request.session["mobile"]
            user = OrgiUser.objects.get(mobile=user_mobile)
            product_id = request.POST.get("product_id")
            rating = int(request.POST.get("rating"))
            comment = request.POST.get("comment")

            product = Product.objects.get(id=product_id)

            # Check if user already reviewed
            existing_review = Review.objects.filter(user=user, product=product).first()
            if existing_review:
                return JsonResponse({'status': 'error', 'message': 'You have already submitted a review.'})

            Review.objects.create(
                product=product,
                user=user,
                name="GetOrgi User", 
                comment=comment,
                rating=rating,
            )
            average_rating = Review.objects.filter(product=product).aggregate(avg_rating=Avg('rating'))['avg_rating']
            product.rating = round(average_rating, 2)  # keep 2 decimal places
            product.save()
            return JsonResponse({'status': 'success', 'message': 'Review submitted successfully.'})

        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def contact_us(request):
    return render(request, 'contact_us.html')

def about_us(request):
    return render(request, 'about_us.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_conditions(request):
    return render(request, 'terms_conditions.html')

def return_policy(request):
    return render(request, 'return_policy.html')

def user_profile(request):
    if 'mobile' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = OrgiUser.objects.get(mobile=request.session['mobile'])

    # Fetch user orders (latest first)
    orders = Order.objects.filter(user=user).order_by('-created_at')

    # Fetch user addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'orders': orders,
        'addresses': addresses
    }

    return render(request, 'user_profile.html', context)

def edit_address_for_user_profile(request, address_id):
    # Fetch the address to edit
    address = get_object_or_404(Address, id=address_id)

    if request.method == 'POST':
        # Update the address fields
        address.customer_name = request.POST.get('customer_name')
        address.full_address = request.POST.get('full_address')
        address.city = request.POST.get('city')
        address.pincode = request.POST.get('pincode')
        address.phone = request.POST.get('phone')

        # Save the changes to the database
        address.save()

        # Provide feedback to the user
        messages.success(request, "Address updated successfully!")

        # Redirect back to the user profile page
        return redirect('user_profile')  # Replace with the correct URL name

    return render(request, 'edit_address.html', {'address': address})

def load_more_orders(request):
    if 'mobile' not in request.session:
        return JsonResponse({'error': 'Please login first.'}, status=400)

    user = OrgiUser.objects.get(mobile=request.session['mobile'])
    
    # Fetch orders for the user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_obj = paginator.get_page(page_number)

    # Prepare the response data
    orders_data = []
    for order in page_obj.object_list:
        order_data = {
            'id': order.id,
            'created_at': order.created_at,
            'total_amount': order.total_amount,
            'is_paid': order.is_paid,
        }
        orders_data.append(order_data)

    return JsonResponse({
        'orders': orders_data,
        'has_next': page_obj.has_next(),  # To check if there's more to load
    })

@csrf_exempt
def delete_cart_item(request):
    if request.method == "POST":
        cart_item_id = request.POST.get('cart_item_id')
        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            user = cart_item.user
            cart_item.delete()

            # Recalculate total
            cart_items = CartItem.objects.filter(user=user)
            total = sum([item.subtotal() for item in cart_items])
            cart_count = cart_items.count()

            return JsonResponse({'success': True, 'total': total, 'cart_count': cart_count})
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def order_detail(request, order_id):
    if 'mobile' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = OrgiUser.objects.get(mobile=request.session['mobile'])
    order = get_object_or_404(Order, id=order_id, user=user)

    # Prepare status choices and current status index
    status_choices = order.STATUS_CHOICES  # list of tuples e.g. [('pending', 'Pending'), ...]
    status_keys = [choice[0] for choice in status_choices]
    current_status_index = status_keys.index(order.status) if order.status in status_keys else -1

    context = {
        'order': order,
        'status_choices': status_choices,
        'current_status_index': current_status_index,
    }
    return render(request, 'order_detail.html', context)


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['placed', 'packed']:
        order.status = 'cancelled'
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled.")
    else:
        messages.warning(request, "This order cannot be cancelled at this stage.")

    return redirect('order_detail', order_id=order.id)