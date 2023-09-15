from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
# from rest_framework import viewsets
# from .serializers import RegistrationSerializer
from playsound import playsound
import os
import threading
from django.db.models import Q

# Create your views here.


def index(request):

    category = Category.objects.all()
    products = None

    if request.method == 'POST':
        product_id = request.POST.get('cartid')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')

        if cart:
            quantity = cart.get(product_id)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product_id)
                    else:
                        cart[product_id] = quantity - 1
                else:
                    cart[product_id] = quantity + 1
            else:
                cart[product_id] = 1
        else:
            cart = {}
            cart[product_id] = 1
        request.session['cart'] = cart

        referer_url = request.META.get('HTTP_REFERER', None)
        if referer_url:
            return redirect(referer_url)

    if 'q' in request.GET:
        query = request.GET.get('q')
        if not query.strip():  # Check if the query is empty
            toast_with_sound(
                request, "What are you searching for? Please enter a search query before proceeding with the search.", "error.mp3", messages.ERROR)
            return redirect('home')
        else:
            results = Product.objects.filter(
                Q(pro_name__icontains=query) | Q(pro_desc__icontains=query)
            )
            return render(request, 'index.html', {'results': results, 'query': query})

    else:
        cate = request.GET.get('category_id')
        if cate:
            products = Product.objects.filter(category=cate)
        else:
            products = Product.objects.all()

    context = {
        'category': category,
        'products': products
    }
    return render(request, 'index.html', context=context)


def sign_up(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('pwd')
        mobile = request.POST.get('mbl')
        gender = request.POST.get('gender')

        reg_obj = Registration(
            first_name=fname,
            last_name=lname,
            email=email,
            password=make_password(password),
            mobile=mobile,
            gender=gender,
        )
        reg_obj.save()
        toast_with_sound(
            request, f"Congratulations, {fname}! You have successfully signed up for our service. Please log in with your email and password to access your account.", "sign-up.mp3", messages.SUCCESS)
        return redirect("home")


def login(request):
    next = request.GET.get('next', request.path)
    if request.method == 'POST':
        email = request.POST.get('emailid')
        password = request.POST.get('password')

        try:
            email_id = Registration.objects.get(email=email)
            if email_id:
                if check_password(password, email_id.password):
                    request.session['name'] = email_id.first_name
                    request.session['customer_id'] = email_id.id
                    toast_with_sound(
                        request, f"Welcome back {email_id.first_name}! You have successfully logged in.", "login.mp3", messages.SUCCESS)
                    return redirect(next)
                else:
                    toast_with_sound(
                        request, "Oops, something went wrong! The email or password you entered does not match our records. Please check your spelling and try again.", "error.mp3", messages.ERROR)
                    return redirect(next)
        except:
            toast_with_sound(
                request, "Oops, something went wrong! The email or password you entered does not match our records. Please check your spelling and try again.", "error.mp3", messages.ERROR)
            return redirect(next)


def logout(request):

    request.session.clear()
    toast_with_sound(
        request, "You have successfully logged out. Thank you for using our service.", "login.mp3", messages.SUCCESS)
    return redirect('home')


def cart_details(request):
    cart = request.session.get('cart', {})
    ids = list(cart.keys())

    if ids:
        cart_info = Product.objects.filter(id__in=ids)
        error = None
        line = None
    elif request.session.get('name'):
        error = "Your Cart is empty!"
        line = "Add items to your cart."
        cart_info = None
    else:
        error = "Missing Cart items?"
        line = "Login to see the items you added previously"
        cart_info = None

    return render(request, 'cart.html', {'cart_info': cart_info, 'error': error, 'line': line})


def checkout(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        customer_id = request.session.get('customer_id')
        cart = request.session.get('cart')
        product = Product.objects.filter(id__in=list(cart.keys()))
        if customer_id:
            for pro in product:
                ord_save = Order(
                    address=address,
                    mobile=mobile,
                    quantity=cart.get(str(pro.id)),
                    customer=Registration(id=customer_id),
                    price=pro.pro_price,
                    product=pro
                )
                ord_save.save()
            return redirect('order')
        else:
            toast_with_sound(
                request, "Please log in to your account before proceeding to checkout.", "error.mp3", messages.WARNING)
            return redirect('cart')


def order_details(request):
    customer_id = request.session.get('customer_id')

    ord_details = Order.objects.filter(customer=customer_id, status='pending')

    tp = 0
    for order in ord_details:
        tp += (order.price * order.quantity)

    context = {
        'order': ord_details,
        'tp': tp,
    }

    return render(request, 'order.html', context=context)


def toast_with_sound(request, message, sound, level=messages.INFO):
    # Display a toast message with the specified level
    messages.add_message(request, level, message)
    # Get the path of the static folder
    static_path = os.path.join(os.path.dirname(__file__), "static")
    # Join the path of the sound file with the path of the static folder
    sound_path = os.path.join(static_path, "audio", sound)
    # Play a sound file
    t = threading.Thread(target=playsound, args=(sound_path,))
    t.start()


# ViewSets define the view behavior.
# class RegistrationViewSet(viewsets.ModelViewSet):
#     queryset = Registration.objects.all()
#     serializer_class = RegistrationSerializer
