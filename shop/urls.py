from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('data.js', views.data_js, name='data_js'),
    path('', views.page('pages/index.html'), name='index'),
    path('category/', views.page('pages/category.html'), name='category'),
    path('product/', views.page('pages/product.html'), name='product'),
    path('cart/', views.page('pages/cart.html'), name='cart'),
    path('checkout/', RedirectView.as_view(url='/cart/'), name='checkout'),
    path('order/', views.page('pages/order.html'), name='order'),
    path('login/', views.page('pages/login.html'), name='login'),
    path('register/', views.page('pages/register.html'), name='register'),
    path('account/', views.page('pages/account.html'), name='account'),
    path('blog/', RedirectView.as_view(url='/'), name='blog'),
    path('article/', RedirectView.as_view(url='/'), name='article'),
    path('about/', views.about, name='about'),
    path('guide/', views.guide, name='guide'),
    path('contact/', views.contact, name='contact'),
    path('api/contact/', views.contact_api),
]
