from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth import *
from django.views.generic import TemplateView
from django.db import connection

from .models import Client, Livre, Emprunt
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
    if request.user.is_authenticated:
        with connection.cursor() as cursor :
            cursor.execute(
                "SELECT Livre.id, Livre.titre\
                FROM polls_Emprunt AS Emprunt \
                JOIN polls_Client AS Client \
                ON Emprunt.client_id = Client.id \
                JOIN polls_Livre AS Livre \
                ON  Livre.id = Emprunt.livre_id \
                WHERE Client.id=%s AND Emprunt.emprunte_le isnull"
                , [request.user.client.id])
            columns = [col[0] for col in cursor.description]
            reservations = [dict(zip(columns, row)) for row in cursor.fetchall()]
    else:
        reservations = ''
    context = {
        'reservations': reservations
    }
    return render(request, 'polls/mesreservations.html', context)

def mesemprunts(request):
    with connection.cursor() as cursor :
        cursor.execute(
            "SELECT Livre.id, Livre.titre, Livre.nomAuteur, Livre.prenomAuteur, Emprunt.emprunte_le, Emprunt.retour_max_le, Emprunt.en_retard\
            FROM polls_Emprunt AS Emprunt \
            JOIN polls_Client AS Client \
            ON Emprunt.client_id = Client.id \
            JOIN polls_Livre AS Livre \
            ON  Livre.id = Emprunt.livre_id \
            WHERE Client.id=%s AND Emprunt.emprunte_le is not null AND rendu_le isnull"
            , [request.user.client.id])
        columns = [col[0] for col in cursor.description]
        emprunts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        print(emprunts)
    context = {
        'emprunts': emprunts
    }
    return render(request, 'polls/mesemprunts.html', context)

def catalogue(request):
    livresList = Livre.objects.order_by('titre')
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
        print(livre)
    context = {
        'livre_titre': livre[0]["titre"],
        'livre_nomAuteur': livre[0]["nomAuteur"],
        'livre_prenomAuteur': livre[0]["prenomAuteur"],
        'livre_disponible': livre[0]["disponible"],
        'livre_empruntable': livre[0]["empruntable"],
        'livre_pk':pk
    }
    return render(request, 'polls/detail.html', context)

def reserver(request, pk):
    if request.user.is_authenticated :
        if not( blacklisted_client(request.user.client) ) AND livre_disponible(pk): 
    with connection.cursor() as cursor :
        cursor.execute("INSERT INTO polls_Emprunt (id, emprunte_le, rendu_le, en_retard, client_id, livre_id, reserve_le, retour_max_le) \
        VALUES \
        (6, NULL, NULL, False, %s, %s, date('now'), date('now','+30 days'))", 
        [request.user.client.id, pk])
    infos = infos_perso(request.user.client)
    context = {
        'infos':infos
    }
    return render(request, 'polls/reserver.html', context)

def contact(request):
    return render(request, 'polls/contact.html')


class DashboardView(TemplateView):
    template_name = "polls/dashboard.html"



## Fontions SQL

def infos_perso(self):
    with connection.cursor() as cursor :
        cursor.execute("SELECT * FROM polls_Client where id=%s", [self.id])
        row = cursor.fetchone()
    return row

def blacklisted_client(self):
    with connection.cursor() as cursor:
        cursor.execute("SELECT bad_borrower FROM polls_Client where id=%s", [self.id])
        row = cursor.fetchone()
    return row[0]

def livre_disponible(self):
    with connection.cursor() as cursor:
        cursor.execute("SELECT (disponible AND empruntable) AS livre_empruntable FROM polls_livre where id=%s", [self])
        row = cursor.fetchone()
    return row[0]
    

def nb_emprunt_inf_lim(self):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(DISTINCT id) AS emprunts_en_cours_livres \
            FROM polls_Emprunt AS Emp \
            JOIN polls_Livre AS Livre\
            ON Livre.id  = Emp.livre_id\
            WHERE Livre.support='Livre'AND Emp.rendu_le isnull AND client_id=%s", [self.id])
        emprunts_en_cours_livres = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(DISTINCT id) AS emprunts_en_cours_livres \
            FROM polls_Emprunt AS Emp \
            JOIN polls_Livre AS Livre\
            ON Livre.id  = Emp.livre_id\
            WHERE Livre.support<>'Livre'AND Emp.rendu_le isnull AND client_id=%s", [self.id]
        )
        emprunts_en_cours_autres = cursor.fetchone()[0]
    return (emprunts_en_cours_livres, emprunts_en_cours_autres)

def type_of_doc(self):
    with connection.cursor() AS cursor:
