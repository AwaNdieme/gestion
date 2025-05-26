# Register your models here.
from django.contrib import admin
from .models import Service, Bureau, Medecin, Infirmier, Patient, RendezVous

admin.site.register(Service)
admin.site.register(Bureau)
admin.site.register(Medecin)
admin.site.register(Infirmier)
admin.site.register(Patient)
admin.site.register(RendezVous)
