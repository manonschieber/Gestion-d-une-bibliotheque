from django.urls import path
from django.http import HttpResponse

from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('moncompte/', views.moncompte, name='moncompte'),
    path('search/', views.search, name='search'),
    path('<int:pk>/', views.detail, name="detail"),
]