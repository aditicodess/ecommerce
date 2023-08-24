from cmath import log
from tkinter import E
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from base.decorators import customer_required
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from base.helper import save_pdf
from base.emails import send_email_with_order_confirmation_pdf
from .models import Profile, Vendor, User
from products.models import *
from accounts.models import Cart, CartItems
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model

# User = get_user_model()


class signup_page(TemplateView):
    template_name = "accounts/signup_form.html"


def customer_login_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user_obj = User.objects.filter(username=email)

        if not user_obj.exists():
            messages.warning(request, "Account not found.")
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username=email, password=password)
        if user_obj:
            login(request, user_obj)
            return redirect("/")

        messages.warning(request, "Invalid credentials")
        return HttpResponseRedirect(request.path_info)

    return render(request, "accounts/login.html")


def customer_register_page(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        user_obj = User.objects.filter(username=email)

        if user_obj.exists():
            messages.warning(request, "Email is already taken.")
            return HttpResponseRedirect(request.path_info)

        print(email, "from registeration page")

        user_obj = User.objects.create(
            first_name=first_name, last_name=last_name, email=email, username=email
        )
        user_obj.set_password(password)
        user_obj.is_customer = True
        user_obj.save()
        Profile.objects.create(user=user_obj)

        messages.success(request, "An email has been sent on your mail.")
        return HttpResponseRedirect(request.path_info)

    return render(request, "accounts/register.html")


def vendor_register_page(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        user_obj = User.objects.filter(username=email)

        if user_obj.exists():
            messages.warning(request, "Email is already taken.")
            return HttpResponseRedirect(request.path_info)

        print(email, "from registeration page")

        user_obj = User.objects.create(
            first_name=first_name, last_name=last_name, email=email, username=email
        )
        user_obj.set_password(password)
        user_obj.is_vendor = True
        user_obj.save()
        Vendor.objects.create(user=user_obj)

        messages.success(request, "An email has been sent on your mail.")
        return HttpResponseRedirect(request.path_info)

    return render(request, "accounts/register.html")


@login_required
@customer_required
def add_to_cart(request, uid):
    variant = request.GET.get("variant")

    product = Product.objects.get(uid=uid)
    user = request.user
    print(user)
    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)
    print(cart)
    cart_item = CartItems.objects.create(cart=cart, product=product)

    if variant:
        variant = request.GET.get("variant")
        Size_variant = SizeVariant.objects.get(size_name=variant)
        cart_item.size_variant = Size_variant
        cart_item.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@customer_required
def remove_cart(request, cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid=cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
@customer_required
def cart(request):
    print(request.user)
    cart_obj = None
    try:
        cart_obj = Cart.objects.get(is_paid=False, user=request.user)
    except Exception as e:
        print(e)

    if request.method == "POST":
        coupon = request.POST.get("coupon")
        coupon_obj = Coupon.objects.filter(coupon_code__icontains=coupon)
        if not coupon_obj.exists():
            messages.warning(request, "Invalid Coupon.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if cart_obj.coupon:
            messages.warning(request, "Coupon already exists.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        print(cart_obj.get_cart_total())
        if cart_obj.get_cart_total() < coupon_obj[0].minimum_amount:
            messages.warning(
                request, f"Amount should be greater than {coupon_obj[0].minimum_amount}"
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if coupon_obj[0].is_expired:
            messages.warning(request, f"Coupon expired.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        cart_obj.coupon = coupon_obj[0]
        cart_obj.save()
        messages.success(request, "Coupon applied.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    context = {"cart": cart_obj}
    return render(request, "accounts/cart.html", context)


@login_required
@customer_required
def remove_coupon(request, cart_id):
    cart = Cart.objects.get(uid=cart_id)
    cart.coupon = None
    cart.save()
    messages.success(request, "Coupon Removed.")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


# new
@csrf_exempt
def stripe_config(request):
    if request.method == "GET":
        stripe_config = {"publicKey": settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == "GET":
        domain_url = "http://localhost:8000/accounts/"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        cart_obj = Cart.objects.get(is_paid=False, user=request.user.id)
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "cancelled/",
                payment_method_types=["card"],
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "unit_amount": cart_obj.get_cart_total() * 100,
                            "product_data": {
                                "name": "t - shirt",
                                "description": "Comfortable cotton t-shirt",
                                "images": ["https://example.com/t-shirt.png"],
                            },
                        },
                        "quantity": 1,
                    }
                ],
            )
            cart_obj.stripe_pay_session_id = checkout_session["id"]
            cart_obj.save()
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            return JsonResponse({"error": str(e)})


def success(request):
    session_id = request.GET.get("session_id")
    cart = Cart.objects.get(stripe_pay_session_id=session_id)
    cart.is_paid = True
    cart.save()
    file_name, _ = save_pdf({"cart": cart})
    subject = "Order Confirmation Details"
    message = "This is the Order Confirmation Email. We have Attached all the required details in this Email."
    recipient_list = (request.user.email,)
    print(request.user.email)
    file_path = str(settings.BASE_DIR) + f"/public/static/{file_name}.pdf"
    send_email_with_order_confirmation_pdf(subject, message, recipient_list, file_path)
    return render(request, "pdfs/invoice.html", {"cart": cart})


def cancel(request):
    return render(request, "accounts/cancel.html")


# def invoice(request):
#     return render(request, "pdfs/invoice.html")
