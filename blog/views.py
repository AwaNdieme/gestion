from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from . import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from .forms import BureauForm, ServiceForm, InfirmierForm, MedecinForm, PatientForm, RendezVousForm
from .models import Patient,Infirmier,RendezVous,Medecin,Bureau,Service
import csv
import openpyxl
from django.contrib import messages


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


from .forms import ServiceForm


def admin_profile(request):
    return render(request, 'blog/admin_profile.html')


def login_page(request):
    form = forms.LoginForm()
    message = ''
    
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('accueil')  # Redirection vers la page d'accueil
            else:
                message = 'Identifiants invalides,il vous reste 5 tentatives !!! '
                return render(request, 'blog/login.html', context={'form': form, 'message': message})
    
    return render(request, 'blog/login.html', context={'form': form, 'message': message})

@login_required
def accueil(request):
    """Vue pour la page d'accueil après connexion"""
    return render(request, 'blog/accueil.html')

def logout_view(request):
    """Vue pour la déconnexion"""
    logout(request)
    return redirect('login')

from django.shortcuts import render, get_object_or_404, redirect
from .models import Service
from .forms import ServiceForm

# Vue principale de gestion des services

def admin_Service(request):
    services = Service.objects.all()
    recherche = request.GET.get('recherche', '')
    selected_service = request.GET.get('service', '')

    # Filtrer par nom
    if recherche:
        services = services.filter(nom_service__icontains=recherche)

    # Filtrer par ID
    if selected_service:
        services = services.filter(id=selected_service)

    # Formulaire vide pour le modal d’ajout
    form = ServiceForm()

    context = {
        'services': services,
        'selected_service': selected_service,
        'recherche': recherche,
        'form': form,  # Passer le formulaire au template
    }
    return render(request, 'blog/admin_Service.html', context)

# Ajouter un service (avec ServiceForm)

def ajouter_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()  # Enregistrement automatique dans la BD
            return redirect('admin_Service')
    return redirect('admin_Service')

#Modifier un service existant (form pré-rempli)
def modifier_service(request, pk):
    service = get_object_or_404(Service, pk=pk)  # Récupère le service à modifier

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)  # Lié au service existant
        if form.is_valid():
            form.save()  # Mise à jour
            return redirect('admin_Service')
    return redirect('admin_Service')

#  Supprimer un service
# ===============================
def supprimer_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
    return redirect('admin_Service')



# Exporter les services au format CSV
def export_services_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="services.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nom du Service', 'Description'])

    for s in Service.objects.all():
        writer.writerow([s.id, s.nom_service, s.description])

    return response

# ===============================
from django.http import HttpResponse
from openpyxl.styles import Font, Alignment

def export_services_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Services"

    # En-têtes stylés
    ws.append(['ID', 'Nom du Service', 'Description'])
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Données
    for s in Service.objects.all():
        ws.append([s.id, s.nom_service, s.description])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="services.xlsx"'
    wb.save(response)
    return response

# ===============================
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from django.http import HttpResponse
from .models import Service

def export_services_pdf(request):
    # Configuration du document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="services_hopital.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter,
                          rightMargin=40, leftMargin=40,
                          topMargin=60, bottomMargin=60)
    elements = []
    styles = getSampleStyleSheet()
    
    # Style personnalisé
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Heading1'],
        textColor=colors.HexColor('#005b96'),  # Bleu hospitalier
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=20
    )
    
    # En-tête avec logo (optionnel)
    try:
        logo = Image("static/blog/img/me.jpg", width=1.5*inch, height=1*inch)
        logo.hAlign = 'LEFT'  # Alignement à gauche
        elements.append(logo)
    except:
        pass  # Continue sans logo si non trouvé
    
    elements.extend([
        Paragraph("HÔPITAL GÉNÉRAL DE L'UIT", title_style),
        Paragraph("LISTE DES SERVICES MÉDICAUX", styles['Heading2']),
        Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']),
        Spacer(1, 24)
    ])

    # Données des services (uniquement les champs du modèle)
    data = [
        ['ID', 'Nom du Service', 'Description']  # En-têtes correspondant exactement aux champs
    ]
    
    services = Service.objects.all().order_by('nom_service')
    
    for service in services:
        data.append([
            service.id,
            service.nom_service,  # Champ direct sans modification
            service.description   # Champ direct sans modification
        ])

    # Style du tableau
    table = Table(data, colWidths=[40, 200, 300], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#17a2b8')),  # Bleu turquoise
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Centrer uniquement la colonne ID
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),  # Fond gris très clair
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # Pied de page
    footer_style = ParagraphStyle(
        'footer_style',
        parent=styles['Italic'],
        textColor=colors.HexColor('#6c757d'),
        fontSize=8,
        alignment=1
    )
    
    elements.append(Paragraph(
        f"Total services: {services.count()} • © {datetime.now().year} Hôpital Général de l'UIT",
        footer_style
    ))

    # Génération du PDF
    doc.build(elements)
    return response
