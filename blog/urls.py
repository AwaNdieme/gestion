from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accueil/', views.accueil, name='accueil'),
    ####bureau
    path('ajouter-bureau/', views.ajouter_bureau, name='ajouter_bureau'),
    path('modifier-bureau/<int:pk>/', views.modifier_bureau, name='modifier_bureau'),
    path('supprimer-bureau/<int:pk>/', views.supprimer_bureau, name='supprimer_bureau'),
    path('admin_Bureau/', views.admin_Bureau, name='admin_Bureau'),
    path('export/bureau/csv/', views.export_bureau_csv, name='export_bureau_csv'),
    path('export/bureau/excel/', views.export_bureau_excel, name='export_bureau_excel'),
    path('export/bureau/pdf/', views.export_bureau_pdf, name='export_bureau_pdf'),

    #############################
path('admin_Infirmier/', views.admin_Infirmier, name='admin_Infirmier'),
path('ajouter-infirmier/', views.ajouter_infirmier, name='ajouter_infirmier'),
path('modifier-infirmier/<int:pk>/', views.modifier_infirmier, name='modifier_infirmier'),
path('supprimer-infirmier/<int:pk>/', views.supprimer_infirmier, name='supprimer_infirmier'),

# Export
path('export_infirmiers_csv/', views.export_infirmiers_csv, name='export_infirmiers_csv'),
path('export_infirmiers_excel/', views.export_infirmiers_excel, name='export_infirmiers_excel'),
path('export_infirmiers_pdf/', views.export_infirmiers_pdf, name='export_infirmiers_pdf'),
#################################


path('admin_Service/', views.admin_Service, name='admin_Service'),
path('ajouter-service/', views.ajouter_service, name='ajouter_service'),
path('modifier-service/<int:pk>/', views.modifier_service, name='modifier_service'),
path('supprimer-service/<int:pk>/', views.supprimer_service, name='supprimer_service'),
path('admin_Service/', views.admin_Service, name='admin_Service'),

##Export pour les service
path('admin_Service/', views.admin_Service, name='admin_Service'),
path('export/services/csv/', views.export_services_csv, name='export_services_csv'),
path('export/services/excel/', views.export_services_excel, name='export_services_excel'),
path('export/services/pdf/', views.export_services_pdf, name='export_services_pdf'),

      
################################


path('admin_Medecin/', views.admin_medecin, name='admin_Medecin'),
path('ajouter-medecin/', views.ajouter_medecin, name='ajouter_medecin'),
path('modifier-medecin/<int:pk>/', views.modifier_medecin, name='modifier_medecin'),
path('supprimer-medecin/<int:pk>/', views.supprimer_medecin, name='supprimer_medecin'),

path('export_medecin_csv/', views.export_medecin_csv, name='export_medecin_csv'),
path('export_medecin_excel/', views.export_medecin_excel, name='export_medecin_excel'),
path('export_medecin_pdf/', views.export_medecin_pdf, name='export_medecin_pdf'),

##############################
# blog/urls.py
path('admin_Patient/', views.admin_Patient, name='admin_Patient'),
path('ajouter-patient/', views.ajouter_patient, name='ajouter_patient'),
path('modifier-patient/<int:pk>/', views.modifier_patient, name='modifier_patient'),
path('supprimer-patient/<int:pk>/', views.supprimer_patient, name='supprimer_patient'),

# Exports
path('export-patient-csv/', views.export_patients_csv, name='export_patient_csv'),
path('export-patient-excel/', views.export_patients_excel, name='export_patient_excel'),
path('export-patient-pdf/', views.export_patients_pdf, name='export_patient_pdf'),

#################   
 path('admin_profile/', views.admin_profile, name='admin-profile'),
    
    path('admin_RendezVous/', views.admin_RendezVous, name='admin_RendezVous'),
    path('ajouter-rendezVous/', views.ajouter_rendezVous, name='ajouter_rendezVous'),
    path('modifier-rendezVous/<int:pk>/', views.modifier_rendezVous, name='modifier_rendezVous'),
    path('supprimer-rendezVous/<int:pk>/', views.supprimer_rendezVous, name='supprimer_rendezVous'),
# Exports rendez-vous
path('export_rendezvous_csv/', views.export_rendezvous_csv, name='export_rendezvous_csv'),
path('export_rendezvous_excel/', views.export_rendezvous_excel, name='export_rendezvous_excel'),
path('export_rendezvous_pdf/', views.export_rendezvous_pdf, name='export_rendezvous_pdf'),

     #path('signup/', views.signup, name='signup'),


]