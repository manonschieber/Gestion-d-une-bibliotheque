from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import *
from django.views.generic import TemplateView
from django.db import connection
from datetime import datetime, timezone, timedelta
from django.core.paginator import Paginator
import pytz
from django.db.models import Q

from .models import Client, Livre, Emprunt, Paiement
from .forms import NameForm

def home(request):   #affichage de la vue de la page d'accueil
    date_du_jour = datetime.now(timezone.utc)
    if request.user.is_authenticated:
        if (request.user.last_login-date_du_jour>timedelta(1)):    #si l'utilisateur s'est connecté il y a plus d'un jour, on regarde s'il ne doit pas payer la cotisation + on met à jour les paiements  
            MAJ_paiement(request.user.client)
            MAJ_is_bad_borrower(request.user.client)
            actualisation_cotisation(request.user.client)
    return render(request, 'polls/home.html')
    
def mesinfospersos(request):    #affichage de la vue des informations personnelles de l'utilisateur
    client=[]
    montant = 0
    deadline=''
    date_du_jour = datetime.now(timezone.utc)
    if request.user.is_authenticated:
        if (request.user.last_login-date_du_jour>timedelta(1)):    #si l'utilisateur s'est connecté il y a plus d'un jour, on regarde s'il ne doit pas payer la cotisation + on met à jour les paiements 
            MAJ_paiement(request.user.client)
            MAJ_is_bad_borrower(request.user.client)
            actualisation_cotisation(request.user.client)
        client = Client.objects.filter(user=request.user)
        montant = montant_du(request.user.client)
        deadline = deadline_paiement(request.user.client)
    context = {
    'client' : client,
    'montant' : montant,
    'deadline' : deadline
    }
    return render(request, 'polls/mesinfospersos.html',context)

def mesreservations(request):    #affichage de la vue de la page des réservations de l'utilisateur 
    if request.user.is_authenticated:
        date_du_jour = datetime.now(timezone.utc)
        if (request.user.last_login-date_du_jour>timedelta(1)):    #si l'utilisateur s'est connecté il y a plus d'un jour, on regarde s'il ne doit pas payer la cotisation + on met à jour les paiements du site 
            actualisation_cotisation(request.user.client)
            MAJ_paiement(request.user.client)
            MAJ_is_bad_borrower(request.user.client)
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

def mesemprunts(request):   #affichage de la vue de la page des emprunts 
    emprunts=[]
    if request.user.is_authenticated: 
        date_du_jour = datetime.now(timezone.utc)
        if (request.user.last_login-date_du_jour>timedelta(1)):    #si l'utilisateur s'est connecté il y a plus d'un jour, on regarde s'il ne doit pas payer la cotisation 
            actualisation_cotisation(request.user.client)
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
    context = {
        'emprunts': emprunts
    }
    return render(request, 'polls/mesemprunts.html', context)

def catalogue(request):     #affichage de la vue de la page du catalogue 
    List = Livre.objects.order_by('titre')
    paginator = Paginator(List, 25)
    page = request.GET.get('page')
    livresList = paginator.get_page(page)
    context = {
        'livresList': livresList,
    }
    return render(request, 'polls/catalogue.html', context)

def search(request):    #permet la recherche de livres, CD ou autre à l'aide du titre, du prénom ou du nom de l'auteur
    query = request.GET.get('query')
    if not query:
        livres = Livre.objects.all()
    else:
        livres = Livre.objects.filter(Q(titre__icontains=query)|Q(prenomAuteur__icontains=query)|Q(nomAuteur__icontains=query))
    title = "Résultats pour la recherche  : %s"%query
    context = {
        'livres': livres,
        'title': title
    }
    return render(request, 'polls/search.html', context)

def detail(request, pk):    #affichage de la vue de la page de détail d'un livre 
    with connection.cursor() as cursor :
        cursor.execute("SELECT * FROM polls_Livre WHERE id=%s", [pk])
        columns = [col[0] for col in cursor.description]
        livre = [dict(zip(columns, row)) for row in cursor.fetchall()]
        #print(livre)
    context = {
        'livre_titre': livre[0]["titre"],
        'livre_nomAuteur': livre[0]["nomAuteur"],
        'livre_prenomAuteur': livre[0]["prenomAuteur"],
        'livre_disponible': livre[0]["disponible"],
        'livre_empruntable': livre[0]["empruntable"],
        'livre_pk':pk
    }
    return render(request, 'polls/detail.html', context)

