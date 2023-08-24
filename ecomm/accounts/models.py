from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.contrib.auth.models import AbstractUser
import uuid
from products.models import ColorVariant, Coupon, Product, SizeVariant


class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.ImageField(upload_to="profile")

    def get_cart_count(self):
        return CartItems.objects.filter(
            cart__is_paid=False, cart__user=self.user
        ).count()

    def __str__(self):
        return self.user.username


class Vendor(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor")
    vendor_image = models.ImageField(upload_to="vendor")
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.user.username


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    stripe_pay_session_id = models.CharField(max_length=100, null=True, blank=True)

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price = []
        for cart_item in cart_items:
            price.append(cart_item.product.price)
            if cart_item.color_variant:
                color_variant_price = cart_item.color_variant.price
                price.append(color_variant_price)
            if cart_item.size_variant:
                size_variant_price = cart_item.size_variant.price
                price.append(size_variant_price)

        if self.coupon:
            if self.coupon.minimum_amount < sum(price):
                return sum(price) - self.coupon.discount_price

        return sum(price)


class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product",
    )
    color_variant = models.ForeignKey(
        ColorVariant, on_delete=models.SET_NULL, null=True, blank=True
    )
    size_variant = models.ForeignKey(
        SizeVariant, on_delete=models.SET_NULL, null=True, blank=True
    )

    def get_product_price(self):
        price = [self.product.price]

        if self.color_variant:
            color_variant_price = self.color_variant.price
            price.append(color_variant_price)
        if self.size_variant:
            size_variant_price = self.size_variant.price
            price.append(size_variant_price)
        return sum(price)
