from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from creature import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Головна сторінка
    path('creatures/', views.creature_list, name='creature_list'),
    path('usage/', views.usage, name='usage'),
    path('about_us/', views.about_us, name='about_us'),

    path('login/', views.login_view, name='login'),

    path('user_profile/', views.user_profile, name='user_profile'),
    path('register/', views.register_view, name='register'),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('creature/<int:creature_id>/', views.chuhaister, name='chuhaister'),
    path('creature/<int:creature_id>/edit/', views.edit_creature, name='edit_creature'),
    path('creature/<int:creature_id>/history/', views.creature_history, name='creature_history'),

    path('notifications/', include('django_nyt.urls')),  # Підключення notifications
    path('wiki/', include('wiki.urls')),  # Підключення для додатку wiki
]

# Додаємо обробку медійних файлів для локального сервера
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