# ===============================
# Fin de la gestion des services

#############  BUREAU #############
def admin_Bureau(request):
    bureaux = Bureau.objects.all()
    services = Service.objects.all()

    # Récupération des filtres depuis l'URL
    recherche = request.GET.get('recherche', '')
    selected_bureau = request.GET.get('bureau', '')

    # Filtrage par numéro de bureau
    if recherche:
        bureaux = bureaux.filter(numero_bureau__icontains=recherche)

    # Filtrage par ID de bureau
    if selected_bureau:
        bureaux = bureaux.filter(id=selected_bureau)

    context = {
        'bureaux': bureaux,
        'services': services,
        'selected_bureau': selected_bureau,
        'recherche': recherche,
        'form': BureauForm(),  # Formulaire vide pour ajout
    }
    return render(request, 'blog/admin_Bureau.html', context)

def ajouter_bureau(request):
    if request.method == 'POST':
        form = BureauForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_Bureau')
    return redirect('admin_Bureau')



def modifier_bureau(request, pk):
    bureau = get_object_or_404(Bureau, pk=pk)
    if request.method == 'POST':
        form = BureauForm(request.POST, instance=bureau)
        if form.is_valid():
            form.save()
            return redirect('admin_Bureau')
    return redirect('admin_Bureau')


def supprimer_bureau(request, pk):
    bureau = get_object_or_404(Bureau, pk=pk)
    if request.method == 'POST':
        bureau.delete()
    return redirect('admin_Bureau')


#############################

def export_bureau_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bureaux.csv"'
    writer = csv.writer(response)
    writer.writerow(['Numero Bureau', 'Etage', 'Service'])

    for b in Bureau.objects.all():
        writer.writerow([b.numero_bureau, b.etage, b.service.nom_service])
    return response


