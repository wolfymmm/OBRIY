from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from creature import views
from django.contrib.auth import views as auth_views
from creature.views import CustomLoginView, moderation_queue, approve_draft, reject_draft, admin_dashboard, \
    custom_logout, user_profile
from creature.views import create_creature_draft, draft_submitted

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('creatures/', views.creature_list, name='creature_list'),
    path('usage/', views.usage, name='usage'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
    path('about_us/', views.about_us, name='about_us'),

    # Авторизація
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('register/', views.register_view, name='register'),

    # Профілі
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('profile/', user_profile, name='user_profile'),

    # ... інші URL ...
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    # ... інші URL ...

    # Чернетки
    path('creature/create/', create_creature_draft, name='create_draft'),
    path('draft-submitted/', draft_submitted, name='draft_submitted'),

    # Модерація
    path('moderation/', moderation_queue, name='moderation_queue'),
    path('moderation/approve/<int:draft_id>/', approve_draft, name='approve_draft'),
    path('moderation/reject/<int:draft_id>/', reject_draft, name='reject_draft'),

    # Істоти

    path('creature/<int:creature_id>/', views.chuhaister, name='chuhaister'),
    path('creature/<int:creature_id>/edit/', views.edit_creature, name='edit_creature'),
    path('creature/<int:creature_id>/history/', views.creature_history, name='creature_history'),
    path('search/', views.search_creatures, name='search_creatures'),

    # Сповіщення
    path('notifications/', include('django_nyt.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
