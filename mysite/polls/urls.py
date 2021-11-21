from django.urls import path
from django.http import HttpResponse

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:livre_id>/', views.detailLivre, name='detail'),
]