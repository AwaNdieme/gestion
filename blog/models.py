from django.db import models

# Table Service : Cette table représente les différents services médicaux disponibles dans l'hôpital.
# Elle contient des informations sur le nom et la description du service.
class Service(models.Model):
    nom_service = models.CharField(max_length=100,unique=True)  # Nom du service (par exemple, cardiologie, pédiatrie)
    description = models.TextField()  # Description détaillée du service

    def __str__(self):
        return self.nom_service


# Table Bureau : Cette table représente les bureaux où les médecins et infirmiers travaillent.
# Elle permet de lier chaque bureau à un service spécifique, facilitant la gestion des espaces.
class Bureau(models.Model):
    numero_bureau = models.CharField(max_length=20,unique=True)  # Numéro du bureau
    etage = models.IntegerField()  # Etage du bureau
    service = models.ForeignKey(Service, on_delete=models.CASCADE)  # Lien avec le service auquel le bureau appartient

    def __str__(self):
        return f"Bureau {self.numero_bureau} (Étage {self.etage})"


# Table Médecin : Cette table contient les informations des médecins, y compris leur spécialité, leur bureau et leur service.
# Elle permet d'identifier à quel service un médecin appartient et où il exerce.
class Medecin(models.Model):

    nom = models.CharField(max_length=100)  # Nom du médecin
    prenom = models.CharField(max_length=100)  # Prénom du médecin
    specialite = models.CharField(max_length=100)  # Spécialité du médecin (ex : cardiologue, pédiatre)
    email = models.EmailField(max_length=50,unique=True)  # Email du médecin pour la communication
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)  # Service auquel le médecin est affecté
    bureau = models.ForeignKey(Bureau, on_delete=models.SET_NULL, null=True,unique=True)  # Bureau du médecin

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.specialite})"


# Table Infirmier : Cette table contient les informations des infirmiers, tels que leur grade et leur service d'affectation.
# Elle permet d'identifier à quel service un infirmier appartient et de gérer ses coordonnées.
class Infirmier(models.Model):
    nom = models.CharField(max_length=100)  # Nom de l'infirmier
    prenom = models.CharField(max_length=100)  # Prénom de l'infirmier
    grade = models.CharField(max_length=50)  # Grade de l'infirmier (ex : infirmier, infirmier en chef)
    telephone = models.CharField(max_length=20,unique=True)  # Numéro de téléphone de l'infirmier
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)  # Service d'affectation de l'infirmier

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.grade})"


# Table Patient : Cette table contient les informations des patients, incluant leur médecin et leur service d'affectation.
# Elle permet de gérer les dossiers des patients et leur prise en charge par un médecin.
class Patient(models.Model):
    nom = models.CharField(max_length=100)  # Nom du patient
    prenom = models.CharField(max_length=100)  # Prénom du patient
    date_naissance = models.DateField()  # Date de naissance du patient
    sexe = models.CharField(max_length=6, choices=[('Homme', 'Homme'), ('Femme', 'Femme')])  # Sexe du patient
    adresse = models.CharField(max_length=255)  # Adresse du patient
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)  # Service du patient (ex : hospitalisation)
    medecin = models.ForeignKey(Medecin, on_delete=models.SET_NULL, null=True)  # Médecin référent du patient

    def __str__(self):
        return f"{self.prenom} {self.nom}"


# Table RendezVous : Cette table contient les informations sur les rendez-vous des patients avec les médecins.
# Elle permet de suivre les consultations prévues, terminées ou annulées.
class RendezVous(models.Model):
    date_rdv = models.DateField(unique=True)  # Date du rendez-vous
    statut = models.CharField(max_length=10, choices=[('Prévu', 'Prévu'), ('Terminé', 'Terminé'), ('Annulé', 'Annulé')], default='Prévu')  # Statut du rendez-vous
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)  # Patient ayant le rendez-vous
    medecin = models.ForeignKey(Medecin, on_delete=models.SET_NULL, null=True)  # Médecin auquel le rendez-vous est destiné

    def __str__(self):
        return f"Rendez-vous du {self.date_rdv} avec Dr. {self.medecin.nom} ({self.statut})"

