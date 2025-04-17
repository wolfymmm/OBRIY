from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from creature import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Головна сторінка
    path('creatures/', views.creature_list, name='creature_list'),
    path('notifications/', include('django_nyt.urls')),  # Підключення notifications
    path('wiki/', include('wiki.urls')),  # Підключення для додатку wiki
]

# Додаємо обробку медійних файлів для локального сервера
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
