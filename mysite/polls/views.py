from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.shortcuts import render, redirect
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
                "SELECT Livre.id, Livre.titre, Livre.nomAuteur, Livre.prenomAuteur, Emprunt.reserve_le, Emprunt.retour_max_le, Emprunt.en_retard\
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

def annuler_reservation(request, pk):
    with connection.cursor() as cursor :
        cursor.execute(            
            "SELECT max(id) AS max_id FROM polls_Emprunt WHERE livre_id=%s AND client_id=%s GROUP BY client_id", [pk, request.user.client.id]
        )
        max_id = cursor.fetchone()[0]
        cursor.execute(
            "DELETE FROM polls_Emprunt WHERE id=%s", [max_id]
        )
        cursor.execute(
            "UPDATE polls_Livre \
            SET disponible=1 WHERE id=%s", 
            [pk]
        )
        cursor.execute(
            "SELECT titre FROM polls_Livre WHERE id=%s", [pk]
        )
        titre = cursor.fetchone()[0]
    context = {
        'titre': titre
    }
    return render(request, 'polls/reservation_annulee.html', context)

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
    with connection.cursor() as cursor:
        cursor.execute("SELECT titre FROM polls_Livre WHERE id=%s", [pk])
        titre=cursor.fetchone()[0]
    if request.user.is_authenticated:
        if blacklisted_client(request.user.client)==0 and livre_disponible(pk) \
        and ((type_of_doc(pk)=='Livre' and nb_emprunt_inf_lim(request.user.client)[0]<3) \
        or (type_of_doc(pk)!='Livre' and nb_emprunt_inf_lim(request.user.client)[1]<2)): 
            
            new_id=max_emprunt_id(request)+1

            with connection.cursor() as cursor :
                cursor.execute("INSERT INTO polls_Emprunt (id, emprunte_le, rendu_le, en_retard, client_id, livre_id, reserve_le, retour_max_le) \
                VALUES \
                (%s, NULL, NULL, False, %s, %s, date('now'), date('now','+30 days'))", 
                [new_id,request.user.client.id, pk])
                cursor.execute("UPDATE polls_Livre\
                SET disponible=0 \
                WHERE id=%s", [pk])
            reservation_done = 'success'
        elif blacklisted_client(request.user.client)==0 : reservation_done = 'blacklist'
        elif not livre_disponible(pk): reservation_done ='livre_non_dispo'
        elif (type_of_doc(pk)=='Livre' and nb_emprunt_inf_lim(request.user.client)[0]<3): reservation_done='max_livre'
        elif (type_of_doc(pk)!='Livre' and nb_emprunt_inf_lim(request.user.client)[1]<2): reservation_done='max_docs'
    else:
        reservation_done = 'user_not_authenticated'
    context = {
        'reservation_done': reservation_done,
        'titre': titre
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
            "SELECT COUNT(DISTINCT Emp.id) AS emprunts_en_cours_livres \
            FROM polls_Emprunt AS Emp \
            JOIN polls_Livre AS Livre\
            ON Livre.id  = Emp.livre_id\
            WHERE Livre.support='Livre'AND Emp.rendu_le isnull AND client_id=%s", [self.id])
        emprunts_en_cours_livres = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(DISTINCT Emp.id) AS emprunts_en_cours_livres \
            FROM polls_Emprunt AS Emp \
            JOIN polls_Livre AS Livre\
            ON Livre.id  = Emp.livre_id\
            WHERE Livre.support<>'Livre'AND Emp.rendu_le isnull AND client_id=%s", [self.id]
        )
        emprunts_en_cours_autres = cursor.fetchone()[0]
    return (emprunts_en_cours_livres, emprunts_en_cours_autres)

def type_of_doc(self):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT support FROM polls_Livre \
            WHERE id=%s",
            [self]
        )
        type_of_doc=cursor.fetchone()[0]
    return(type_of_doc)

def max_emprunt_id(self):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT max(id) AS max_id FROM polls_Emprunt"
        )
        max=cursor.fetchone()[0]
    return(max)
