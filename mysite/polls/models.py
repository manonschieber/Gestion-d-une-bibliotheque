from django.db import models
import datetime
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User

class Client(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, default='plein tarif') # chômeur gratuit étudiant, élève ou militaire
    bad_borrower = models.BooleanField(default=False)
    blacklisted_until = models.DateField(null=True, blank=True)
    # def __str__(self):
    #     return self.user



class Livre(models.Model):
    nomAuteur = models.CharField(max_length=20)
    prenomAuteur = models.CharField(max_length=20)
    titre = models.CharField(max_length=30)
    disponible=models.BooleanField(default=True)
    empruntable=models.BooleanField(default=False)
    support=models.CharField(null=True, blank=True,max_length=15)
    categorie=models.CharField(null=True, blank=True,max_length=30)
    theme=models.CharField(null=True, blank=True,max_length=30)
    date_publication=models.DateField(null=True, blank=True)
    cree_le=models.DateField(default=timezone.now())
    supprime_le=models.DateField(null=True, blank=True)

    def __str__(self):
        return self.titre

class Emprunt(models.Model):
    livre=models.ForeignKey(Livre, on_delete=models.CASCADE)
    client=models.ForeignKey(Client, on_delete=models.CASCADE)

    emprunte_le=models.DateField(default=timezone.now())
    retour_max_le=models.DateField(default=timezone.now()+timedelta(days=30))
    rendu_le=models.DateField(null=True, blank=True)
    en_retard=models.BooleanField(default=False)

    def __str__(self):
        return self.livre.titre

class Paiement(models.Model):
    client=models.ForeignKey(Client, on_delete=models.CASCADE)

    cree_le=models.DateField(default=timezone.now())
    deadline=models.DateField(null=True,blank=True)
    paye_le=models.DateField(null=True, blank=True)
    raison=models.CharField(max_length=30)
    montant=models.DecimalField(max_digits=5, decimal_places=2, default=0)