def reserver(request, pk):   #permet de réserver un livre en prenant en entrée son id
    with connection.cursor() as cursor:
        cursor.execute("SELECT titre FROM polls_Livre WHERE id=%s", [pk])
        titre=cursor.fetchone()[0]
    if request.user.is_authenticated:
        if blacklisted_client(request.user.client)==0 and livre_disponible(pk) \
        and ((type_of_doc(pk)=='Livre' and nb_emprunt_inf_lim(request.user.client)[0]<3) \
        or (type_of_doc(pk)!='Livre' and nb_emprunt_inf_lim(request.user.client)[1]<2)):  #on vérifie que le client n'est pas blacklisté, que le livre est disponible, que le client n'a pas atteint le nombre maximum d'emprunts...
            
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
        elif blacklisted_client(request.user.client)==1 : reservation_done = 'blacklist'
        elif not livre_disponible(pk): reservation_done ='livre_non_dispo'
        elif (type_of_doc(pk)=='Livre' and nb_emprunt_inf_lim(request.user.client)[0]>=3): reservation_done='max_livre'
        elif (type_of_doc(pk)!='Livre' and nb_emprunt_inf_lim(request.user.client)[1]>=2): reservation_done='max_docs'
    else:
        reservation_done = 'user_not_authenticated'
    context = {
        'reservation_done': reservation_done,
        'titre': titre
    }
    return render(request, 'polls/reserver.html', context)

def contact(request):    #affichage de la vue de la page de contacts
    return render(request, 'polls/contact.html')


class DashboardView(TemplateView):   #affichage de la vue de la page de connexion 
    template_name = "polls/dashboard.html"



## Fontions SQL

def montant_du(self):  #Calcul du montant dû par le client
    with connection.cursor() as cursor :
        cursor.execute("SELECT * FROM polls_Paiement where client_id=%s", [self.id])   #on récupère tous les paeiments du client connecté
        row = cursor.fetchall()
    montant=0
    if len(row) != 0: #on regarde les paiements qui ont été effectués ou sont en cours
        for i in range(len(row)): 
            if row[i][2]==None: #quand le paiement n'a pas encore été effectué
                montant = montant + row[i][4]   #on ajoute le montant au montant total
    return round(montant,2)

def deadline_paiement(self):  #Calcul de la deadline pour le paiement (minimum des deadlines de tous les paiements)
    with connection.cursor() as cursor :
        cursor.execute("SELECT * FROM polls_Paiement where client_id=%s", [self.id])    #on sélectionne tous les paiements du client connecté
        row = cursor.fetchall()
    deadlines=[]
    if len(row) != 0: #on regarde les paiements qui ont été effectués ou sont en cours
        for i in range(len(row)): 
            if row[i][2]==None: #quand le paiement n'a pas encore été effectué
                if (row[i][1]!=None):
                    deadlines.append(row[i][1])   #on ajoute la deadline à la liste de toutes les deadlines
    if deadlines : 
        return min(deadlines)    #on retourne la deadline minimum
    else:
        return

