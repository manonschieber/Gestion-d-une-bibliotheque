from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth import *
from django.views.generic import TemplateView
from django.db import connection

from .models import Client, Livre,Emprunt
from .forms import NameForm

def home(request):
    return render(request, 'polls/home.html')
    
def mesinfospersos(request):
    client = Client.objects.filter(user=request.user)
    print(client)
    context = {
    'client' : client
    }
    return render(request, 'polls/mesinfospersos.html')

def mesreservations(request):
    context = {
    }
    return render(request, 'polls/mesreservations.html', context)

def mesemprunts(request):
    emprunts = Emprunt.objects.filter(client=request.user.id)
    context = {
    'emprunts' : emprunts
    }
    return render(request, 'polls/mesemprunts.html', context)

def catalogue(request):
    livresList = Livre.objects.order_by('-titre')
    context = {
        'livresList': livresList,
    }
    return render(request, 'polls/catalogue.html', context)

def search(request):
    query = request.GET.get('query')
    if not query:
        livres = Livre.objects.all()
    else:
        livres = Livre.objects.filter(titre__icontains=query)
    title = "Résultats pour la recherche  : %s"%query
    context = {
        'livres': livres,
        'title': title
    }
    return render(request, 'polls/search.html', context)

def detail(request, pk):
    with connection.cursor() as cursor :
        cursor.execute("SELECT * FROM polls_Livre WHERE id=%s", [pk])
        columns = [col[0] for col in cursor.description]
        livre = [dict(zip(columns, row)) for row in cursor.fetchall()]
    context = {
        'livre_titre': livre[0]["titre"],
        'livre_nomAuteur': livre[0]["nomAuteur"],
        'livre_prenomAuteur': livre[0]["prenomAuteur"],
        'livre_disponibilite': livre[0]["disponible"],
        'livre_empruntabilite': livre[0]["empruntable"],
        'livre_pk':pk
    }
    return render(request, 'polls/detail.html', context)

def contact(request):
    return render(request, 'polls/contact.html')

class DashboardView(TemplateView):
    template_name = "polls/dashboard.html"



## Fontions SQL

def infos_perso(self):
    with connection.cursor() as cursor :
        cursor.execute("SELECT * FROM Client where username=%s", [self.user])
        row = cursor.fetchone()
    return row