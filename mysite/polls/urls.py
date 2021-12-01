from django.urls import path
from django.http import HttpResponse
from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView

from . import views
from .views import DashboardView

app_name = 'polls'

urlpatterns = [
    url(r'^dashboard/$', view = DashboardView.as_view(), name="dashboard"),
    url(r'^login/$', view=LoginView.as_view(template_name="polls/login.html", redirect_authenticated_user = True), name='login'),
    url(r'^logout/$', view=LogoutView.as_view(), name = "logout"),
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