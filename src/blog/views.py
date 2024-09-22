from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView
)

from tags.models import Tag

from .forms import BlogForm
from .models import Blog


class BlogCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create_blog.html'
    form_class = BlogForm
    queryset = Blog.objects.all()

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/create_blog.html'
    form_class = BlogForm
    queryset = Blog.objects.all()

    def form_valid(self, form):
        return super().form_valid(form)


def blog_delete_view(request, slug):
    obj = get_object_or_404(Blog, slug=slug)
    if request.method == "POST":
        obj.delete()
        return redirect('blog:home')
    context = {
        "object": obj
    }
    return render(request, "blog/delete_blog.html", context)


class BlogListView(ListView):
    template_name = "blog/home.html"
    model = Blog
    blog_public = model.objects.filter(is_public=True, tags__public=True)

    def get_context_data(self, *args, **kwargs):
        context = super(BlogListView, self).get_context_data(*args, **kwargs)
        request = self.request
        user = request.user
        blog_tag = Tag.objects.filter(name="blog").first()

        if user.is_authenticated:
            blog_user = self.model.objects.filter(user=user)[:5]
        else:
            blog_user = None

        blog_obj = self.model.objects.filter(tags=blog_tag, is_public=True)[:5]

        context['blog_obj_public'] = self.blog_public
        context['user_blog_obj'] = blog_user
        context['title'] = "Blog"
        context['description'] = "Blogs"
        context['blog_obj'] = blog_obj
        return context

    def get_queryset(self, *args, **kwargs):
        return Blog.objects.all()


class BlogDetailSlugView(DetailView):
    template_name = "blog/detail.html"
    model = Blog

    def get_context_data(self, *args, **kwargs):
        context = super(
            BlogDetailSlugView,
            self).get_context_data(
            *
            args,
            **kwargs)
        slug = self.kwargs.get('slug')
        try:
            blog_obj = Blog.objects.get(slug=slug)
        except BaseException:
            blog_obj = None

        context['blog_list'] = Blog.objects.all()
        context['title'] = blog_obj.title
        context['description'] = blog_obj.blog_post
        return context
