from django import forms  # Import de l'API de formulaires de Django
from .models import Service, Bureau, Medecin, Infirmier, Patient, RendezVous  # Import des modèles utilisés

# ========================
#  Formulaire de Connexion
# ========================
class LoginForm(forms.Form):
    # Champ pour le nom d'utilisateur (simple champ texte)
    username = forms.CharField(max_length=50, label="Nom d'utilisateur")
    
    # Champ mot de passe, masqué (widget spécial)
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput,  # Affiche des points au lieu du texte
        label='Mot de Passe'
    )

# ========================
#  Formulaire pour les Patients
# ========================
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient  # Le modèle utilisé est Patient
        fields = '__all__'  # Inclure tous les champs du modèle
        widgets = {
            # Spécifie que le champ date_naissance doit utiliser un input de type "date" (calendrier)
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

# ========================
#  Formulaire pour les Médecins
# ========================
class MedecinForm(forms.ModelForm):
    class Meta:
        model = Medecin  # Utilise le modèle Medecin
        fields = '__all__'  # Tous les champs du modèle

# ========================
#  Formulaire pour les Rendez-vous
# ========================
class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RendezVous  # Modèle utilisé
        fields = '__all__'
        widgets = {
            # Date de RDV avec un input HTML de type "date"
            'date_rdv': forms.DateInput(attrs={'type': 'date'}),
        }

# ========================
#  Formulaire pour les Infirmiers
# ========================
class InfirmierForm(forms.ModelForm):
  #  grade = forms.ChoiceField(choices=GRADE_CHOICES, label="Grade")

    class Meta:
        model = Infirmier
        fields = '__all__'

# ========================
#  Formulaire pour les Services
# ========================


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

# ========================
#  Formulaire pour les Bureaux
# ========================
class BureauForm(forms.ModelForm):
    class Meta:
        model = Bureau
        fields = '__all__'
        widgets = {
            # Ajout d’une classe CSS pour styliser la sélection du service dans Bootstrap
            'service': forms.Select(attrs={'class': 'form-control'}),
        }





