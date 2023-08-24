from django.http import HttpResponse
from django.shortcuts import render
from products.models import Product


def index(request):
    context = {"products": Product.objects.all()}
    return render(request, "home/index.html", context)


def get_product(request, slug):
    try:
        print("start here 1")
        product = Product.objects.filter(slug=slug).first
        context = {"product": product}
        print("start here 2")
        if request.GET.get("size"):
            size = request.GET.get("size")
            print(size)
            price = product.get_product_price_by_size(size)
            context["selected_size"] = size
            context["updated_price"] = price
            print(price)

        return render(request, "product/product.html", context=context)

    except Exception as e:
        print(e)
        return HttpResponse({"status": 404, "message": "Not Found"})
