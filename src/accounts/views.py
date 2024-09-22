from django.shortcuts import render
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView

class Accounts(DetailView):
    template_name = 'accounts/home.html'

    def get_context_data(self, *args, **kwargs):
        request = self.request
        context = super(Accounts, self).get_context_data(*args, **kwargs)
        context['title'] = "Account Home"
        context['description'] = "Account Home"
        return context

    def get_object(self):
        return self.request.user