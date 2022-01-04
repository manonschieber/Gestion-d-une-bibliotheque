# Gestion d'une bibliothèque
Projet de Système de bases de données. 

## Contexte 
Un groupe d’étudiants bénévoles a décidé de construire une base de données pour gérer une médiathèque. D’une part, il s’agit du gérer le fonds documentaire. D’autre part, il s’agit de gérer les clients, leurs réservations, emprunts et cotisations.
Notre bibliothèque s’appelle "Biblivres".

Pour tout abonnement les clients doivent une cotisation renouvelable tous les ans. Cet abonnement permet à chaque personne d’emprunter jusqu’à trois livres plus deux autres documents (CD, revue etc) en simultané pendant une durée maximale de 30 jours. Le montant de la cotisation dépend de la situation du client (chômeur : gratuit, étudiant, élève ou militaire : demi-tarif, etc.). 

Si le livre n’est pas rendu au bout de 33 jours (3 jours de tolérance), l’emprunteur doit payer une pénalité de 1€ par jour de retard.
La récidive (3 fois dans les 12 derniers mois) entraîne l’exclusion de l’abonné : il est placé sur une liste de "mauvais emprunteurs" qui ne peuvent plus emprunter ou réserver des livres.
