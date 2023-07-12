from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import viewsets
from .serializers import RegistrationSerializer

# Create your views here.


def index(request):

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

    category = Category.objects.all()

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
        return redirect("home")


def login(request):
    if request.method == 'POST':
        email = request.POST.get('emailid')
        password = request.POST.get('password')

        try:
            email_id = Registration.objects.get(email=email)
            if email_id:
                if check_password(password, email_id.password):
                    request.session['name'] = email_id.first_name
                    request.session['customer_id'] = email_id.id
                    return redirect('home')
                else:
                    return HttpResponse("Wrong Password!")
        except:
            return HttpResponse("Wrong Email Address!")


def logout(request):
    request.session.clear()
    return redirect('home')


def cart_details(request):

    try:
        ids = list(request.session.get('cart').keys())
        cart_info = Product.objects.filter(id__in=ids)
        error = None
        line = None
    except:
        cart_info = None
        if request.session.get('name'):
            error = "Your Cart is empty!"
            line = "Add items to your cart."
        else:
            error = "Missing Cart items?"
            line = "Login to see the items you added previously"

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


def order_details(request):

    customer_id = request.session.get('customer_id')
    ord_details = Order.objects.filter(customer=customer_id)
    tp = 0
    for i in ord_details:
        tp = tp + (i.price * i.quantity)

    context = {
        'order': ord_details,
        'tp': tp,
    }

    return render(request, 'order.html', context=context)


# ViewSets define the view behavior.
class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
