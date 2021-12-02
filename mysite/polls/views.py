from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth import *
from django.views.generic import TemplateView

from .models import Livre
from .forms import NameForm

def home(request):
    return render(request, 'polls/home.html')
    
def mesinfospersos(request):
    return HttpResponseRedirect('/polls/login')

def catalogue(request):
    livresList = Livre.objects.order_by('-titre')
    context = {
        'livresList': livresList,
    }
    return render(request, 'polls/catalogue.html', context)

def contact(request):
    return render(request, 'polls/contact.html')

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
    livre = Livre.objects.get(pk=pk)
    context = {
        'livre_titre': livre.titre,
        'livre_nomAuteur': livre.nomAuteur,
        'livre_prenomAuteur': livre.prenomAuteur,
        'livre_disponibilite': livre.disponibilite
    }
    return render(request, 'polls/detailLivre.html', context)

def index(request):
    livres = Livre.objects.order_by('-titre')
    context = {
        'livres': livres
    }
    return render(request, 'polls/index.html', context)

def listing(request):
    livres = Livre.objects.order_by('-titre')
    context = {
        'livres': livres
    }
    return render(request, 'polls/listing.html', context)

def mesreservations(request):
    context = {
    }
    return render(request, 'polls/mesreservations.html', context)

def mesemprunts(request):
    context = {
    }
    return render(request, 'polls/mesemprunts.html', context)

def get_name(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = NameForm()
    return render(request, 'polls/name.html', {'form': form})


class DashboardView(TemplateView):
    template_name = "polls/dashboard.html"