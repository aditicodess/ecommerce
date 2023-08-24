from django.urls import path
from accounts.views import (
    customer_login_page,
    add_to_cart,
    remove_coupon,
    customer_register_page,
    vendor_register_page,
    signup_page,
    cart,
    remove_cart,
    stripe_config,
    create_checkout_session,
    success,
    cancel,
)

urlpatterns = [
    path("login/customer/", customer_login_page, name="customer_login"),
    path("register/customer/", customer_register_page, name="customer_signup"),
    path("register/vendor/", vendor_register_page, name="vendor_signup"),
    path("signup/", signup_page.as_view(), name="signup"),
    path("cart/", cart, name="cart"),
    path("add-to-cart/<uid>/", add_to_cart, name="add_to_cart"),
    path("remove-cart/<cart_item_uid>/", remove_cart, name="remove_cart"),
    path("remove-coupon/<cart_id>/", remove_coupon, name="remove_coupon"),
    path("config/", stripe_config),
    path("create-checkout-session/", create_checkout_session),
    path("success/", success),
    path("cancelled/", cancel),
]
