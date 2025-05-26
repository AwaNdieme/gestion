from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]

# Ajouter les fichiers statiques correctement
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
# OU, si tu utilises STATIC_ROOT pour le déploiement
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