def actualisation_cotisation(self):  #Actualisation du paiement de la cotisation 
    statut=''

    #on va d'abord récupérer la date du jour en format AAAAMMJJ
    utc=pytz.UTC
    date_du_jour = str(datetime.now(timezone.utc))
    annee_actuelle=int(date_du_jour[0]+date_du_jour[1]+date_du_jour[2]+date_du_jour[3])
    mois_actuel=int(date_du_jour[5]+date_du_jour[6])
    mois=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    jour_actuel=int(date_du_jour[8]+date_du_jour[9])
    date_du_jour_str=str(jour_actuel)+'-'+mois[mois_actuel-1]+'-'+str(annee_actuelle)
    date_du_jour_AAAAMMJJ = datetime.strptime(date_du_jour_str, '%d-%b-%Y').strftime('%Y-%m-%d')

    if jour_actuel==1 and mois_actuel==1:   #on met à jour les cotisations le 1 janvier
        with connection.cursor() as cursor :
            cursor.execute("SELECT * FROM polls_Client where id=%s", [self.id])   #on sélectionne le client connecté 
            row = cursor.fetchall()
            if row:
                statut=row[0][1]   # on récupère le statut du client pour savoir combien il doit payer
        if statut != '':  #on ajoute un paiement pour la cotisation pour le client
            if statut == "plein tarif": 
                p = Paiement(cree_le=date_du_jour_AAAAMMJJ, deadline=utc.localize(datetime(annee_actuelle, 2, 1, 0, 0)),raison="Cotisation annuelle",montant=18)
                p.save()
            if statut == "jeune":
                p = Paiement(client=self,cree_le=date_du_jour_AAAAMMJJ, deadline=utc.localize(datetime(annee_actuelle, 2, 1, 0, 0)),raison="Cotisation annuelle",montant=10)
                p.save()
    #tous les ans, on ajoute un paiement du montant de la cotisation à tous le monde, pour la fin du mois de janvier
    return

def MAJ_paiement(self):  #mise à jour de tous les paiements de la bilbi
    date_du_jour = datetime.now(timezone.utc)
    with connection.cursor() as cursor :
        cursor.execute("SELECT * FROM polls_Emprunt")  #on récupère tous les emprunts 
        emprunts = cursor.fetchall()
    deadline=''

    #mise à jour du montant dû qui augmente de 1€ tous les jours
    for i in range(len(emprunts)):
        if emprunts and emprunts[i]:
            annee=str(emprunts[i][7])
            annee=int(annee[0]+annee[1]+annee[2]+annee[3])
            mois=str(emprunts[i][7])
            mois=int(mois[5]+mois[6])
            jour=str(emprunts[i][7])
            jour=int(jour[8]+jour[9])
            utc=pytz.UTC
            deadline =  utc.localize(datetime(annee, mois, jour, 0, 0))
            if deadline+timedelta(3)>=date_du_jour:
                prix = deadline+timedelta(3)-date_du_jour
                prix=str(prix)
                prix=prix[0]+prix[1]+'.00'
                prix=float(prix)
                Paiement.objects.filter(pk=i).update(montant=prix)  #le montant de la pénalité est égal au nombre de jour depuis la date de fin de l'emprunt moins les 3 jours de tolérance 
    
    #ajout d'un paiement en cas de rendu en retard dès le 4e jour
    with connection.cursor() as cursor :
        cursor.execute("SELECT * FROM polls_Emprunt")  #on récupère tous les emprunts 
        emprunts = cursor.fetchall()

        for i in range(len(emprunts)):
            if emprunts and emprunts[i]:
                annee=str(emprunts[i][7])
                annee=int(annee[0]+annee[1]+annee[2]+annee[3])
                mois=str(emprunts[i][7])
                mois=int(mois[5]+mois[6])
                jour=str(emprunts[i][7])
                jour=int(jour[8]+jour[9])
                utc=pytz.UTC
                deadline =  utc.localize(datetime(annee, mois, jour, 0, 0))

                annee_actuelle=int(date_du_jour[0]+date_du_jour[1]+date_du_jour[2]+date_du_jour[3])
                mois_actuel=int(date_du_jour[5]+date_du_jour[6])
                mois=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                jour_actuel=int(date_du_jour[8]+date_du_jour[9])
                date_du_jour_str=str(jour_actuel)+'-'+mois[mois_actuel-1]+'-'+str(annee_actuelle)
                date_du_jour_AAAAMMJJ = datetime.strptime(date_du_jour_str, '%d-%b-%Y').strftime('%Y-%m-%d')
                if (utc.localize(datetime(2021, 12, 1, 0, 0))+timedelta(4))==date_du_jour:   #premier jour de paiement 
                    p = Paiement(client=self,cree_le=date_du_jour_AAAAMMJJ, deadline=None,raison="Retard Emprunt",montant=1)   #on créé une instance paiement pour cause d'emprunt rendu en retard 
                    p.save()
    return 

