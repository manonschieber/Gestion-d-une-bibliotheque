from django.db import models
import datetime
from django.utils import timezone

class Client(models.Model):
    nom = models.CharField(max_length=15)
    prenom = models.CharField(max_length=15)
    situation = models.CharField(max_length=15)   #chômeur gratuit étudiant élève ou militaire 
    solde = models.DecimalField(max_digits=5, decimal_places=2)
    penalites = models.IntegerField(default=0)

    #liste des emprunts

    def __str__(self):
        return self.prenom + " " + self.nom

class Livre(models.Model):
    nomAuteur = models.CharField(max_length=15)
    prenomAuteur = models.CharField(max_length=15)
    titre = models.CharField(max_length=30)
    disponibilite=models.BooleanField(default=False)

    def __str__(self):
        return self.titre