from django.shortcuts import render
from django.views.generic import TemplateView

from products.models import Product, Tag


class DefaultHomePage(TemplateView):
    display_name = "home"
    model = Product
    tags_obj = Tag
    
    def get(self, request):
        context = {
                "title": "Home Page",
                "content": "Welcome to the home page",
                "description": "Buy high-quality products ranging from books to apparel",
            }
        return render(request, "home_page.html", context)


def contact_page(request):
    context = {
        "description": "Contat Page",
        "title": "Contact Page",
    }
    return render(request, "contact/view.html", context)


def about_page(request):
    context = {
        "description": "About page",
        "title": "About Page",
    }
    return render(request, "about.html", context)
