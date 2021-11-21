from django.urls import path
from django.http import HttpResponse

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:livre_id>/', views.detailLivre, name='detail'),
]