def export_bureau_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bureaux"
    ws.append(['Numero Bureau', 'Etage', 'Service'])

    for b in Bureau.objects.all():
        ws.append([b.numero_bureau, b.etage, b.service.nom_service])

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="bureaux.xlsx"'
    wb.save(response)
    return response


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_bureau_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bureaux.pdf"'
    p = canvas.Canvas(response, pagesize=A4)

    y = 800
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Liste des Bureaux")
    p.setFont("Helvetica", 12)
    y -= 40

    for b in Bureau.objects.all():
        p.drawString(100, y, f"Bureau: {b.numero_bureau} - Étage: {b.etage} - Service: {b.service.nom_service}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response
###############################  FIN BUREAU ###########



#############   INFIRMIER ##############
#Affichage des infirmiers
from django.db.models import Q

def admin_Infirmier(request):
    infirmiers = Infirmier.objects.select_related('service').all()
    recherche = request.GET.get('recherche', '')
    selected_grade = request.GET.get('grade', '')
    selected_service = request.GET.get('service', '')

    # Filtres combinés
    if recherche:
        infirmiers = infirmiers.filter(
            Q(nom__icontains=recherche) | 
            Q(prenom__icontains=recherche)
    )
    
    if selected_grade:
        infirmiers = infirmiers.filter(grade__iexact=selected_grade)
        
    if selected_service:
        infirmiers = infirmiers.filter(service__id=selected_service)

    # Récupération des grades distincts existants
    grades = Infirmier.objects.values_list('grade', flat=True).distinct()

    context = {
        'infirmiers': infirmiers,
        'grades': grades,
        'recherche': recherche,
        'selected_grade': selected_grade,
        'selected_service': selected_service,
        'form': InfirmierForm(),
        'services': Service.objects.all()
    }
    return render(request, 'blog/admin_Infirmier.html', context)

#  Ajout d’un infirmier via InfirmierForm
def ajouter_infirmier(request):
    if request.method == "POST":
        form = InfirmierForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('admin_Infirmier')

#  Modifier infirmier
def modifier_infirmier(request, pk):
    infirmier = get_object_or_404(Infirmier, pk=pk)
    if request.method == "POST":
        form = InfirmierForm(request.POST, instance=infirmier)
        if form.is_valid():
            form.save()
            return redirect('admin_Infirmier')
    return redirect('admin_Infirmier')

# 🗑️ Supprimer infirmier
def supprimer_infirmier(request, pk):
    infirmier = get_object_or_404(Infirmier, pk=pk)
    if request.method == "POST":
        infirmier.delete()
    return redirect('admin_Infirmier')




def export_infirmiers_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="infirmiers.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prénom', 'Grade', 'Téléphone', 'Service'])

    for i in Infirmier.objects.all():
        writer.writerow([i.nom, i.prenom, i.grade, i.telephone, i.service.nom_service if i.service else ''])
    
    return response


def export_infirmiers_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Infirmiers"
    ws.append(['Nom', 'Prénom', 'Grade', 'Téléphone', 'Service'])

    for i in Infirmier.objects.all():
        ws.append([i.nom, i.prenom, i.grade, i.telephone, i.service.nom_service if i.service else ''])

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="infirmiers.xlsx"'
    wb.save(response)
    return response

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

def export_infirmiers_pdf(request):
    # Configuration du document
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          rightMargin=40, leftMargin=40,
                          topMargin=60, bottomMargin=60)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Style pour l'en-tête des infirmiers (couleur verte médicale)
    infirmier_header_style = ParagraphStyle(
        'infirmier_header',
        parent=styles['Heading1'],
        textColor=colors.HexColor('#2e7d32'),  # Vert médical
        spaceAfter=12,
        alignment=1
    )
    
    # 1. En-tête avec style spécifique aux infirmiers
    elements.append(Paragraph("<img src='static/blog/img/infirmier.jpg' width='50' height='50'/><br/>", 
                           styles['Normal']))
    elements.append(Paragraph("LISTE DU PERSONNEL INFIRMIER UIT", infirmier_header_style))
    
    # Informations complémentaires
    info_style = ParagraphStyle(
        'info_style',
        parent=styles['Normal'],
        textColor=colors.HexColor('#1b5e20'),
        fontSize=10,
        leading=12
    )
    
    elements.extend([
        Paragraph(f"<b>Hôpital Général de l'UIT</b>", info_style),
        
        Paragraph(f"Service des Soins Infirmiers", info_style),
       
        Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", info_style),
        Spacer(1, 24)
    ])

    # 2. Données des infirmiers - Style différent des médecins
    data = [
        ['ID', 'Nom', 'Prénom', 'Grade', 'Téléphone', 'Service']
    ]
    
    infirmiers = Infirmier.objects.select_related('service').order_by('nom', 'prenom')
    
    for idx, infirmier in enumerate(infirmiers, start=1):
        data.append([
            str(idx),
            infirmier.nom.upper(),
            infirmier.prenom,
            Paragraph(infirmier.grade, styles['Normal']),
            infirmier.telephone or "N/A",
            infirmier.service.nom_service if infirmier.service else "Non affecté"
        ])

    # 3. Style du tableau spécifique aux infirmiers
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#81c784')),  # Vert clair
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8f5e9')),  # Vert très clair
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a5d6a7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # 4. Pied de page spécifique
    footer_style = ParagraphStyle(
        'footer_style',
        parent=styles['Italic'],
        textColor=colors.HexColor('#2e7d32'),
        fontSize=8,
        alignment=1
    )
    
    elements.append(Paragraph(
        "Service des Soins Infirmiers | © Hôpital Général {}".format(datetime.now().year),
        footer_style
    ))

    # Génération du PDF
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_infirmiers_{}.pdf"'.format(
        datetime.now().strftime('%Y%m%d')
    )
    return response
