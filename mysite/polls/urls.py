from django.urls import path
from django.http import HttpResponse
from django.conf.urls import url

from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.home, name='home'),
    url(r'^$', views.listing, name='listing'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('moncompte/', views.moncompte, name='moncompte'),
    url(r'^search/$', views.search, name='search'),
    path('<int:pk>/', views.detail, name="detail"),
]