from pydoc import render_doc
from tkinter import E
from django.shortcuts import render
from home.views import index
from products.models import ColorVariant, SizeVariant, Category, ProductImage
from products.models import Product
from django.contrib.auth.decorators import login_required
from base.decorators import customer_required, vendor_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect


# @login_required
# @vendor_required
def create_product(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        category = Category.objects.get(uid=request.POST.get("category"))
        price = request.POST.get("price")
        product_description = request.POST.get("product_description")
        product_obj = Product.objects.filter(
            product_name=product_name,
        )

        if product_obj.exists():
            messages.warning(request, "Product has Already Created.")
            return HttpResponseRedirect(request.path_info)

        print(product_name, "from registeration page")

        product_obj = Product.objects.create(
            product_name=product_name,
            category=category,
            price=price,
            product_description=product_description,
        )
        product_obj.save()
        color_variant = ColorVariant.objects.get(uid=request.POST.get("color_variant"))
        size_variant = SizeVariant.objects.get(uid=request.POST.get("size_variant"))
        product_obj.color_variant.add(color_variant)
        product_obj.size_variant.add(size_variant)

        messages.success(request, "Product ", product_name, "Created Successfully")
        return HttpResponseRedirect(request.path_info)
    else:
        context = {
            "category_list": Category.objects.all(),
            "color_variant_list": ColorVariant.objects.all(),
            "size_variant_list": SizeVariant.objects.all(),
        }
        return render(request, "product/create_product.html", context=context)


def upload_product_image(request):
    if request.method == "POST":
        product = Product.objects.get(uid=request.POST.get("product"))
        image = request.POST.get("image")

        print(product, "from registeration page")

        image_obj = ProductImage.objects.create(
            product=product,
            image=image,
        )
        image_obj.save()
        messages.success(request, "Product ", product, "Created Successfully")
        return HttpResponseRedirect(request.path_info)
    else:
        context = {
            "product_list": Product.objects.all(),
        }
        return render(request, "product/upload_product_images.html", context=context)


@login_required
@vendor_required
def delete_product(request, slug):
    print(request.method)
    product = Product.objects.get(slug=slug)
    if request.method == "POST":
        try:
            product.delete()
            return HttpResponseRedirect("/")

        except ObjectDoesNotExist:
            return HttpResponse({"status": 404, "message": "Not Found"})

    else:
        return render(request, "product/delete_product.html", {"product": product})