###############################  FIN INFIRMIER ###########


#############   MEDECIN ##############
from django.db.models import Q

def admin_medecin(request):
    # Initialisation des paramètres
    recherche = request.GET.get('recherche', '')
    specialite = request.GET.get('specialite', '')
    service = request.GET.get('service', '')
    
    # Construction de la requête
    medecins = Medecin.objects.all()
    
    if recherche:
        medecins = medecins.filter(
            Q(nom__icontains=recherche) | 
            Q(prenom__icontains=recherche)
        )
    if specialite:
        medecins = medecins.filter(specialite__icontains=specialite)
    
    if service:
        medecins = medecins.filter(service__id=service)
    
    # Préparation du contexte
    context = {
        'medecins': medecins,
        'recherche': recherche,
        'selected_specialite': specialite,
        'selected_service': service,
        'form': MedecinForm(),
        'services': Service.objects.all(),
        'bureaux': Bureau.objects.all(),
        'specialites': Medecin.objects.values_list('specialite', flat=True).distinct()
    }
    return render(request, 'blog/admin_Medecin.html', context)

def ajouter_medecin(request):
    if request.method == 'POST':
        form = MedecinForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('admin_Medecin')





#def modifier_medecin(request, pk):
 #   medecin = get_object_or_404(Medecin, pk=pk)
  #  if request.method == 'POST':
      #  form = MedecinForm(request.POST, instance=medecin)
       # if form.is_valid():
        #    form.save()
    #return redirect('admin_Medecin')

def modifier_medecin(request, pk):
    medecin = get_object_or_404(Medecin, pk=pk)

    if request.method == 'POST':
        medecin.nom = request.POST.get('nom')
        medecin.prenom = request.POST.get('prenom')
        medecin.specialite = request.POST.get('specialite')
        medecin.email = request.POST.get('email')

        # Récupération des objets Service et Bureau à partir des IDs
        service_id = request.POST.get('service')
        bureau_id = request.POST.get('bureau')

        medecin.service = Service.objects.get(id=service_id) if service_id else None
        medecin.bureau = Bureau.objects.get(id=bureau_id) if bureau_id else None

        medecin.save()
        return redirect('admin_Medecin')




def supprimer_medecin(request, pk):
    medecin = get_object_or_404(Medecin, pk=pk)
    if request.method == 'POST':
        medecin.delete()
    return redirect('admin_Medecin')



########## Exporter les médecins au format pdf, excel et csv ##########

from io import BytesIO
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from .models import Medecin

