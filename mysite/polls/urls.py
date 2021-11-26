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
    path('mesreservations/', views.mesreservations, name='mesreservations'),
    path('mesemprunts/', views.mesemprunts, name='mesemprunts'),
    path('infos/', views.infos, name='infos'),
    url(r'^search/$', views.search, name='search'),
    path('<int:pk>/', views.detail, name="detail"),
    path('your-name/', views.get_name, name="get_name"),
]