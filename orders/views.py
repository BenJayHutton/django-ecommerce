import logging
from django.conf import settings
from django.utils import timezone
from django.http import Http404, JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView, DetailView, View

from .forms import OrderForm
from .models import Order, ProductPurchase

now = timezone.now()
project_error_log = logging.getLogger("project_error_log")
project_exception_log = logging.getLogger("project_exception_log")


class OrderCreateView(LoginRequiredMixin, CreateView):
    template_name = 'orders/create_order.html'
    form_class = OrderForm
    queryset = Order.objects.all()

    def get(self, *args, **kwargs):
        try:
            if not self.request.user.staff:
                return redirect("home")
            return super().get(*args, **kwargs)
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
            return HttpResponse(status=500)

    def form_valid(self, form):
        return super().form_valid(form)


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'orders/create_order.html'
    form_class = OrderForm
    queryset = Order.objects.all()

    def get(self, *args, **kwargs):
        try:
            if not self.request.user.staff:
                return redirect("home")
            return super().get(*args, **kwargs)
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
            return HttpResponse(status=500)

    def form_valid(self, form):
        return super().form_valid(form)


def order_delete_view(request, pk):
    try:
        obj = get_object_or_404(Order, pk=pk)
        if request.method == "POST":
            obj.delete()
            return redirect('analytics:orders')
        context = {
            "object": obj
        }
        return render(request, "orders/delete_order.html", context)
    except Exception as e:
        project_error_log.log(
        logging.DEBUG if settings.DEBUG else logging.WARNING,
        f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
        return HttpResponse(status=500)


class OrderListView(LoginRequiredMixin, ListView):

    def get_context_data(self, *args, **kwargs):
        try:
            request = self.request
            context = super(OrderListView, self).get_context_data(*args, **kwargs)
            context['title'] = "Orders"
            return context
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
            return HttpResponse(status=500)

    def get_queryset(self):
        return Order.objects.by_request(self.request) #.not_created() # show all orders 


class OrderDetailView(LoginRequiredMixin, DetailView):

    def get_context_data(self, *args, **kwargs):
        try:
            request = self.request
            context = super( OrderDetailView, self).get_context_data(*args, **kwargs)
            context['title'] = "Order Details"
            return context
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
            return HttpResponse(status=500)

    def get_object(self):
        qs = Order.objects.by_request(
            self.request).filter(
            order_id=self.kwargs.get('order_id'))
        if qs.count() == 1:
            return qs.first()
        raise Http404


class LibraryView(LoginRequiredMixin, ListView):
    template_name = 'orders/library.html'

    def get_context_data(self, *args, **kwargs):
        try:
            request = self.request
            context = super(LibraryView, self).get_context_data(*args, **kwargs)
            context['title'] = "Library View"
            return context
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
            return HttpResponse(status=500)

    def get_queryset(self):
        return ProductPurchase.objects.products_by_request(
            self.request)  # by_request(self.request).digital()


class VerifyOwnership(View):

    def get(self, request, *args, **kwargs):
        try:
            if request.is_ajax():
                data = request.GET
                product_id = data.get('product_id')
                if product_id is not None:
                    product_id = int(product_id)
                    ownership_ids = ProductPurchase.objects.products_by_id(request)
                    if product_id in ownership_ids:
                        return JsonResponse({'owner': True})
                    return JsonResponse({'owner': False})
            raise Http404
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
            return HttpResponse(status=500)


class OrderConfirmation(View):
    def post(self, request):
        try:
            order_id = request.POST.get('order_id', None)
            order_qs = Order.objects.filter(order_id=order_id)
            for order in order_qs:
                email = order.billing_profile.email
            if order_id is not None:
                Order.objects.email_order(order_id)
                messages.success(request, "An email has been sent to: " + email)
                url_redirect = (
                    reverse(
                        "orders:detail",
                        kwargs={
                            "order_id": order_id}))
                return redirect(url_redirect)
            else:
                raise Http404
        except Exception as e:
            project_error_log.log(
            logging.DEBUG if settings.DEBUG else logging.WARNING,
            f'[{now}] Accounts view GET\n {type(e)} {e}', exc_info=True)
            return HttpResponse(status=500)
