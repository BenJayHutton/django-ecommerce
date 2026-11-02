import logging
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render
from django.views.generic import TemplateView

from carts.models import Cart
from products.models import Product, Tag

now = timezone.now()
project_error_log = logging.getLogger("project_error_log")


class DefaultHomePage(TemplateView):
    display_name = "home"
    model = Product
    tags_obj = Tag
    products_featured_obj = model.objects.filter(featured=True)
    
    def get(self, request):
        try:
            cart_obj = Cart.objects.new_or_get(request)
            print(f"DefaultHomePage cart_obj {cart_obj}")
            context = {
                    "title": "Home Page",
                    "content": "Welcome to the home page",
                    "description": "Buy high-quality products ranging from books to apparel",
                    'products_featured_obj': self.products_featured_obj,
                }
            return render(request, "home_page.html", context)
        except Exception as e:
            project_error_log.log(
                logging.DEBUG if settings.DEBUG else logging.WARNING,
                f'[{now}] DefaultHomePage GET\n {type(e)} {e}', exc_info=True)
            raise Exception


def contact_page(request):
    try:
        context = {
            "description": "Contat Page",
            "title": "Contact Page",
        } 
        return render(request, "contact/view.html", context)
    except Exception as e:
        project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] def contact_page\n {type(e)} {e}', exc_info=True)        
        raise Exception
   


def about_page(request):
    try:
        context = {
            "description": "About page",
            "title": "About Page",
        }
        return render(request, "about.html", context)
    except Exception as e:
            project_error_log.log(
                logging.DEBUG if settings.DEBUG else logging.WARNING,
                f'[{now}] def about_page \n {type(e)} {e}', exc_info=True)
            raise Exception
