from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.shortcuts import render

from .models import Livre
from .forms import NameForm

def home(request):
    return render(request, 'polls/home.html')

def catalogue(request):
    livresList = Livre.objects.order_by('-titre')
    context = {
        'livresList': livresList,
    }
    return render(request, 'polls/catalogue.html', context)

def moncompte(request):
    return render(request, 'polls/moncompte.html')

def search(request):
    query = request.GET.get('query')
    if not query:
        livres = Livre.objects.all()
    else:
        livres = Livre.objects.filter(titre__icontains=query)
    title = "Résultats pour la requête %s"%query
    context = {
        'livres': livres,
        'title': title
    }
    return render(request, 'polls/search.html', context)

def detail(request, pk):
    livre = Livre.objects.get(pk=pk)
    try:
        livre = Livre.objects.get(pk=pk)
    except Livre.DoesNotExist:
        raise Http404("Le livre n'existe pas")
    return render(request, 'polls/detailLivre.html', {'livre': livre})

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

def infos(request):
    context = {
    }
    return render(request, 'polls/infos.html', context)