def export_medecin_pdf(request):
    # Configuration du document
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # 1. En-tête professionnel avec logo centré
    logo_path = "static/blog/img/uit.jpg"  # Chemin vers votre logo
    try:
        # Création d'une table pour centrer le logo
        logo_table_data = [
            [Image(logo_path, width=1.5*inch, height=1*inch)]
        ]
        logo_table = Table(logo_table_data, colWidths=[doc.width])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(logo_table)
        elements.append(Spacer(1, 20))  # Espace après le logo
    except:
        # Si le logo n'est pas trouvé, on ajoute juste le titre
        elements.append(Paragraph("<b>HÔPITAL GÉNÉRAL DE L'UIT</b>", 
                               getSampleStyleSheet()['Title']))
        elements.append(Spacer(1, 12))

    # Style personnalisé
    header_style = ParagraphStyle(
        'header',
        parent=styles['Normal'],
        fontSize=12,
        leading=14,
        spaceAfter=6,
        alignment=1  # Centré
    )
    
    # Informations de l'hôpital
    hospital_info = [
        Paragraph("<b>HÔPITAL GÉNÉRAL DE L'UIT</b>", header_style),
        Paragraph("123 Avenue de la Santé", styles['Normal']),
        
        Paragraph("Ville:Thies", styles['Normal']),
        Paragraph("Tél: +33 345 67 78", styles['Normal']),
        Paragraph("Email: uit@univ_hopital.com", styles['Normal']),
        Spacer(1, 12),
        Paragraph("<b>LISTE DES MÉDECINS</b>", styles['Title']),
        Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']),
        Spacer(1, 24)
    ]
    elements.extend(hospital_info)

    # 2. Données des médecins
    data = [
        ['Nom', 'Prénom', 'Spécialité', 'Email', 'Service', 'Bureau']
    ]
    
    medecins = Medecin.objects.select_related('service', 'bureau').order_by('nom', 'prenom')
    
    for medecin in medecins:
        data.append([
            medecin.nom.upper(),
            medecin.prenom,
            medecin.specialite,
            medecin.email or "N/A",
            str(medecin.service) if medecin.service else "N/A",
            str(medecin.bureau) if medecin.bureau else "N/A"
        ])

    # 3. Style du tableau
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005b96')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # 4. Pied de page
    footer = Paragraph(
        "<i>Document confidentiel - © Hôpital Général {}</i>".format(datetime.now().year),
        styles['Italic']
    )
    elements.append(footer)
    
   

    # Génération du PDF
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_medecins_{}.pdf"'.format(
        datetime.now().strftime('%Y%m%d')
    )
    return response



def export_medecin_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Médecins"
    ws.append(['Nom', 'Prénom', 'Spécialité', 'Email', 'Service', 'Bureau'])

    for m in Medecin.objects.all():
        ws.append([m.nom, m.prenom, m.specialite, m.email, str(m.service), str(m.bureau)])

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="medecins.xlsx"'
    wb.save(response)
    return response


def export_medecin_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="medecins.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prénom', 'Spécialité', 'Email', 'Service', 'Bureau'])
    for m in Medecin.objects.all():
        writer.writerow([m.nom, m.prenom, m.specialite, m.email, m.service, m.bureau])
    return response


###############################  FIN MEDECIN ###########
#############   PATIENT ##############


from django.db.models import Q

def admin_Patient(request):
    patients = Patient.objects.select_related('service', 'medecin').all()
    services = Service.objects.all()
    medecins = Medecin.objects.all()

    # Récupération des paramètres
    recherche = request.GET.get('recherche', '')
    selected_service = request.GET.get('service', '')
    selected_medecin = request.GET.get('medecin', '')

    # Application des filtres
    if recherche:
        patients = patients.filter(
            Q(nom__icontains=recherche) | 
            Q(prenom__icontains=recherche)
        )

    if selected_service:
        patients = patients.filter(service__id=selected_service)

    if selected_medecin:
        patients = patients.filter(medecin__id=selected_medecin)

    context = {
        'patients': patients,
        'services': services,
        'medecins': medecins,
        'recherche': recherche,
        'selected_service': selected_service,
        'selected_medecin': selected_medecin
    }
    return render(request, 'blog/admin_Patient.html', context)




def ajouter_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Patient ajouté avec succès.")
    return redirect('admin_Patient')


def modifier_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.warning(request, "✏️ Patient modifié avec succès.")
    return redirect('admin_Patient')


def supprimer_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.error(request, "🗑️ Patient supprimé avec succès.")
    return redirect('admin_Patient')




import csv
from django.http import HttpResponse
from .models import Patient

def export_patients_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="patients.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nom', 'Prénom', 'Date de naissance', 'Sexe', 'Adresse', 'Service', 'Médecin'])

    for patient in Patient.objects.all():
        writer.writerow([
            patient.id,
            patient.nom,
            patient.prenom,
            patient.date_naissance,
            patient.sexe,
            patient.adresse,
            patient.service.nom_service if patient.service else '',
            f"{patient.medecin.prenom} {patient.medecin.nom}" if patient.medecin else ''
        ])
    
    return response
