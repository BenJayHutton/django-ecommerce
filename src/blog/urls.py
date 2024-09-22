from django.urls import path


from .views import (
    BlogListView,
    BlogDetailSlugView,
    BlogCreateView,
    BlogUpdateView,
    blog_delete_view,
)

app_name = 'blog'

urlpatterns = [
    path('', BlogListView.as_view(), name='home'),
    path('create/', BlogCreateView.as_view(), name='create'),
    path('update/<slug:slug>/', BlogUpdateView.as_view(), name='update'),
    path('delete/<slug:slug>/', blog_delete_view, name='delete'),
    path('view/P<slug:slug>/', BlogDetailSlugView.as_view(), name='detail'),
]