def MAJ_is_bad_borrower(self):  #mise à jour clients bad_borrower
    date_du_jour = datetime.now(timezone.utc)
    annee_en_cours=str(date_du_jour)
    annee_en_cours=int(annee_en_cours[0]+annee_en_cours[1]+annee_en_cours[2]+annee_en_cours[3])
    utc=pytz.UTC
    with connection.cursor() as cursor :
        cursor.execute("SELECT * FROM polls_Emprunt where client_id=%s", [self.id])   #on récupère les emprunts du client 
        emprunts = cursor.fetchall()
    nb_en_retard=0
    for i in range(len(emprunts)):    #on parcourt les emprunts 
        annee_emprunt = str(emprunts[i][1])
        annee_emprunt=int(annee_emprunt[0]+annee_emprunt[1]+annee_emprunt[2]+annee_emprunt[3])
        if emprunts[i][3]==True and annee_emprunt==annee_en_cours:  #si l'emprunt a été rendu en retard, on ajoute 1 au compteur
            nb_en_retard=nb_en_retard+1
    if nb_en_retard>=3 and self.bad_borrower==False:   #si il y a plus de 3 rendus en retard et que le client n'est pas bad_borrower, on le pase à True 
        Client.objects.filter(pk=self.id).update(bad_borrower=True)
        deadline=date_du_jour+timedelta(2*365)
        Client.objects.filter(pk=self.id).update(blacklisted_until=deadline)
    elif nb_en_retard<3 and self.bad_borrower==True:   #si il y a moins de 3 emprunts rendus en retard au cours de l'année précédente, et que le client est bad_borrower, on le passe à False
        Client.objects.filter(pk=self.id).update(bad_borrower=False)
        Client.objects.filter(pk=self.id).update(blacklisted_until=None)
    return 


def blacklisted_client(self):    #permet de renvoyer l'information de est-ce que le client est bad_borrower ou non. Si oui, il ne peut pas emprunter
    with connection.cursor() as cursor:
        cursor.execute("SELECT bad_borrower FROM polls_Client where id=%s", [self.id])
        row = cursor.fetchone()
    return row[0]

def livre_disponible(self):   #permet de renvoyer la disponibilité d'un livre 
    with connection.cursor() as cursor:
        cursor.execute("SELECT (disponible AND empruntable) AS livre_empruntable FROM polls_livre where id=%s", [self])
        row = cursor.fetchone()
    return row[0]
    

def nb_emprunt_inf_lim(self):  #renvoie le nombre d'emprunts en cours pour les livres et pour les autres supports 
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(DISTINCT Emp.id) \
            FROM polls_Emprunt AS Emp \
            JOIN polls_Livre AS Livre\
            ON Livre.id  = Emp.livre_id\
            WHERE Livre.support='Livre' AND Emp.rendu_le isnull AND client_id=%s", [self.id])
        emprunts_en_cours_livres = cursor.fetchone()[0]
        print(emprunts_en_cours_livres)

        cursor.execute(
            "SELECT COUNT(DISTINCT Emp.id) \
            FROM polls_Emprunt AS Emp \
            JOIN polls_Livre AS Livre\
            ON Livre.id  = Emp.livre_id\
            WHERE Livre.support<>'Livre' AND Emp.rendu_le isnull AND client_id=%s", [self.id]
        )
        emprunts_en_cours_autres = cursor.fetchone()[0]
        print(emprunts_en_cours_autres)
    return (emprunts_en_cours_livres, emprunts_en_cours_autres)

def type_of_doc(self):   #renvoie le type du document 
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT support FROM polls_Livre \
            WHERE id=%s",
            [self]
        )
        type_of_doc=cursor.fetchone()[0]
        print(type_of_doc)
    return(type_of_doc)

def max_emprunt_id(self):   #renvoie l'indice maximal des indices des emprunts 
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT max(id) AS max_id FROM polls_Emprunt"
        )
        max=cursor.fetchone()[0]
    return(max)
