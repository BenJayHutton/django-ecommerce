from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView, View, ListView
from django.shortcuts import render
from django.utils import timezone

import datetime

from stripe import Product as StripeProduct

from orders.models import Order
from products.models import Product
from billing.models import BillingProfile
from carts.models import Cart

from .models import ObjectViewed


class ObjectViewList(ListView):
    model = ObjectViewed


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/carts.html'
    paginate_by = 2
    model = Order

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return render(self.request, "400.html", {})
        return super(CartView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(CartView, self).get_context_data(*args, **kwargs)
        qs = Cart.objects.all()
        return context


class OrderView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/orders.html'
    paginate_by = 2
    model = Order

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return render(self.request, "400.html", {})
        return super(OrderView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(OrderView, self).get_context_data(*args, **kwargs)
        qs = Order.objects.all()
        return context


class BillingProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/billing.html'
    paginate_by = 2
    model = BillingProfile

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return render(self.request, "400.html", {})
        return super(BillingProfileView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(
            BillingProfileView,
            self).get_context_data(
            *
            args,
            **kwargs)
        qs = Order.objects.all()
        return context


class ProductView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/product.html'
    paginate_by = 2
    model = Product

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return render(self.request, "400.html", {})
        return super(ProductView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(ProductView, self).get_context_data(*args, **kwargs)
        context['title'] = "Manage Product"
        qs = Order.objects.all()
        return context


class SalesAjaxView(View):
    def get(self, request, *args, **kwargs):
        data = {}
        if request.user.is_staff:
            qs = Order.objects.all().by_weeks_range(weeks_ago=5, number_of_weeks=5)
            if request.GET.get('type') == 'week':
                days = 7
                start_date = timezone.now().today() - datetime.timedelta(days=days - 1)
                datetime_list = []
                labels = []
                salesItems = []
                for x in range(0, days):
                    new_time = start_date + datetime.timedelta(days=x)
                    datetime_list.append(
                        new_time
                    )
                    labels.append(
                        new_time.strftime("%a")
                    )
                    new_qs = qs.filter(
                        updated__day=new_time.day,
                        updated__month=new_time.month)
                    day_total = new_qs.totals_data()['total__sum'] or 0
                    salesItems.append(
                        day_total
                    )
                data['labels'] = labels
                data['data'] = salesItems

            if request.GET.get('type') == '4weeks':
                data['labels'] = [
                    'Four Weeks Ago',
                    'Three Weeks Ago',
                    'Couple weeks ago',
                    'Last Week',
                    'This Week']
                current = 5
                data['data'] = []
                for i in range(0, 5):
                    new_qs = qs.by_weeks_range(
                        weeks_ago=current, number_of_weeks=1)
                    sales_total = new_qs.totals_data()['total__sum'] or 0
                    data['data'].append(sales_total)
                    current -= 1
        return JsonResponse(data)


class SalesView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return render(self.request, "400.html", {})
        return super(SalesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(SalesView, self).get_context_data(*args, **kwargs)
        qs = Order.objects.all().by_weeks_range(weeks_ago=10, number_of_weeks=10)
        start_date = timezone.now().date()
        today_data = qs.by_range(
            start_date=timezone.now().date()).get_sales_breakdown()
        context['today'] = today_data
        context['this_week'] = qs.by_weeks_range(
            weeks_ago=1, number_of_weeks=1).get_sales_breakdown()
        context['last_four_weeks'] = qs.by_weeks_range(
            weeks_ago=5, number_of_weeks=4).get_sales_breakdown()
        return context
