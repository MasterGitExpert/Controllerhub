from django.shortcuts import render
from .models import Product

# Create your views here.


def home(request):
    return render(request, "index.html")


def products(request):
    """
        Returns a rendered view to display all products with search and
        sort functionality
    """
    # Get all products that are marked for display
    products = Product.objects.all().filter(display_item=True)
    # Update sale price to price for all products not on discount
    # this for price ordering purposes and check stock to update tagline
    # if any products is out of stock.
    for product in products:
        product.update_sale_price()
        product.check_stock()

    # Handle POST requests for search and sort requests
    if request.method == "POST":
        query = request.POST.get('search')
        sort = request.POST.get('sort')

        # Handles search query
        if query:
            products = products.filter(name__icontains=query)

        # Handles product sorting
        products = products.order_by('name')
        if sort == "non-alphabetical":
            products = products.order_by('-name')
        elif sort == "lowest-price":
            products = products.order_by('sale_price')
        elif sort == "highest-price":
            products = products.order_by('-sale_price')

        # Return the rendered view with the filtered products
        return render(request, "products.html", {'products': products,
                                                 "count": len(products),
                                                 "query": query,
                                                 "sort": sort})
    else:
        # Return all display-able products ordered alphabetically by default
        products = products.order_by('name')
        return render(request, "products.html", {'products': products,
                                                 "count": len(products)})


def product(request, pk):
    """
        Returns a rendered view for displaying a single product passed in
        the URL.
    """
    product = Product.objects.get(id=pk)
    return render(request, "product.html", {'product': product})


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def account(request):
    return render(request, "account.html")