import openpyxl
from openpyxl.styles import Font, PatternFill
from django.http import HttpResponse

def export_patients_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Patients"

    # En-têtes avec style
    headers = ['ID', 'Nom', 'Prénom', 'Date de naissance', 'Sexe', 'Adresse', 'Service', 'Médecin']
    header_fill = PatternFill(start_color="B8CCE4", end_color="B8CCE4", fill_type="solid")
    header_font = Font(bold=True)

    ws.append(headers)
    for col in range(1, len(headers) + 1):
        ws.cell(row=1, column=col).fill = header_fill
        ws.cell(row=1, column=col).font = header_font

    # Lignes de données
    for p in Patient.objects.all():
        ws.append([
            p.id,
            p.nom,
            p.prenom,
            p.date_naissance,
            p.sexe,
            p.adresse,
            p.service.nom_service if p.service else '',
            f"{p.medecin.prenom} {p.medecin.nom}" if p.medecin else ''
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="patients.xlsx"'
    wb.save(response)
    return response
###################
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from django.http import HttpResponse
from .models import Patient

def export_patients_pdf(request):
    # Configuration du document PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="liste_patients.pdf"'

    doc = SimpleDocTemplate(
        response, pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=60, bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    # Titre stylisé
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Heading1'],
        fontSize=15,
        textColor=colors.HexColor('#1E3A8A'),  # Bleu profond
        alignment=1,
        spaceAfter=15
    )

    # Tentative d'ajout du logo
    try:
        logo = Image("static/blog/img/logo1.jpg", width=1.2*inch, height=1*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
    except Exception as e:
        pass  # Continue sans le logo si erreur

    # En-tête
    elements.append(Paragraph("HÔPITAL GÉNÉRAL DE L'UIT", title_style))
    elements.append(Spacer(1, 18))
    header_style = ParagraphStyle(  # Ajout de ce style manquant
        'header_style',
        parent=styles['Heading2'],
        textColor=colors.HexColor('#1a5276'),
        fontSize=14,
        alignment=1,
        spaceAfter=15
    )


    hospital_info = [
        Paragraph("123 Avenue de la Santé", styles['Normal']),
        
        Paragraph("Ville:Thies", styles['Normal']),
        Paragraph("Tél: +33 345 67 78", styles['Normal']),
        Paragraph("Email: uit@univ_hopital.com", styles['Normal']),
        Spacer(1, 12),
        Paragraph("<b>Listes Des patients enregistrés</b>", styles['Title']),
        Spacer(1, 24)
    ]
    elements.extend(hospital_info)
    
    # Données du tableau
    data = [['ID', 'Nom', 'Prénom', 'Naissance', 'Sexe', 'Adresse']]
    patients = Patient.objects.all().order_by('nom', 'prenom')

    for p in patients:
        data.append([
            p.id,
            p.nom.upper(),
            p.prenom,
            p.date_naissance.strftime('%d/%m/%Y') if p.date_naissance else '',
            p.sexe,
            (p.adresse[:35] + '...') if len(p.adresse) > 35 else p.adresse
        ])

    # Création du tableau
    table = Table(data, colWidths=[30, 80, 80, 70, 45, 170], repeatRows=1)

    # Style du tableau
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),  # Bleu Bootstrap
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    # Date de génération
    footer_style = ParagraphStyle(
        'footer_style',
        fontSize=8,
        textColor=colors.HexColor('#6c757d'),
        alignment=2
    )
    elements.append(Paragraph(
        f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        footer_style
    ))

    # Pied de page
    elements.append(Paragraph(
        f"Total : {patients.count()} patients — © {datetime.now().year} Hôpital Général de l'UIT",
        ParagraphStyle(
            'footer_center',
            fontSize=8,
            textColor=colors.HexColor('#6c757d'),
            alignment=1
        )
    ))

    # Générer le PDF
    doc.build(elements)
    return response


############  RV #########
from django.shortcuts import render, redirect, get_object_or_404
from .models import RendezVous
from .forms import RendezVousForm

def admin_RendezVous(request):
    rendezVouss = RendezVous.objects.all()
    recherche = request.GET.get('recherche', '')
    selected_rendezVous = request.GET.get('rendezVous', '')

    # Filtrage par nom du patient
    if recherche:
        rendezVouss = rendezVouss.filter(patient__nom__icontains=recherche)

    # Filtrage par ID
    if selected_rendezVous:
        rendezVouss = rendezVouss.filter(id=selected_rendezVous)

    form = RendezVousForm()  # Formulaire vide pour l’ajout

    context = {
        'rendezVouss': rendezVouss,
        'selected_rendezVous': selected_rendezVous,
        'recherche': recherche,
        'form': form,
        'patients': Patient.objects.all(),
        'medecins': Medecin.objects.all(),

    }
    return render(request, 'blog/admin_RendezVous.html', context)

#  Ajouter un rendez-vous
def ajouter_rendezVous(request):
    if request.method == "POST":
        form = RendezVousForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('admin_RendezVous')
    

#  Modifier un rendez-vous
def modifier_rendezVous(request, pk):
    rendezVous = get_object_or_404(RendezVous, pk=pk)
    if request.method == 'POST':
        form = RendezVousForm(request.POST, instance=rendezVous)
        if form.is_valid():
            form.save()
        return redirect('admin_RendezVous')
    

#  Supprimer un rendez-vous
def supprimer_rendezVous(request, pk):
    rendezVous = get_object_or_404(RendezVous, pk=pk)
    if request.method == 'POST':
        rendezVous.delete()
    return redirect('admin_RendezVous')
# ===============================


########export rendezvous
import csv
from django.http import HttpResponse
from .models import RendezVous

def export_rendezvous_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rendezvous.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Statut', 'Patient', 'Médecin'])

    for rdv in RendezVous.objects.all():
        writer.writerow([
            rdv.date_rdv,
            rdv.statut,
            f"{rdv.patient.prenom} {rdv.patient.nom}",
            f"{rdv.medecin.prenom} {rdv.medecin.nom}" if rdv.medecin else "Non assigné"
        ])

    return response


import openpyxl
from django.http import HttpResponse
from .models import RendezVous
from openpyxl.styles import Font, Alignment, PatternFill



##################

def export_rendezvous_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rendez-vous"

    # En-têtes stylés
    headers = ['Date', 'Statut', 'Patient', 'Médecin']
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="4F81BD")

    ws.append(headers)
    for col in ws.iter_cols(min_row=1, max_row=1, min_col=1, max_col=len(headers)):
        for cell in col:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')

    # Données
    for rdv in RendezVous.objects.all():
        ws.append([
            str(rdv.date_rdv),
            rdv.statut,
            f"{rdv.patient.prenom} {rdv.patient.nom}",
            f"{rdv.medecin.prenom} {rdv.medecin.nom}" if rdv.medecin else "Non assigné"
        ])

    # Réponse
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="rendezvous.xlsx"'
    wb.save(response)
    return response
########################

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from .models import RendezVous

def export_rendezvous_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rendezvous.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 3 * cm

    p.setFont("Helvetica-Bold", 16)
    p.drawString(5 * cm, y, "Liste des Rendez-vous")
    y -= 2 * cm

    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * cm, y, "Date")
    p.drawString(5 * cm, y, "Statut")
    p.drawString(9 * cm, y, "Patient")
    p.drawString(14 * cm, y, "Médecin")
    y -= 1 * cm

    p.setFont("Helvetica", 11)
    for rdv in RendezVous.objects.all():
        if y < 2 * cm:
            p.showPage()
            y = height - 2 * cm
        p.drawString(1 * cm, y, str(rdv.date_rdv))
        p.drawString(5 * cm, y, rdv.statut)
        p.drawString(9 * cm, y, f"{rdv.patient.prenom} {rdv.patient.nom}")
        p.drawString(14 * cm, y, f"{rdv.medecin.prenom} {rdv.medecin.nom}" if rdv.medecin else "N/A")
        y -= 0.7 * cm

    p.showPage()
    p.save()
    return response

