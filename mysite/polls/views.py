from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.shortcuts import render

from .models import Livre


def home(request):
    livresList = Livre.objects.order_by('-titre')[:1]
    template = loader.get_template('polls/index.html')
    context = {
        'livresList': livresList,
    }
    return render(request, 'polls/index.html', context)

def detailLivre(request, livre_id):
    try:
        livre = Livre.objects.get(pk=livre_id)
    except Livre.DoesNotExist:
        raise Http404("Le livre n'existe pas")
    return render(request, 'polls/detailLivre.html', {'livre': livre})

