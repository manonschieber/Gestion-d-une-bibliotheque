from django.urls import path
from django.http import HttpResponse
from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView

from . import views
from .views import DashboardView

app_name = 'polls'

urlpatterns = [
    path('', views.home, name='home'),
    path('mesinfospersos/', views.mesinfospersos, name='mesinfospersos'),
    path('mesreservations/', views.mesreservations, name='mesreservations'),
    path('mesemprunts/', views.mesemprunts, name='mesemprunts'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('<int:pk>/', views.detail, name="detail"),
    path('contact/', views.contact, name='contact'),
    path('reserver/<int:pk>/$', views.reserver, name='reserver'),
    path('annuler_reservation/<int:pk>/$', views.annuler_reservation, name='annuler_reservation'),
    url(r'^login/$', view=LoginView.as_view(template_name="polls/login.html", redirect_authenticated_user = True), name='login'),
    url(r'^logout/$', view=LogoutView.as_view(), name = "logout"),
    url(r'^dashboard/$', view = DashboardView.as_view(), name="dashboard"),
    url(r'^search/$', views.search, name='search'),
]