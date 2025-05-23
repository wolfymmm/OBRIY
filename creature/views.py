from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from creature.models import User
from django.contrib.auth import login
from django.utils import timezone
from datetime import timedelta
from django.views import View
from .models import Creature, CreatureDraft, AdminActionLog
from django.contrib.auth.hashers import make_password
from .forms import CreatureForm, CreatureDraftForm, RegisterForm
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
import logging
logger = logging.getLogger(__name__)


# Функція для перевірки, чи є користувач адміністратором
def is_admin(user):
    return user.is_staff

# Перевірка доступу для неавторизованих користувачів
def check_auth(request):
    if not request.user.is_authenticated:
        return redirect('edit_auth_required')  # Перенаправлення на сторінку для неавторизованих
    return None

# Сторінка редагування для авторизованих користувачів
@login_required
def edit_creature(request, creature_id):
    creature = get_object_or_404(Creature, id=creature_id)

    if request.method == 'POST':
        form = CreatureForm(request.POST, instance=creature)

        if form.is_valid():
            if request.user.is_staff:  # Якщо користувач є адміністратором
                form.save()  # Зберігаємо зміни в базі
                messages.success(request, 'Зміни успішно збережено.')
                return redirect('creature_detail', creature_id=creature.id)
            else:
                # Якщо користувач не адміністратор, створюємо запит на редагування
                draft = CreatureDraft(
                    author=request.user,
                    name=form.cleaned_data['name'],
                    type=form.cleaned_data['type'],
                    region=form.cleaned_data['region'],
                    appearance=form.cleaned_data['appearance'],
                    behavior=form.cleaned_data['behavior'],
                    role_in_mythology=form.cleaned_data['role_in_mythology'],
                    description=form.cleaned_data.get('description', ''),
                    sources=form.cleaned_data.get('sources', ''),
                    image_url=form.cleaned_data.get('image_url', '')
                )
                draft.save()
                messages.success(request, 'Запит на редагування надіслано на модерацію.')
                return redirect('draft_submitted')  # Перенаправлення на сторінку підтвердження
    else:
        form = CreatureForm(instance=creature)

    return render(request, 'edit_creature.html', {
        'form': form,
        'creature': creature
    })


# Перевірка доступу для неавторизованих користувачів
def edit_auth_required(request):
    return render(request, 'edit_auth_required.html')

# Відображення чернеток для адміністраторів
@user_passes_test(is_admin)
def approve_creature_drafts(request):
    drafts = CreatureDraft.objects.filter(is_approved=False)
    return render(request, 'approve_draft.html', {'drafts': drafts})


@user_passes_test(is_admin)
def approve_draft(request, draft_id):
    draft = get_object_or_404(CreatureDraft, id=draft_id)

    if request.method == 'POST':
        # Визначаємо, яку істоту оновлювати чи створювати
        creature = None

        if draft.creature:
            # Чернетка редагування: оновлюємо існуючу істоту
            creature = draft.creature
        else:
            # Чернетка створення: перевіряємо, чи така істота вже є
            creature = Creature.objects.filter(name__iexact=draft.name).first()

        if creature:
            # Оновлюємо наявну істоту
            creature.name = draft.name
            creature.type = draft.type
            creature.region = draft.region
            creature.appearance = draft.appearance
            creature.behavior = draft.behavior
            creature.role_in_mythology = draft.role_in_mythology
            creature.description = draft.description
            creature.sources = draft.sources
            creature.image_url = draft.image_url
            creature.save()
        else:
            # Створюємо нову істоту
            creature = Creature.objects.create(
                name=draft.name,
                type=draft.type,
                region=draft.region,
                appearance=draft.appearance,
                behavior=draft.behavior,
                role_in_mythology=draft.role_in_mythology,
                description=draft.description,
                sources=draft.sources,
                image_url=draft.image_url
            )

        draft.is_approved = True
        draft.save()

        messages.success(request, 'Чернетку було успішно опубліковано!')
        return redirect('approve_creature_drafts')

    return render(request, 'approve_draft.html', {'draft': draft})



@login_required
def create_creature_draft(request):
    if request.method == 'POST':
        try:
            # Отримуємо дані з форми
            draft = CreatureDraft(
                author=request.user,
                name=request.POST.get('name'),
                type=request.POST.get('type'),
                region=request.POST.get('region'),
                appearance=request.POST.get('appearance'),
                behavior=request.POST.get('behavior'),
                role_in_mythology=request.POST.get('role_in_mythology'),
                description=request.POST.get('description', ''),
                sources=request.POST.get('sources', ''),
                image_url=request.POST.get('image_url', '')
            )

            # Обробляємо символи
            symbols = request.POST.get('symbols', '')
            if symbols:
                draft.symbols = [s.strip() for s in symbols.split(',')]

            draft.save()
            messages.success(request, 'Чернетку успішно надіслано на модерацію!')
            return redirect('draft_submitted')

        except Exception as e:
            messages.error(request, f'Помилка при збереженні: {str(e)}')
            return render(request, 'create_draft.html', {'form_data': request.POST})

    return render(request, 'create_draft.html')


@staff_member_required
def admin_dashboard(request):
    """
    Адмін-панель для персоналу
    """
    pending_count = CreatureDraft.objects.filter(
        is_approved=False,
        is_rejected=False
    ).count()

    total_articles = Creature.objects.count()
    rejected_count = CreatureDraft.objects.filter(is_rejected=True).count()

    # Використовуємо вашу кастомну модель User
    users_count = User.objects.filter(is_active=True).count()

    recent_actions = AdminActionLog.objects.select_related('user') \
                         .order_by('-timestamp')[:5]

    context = {
        'pending_count': pending_count,
        'total_articles': total_articles,
        'rejected_count': rejected_count,
        'users_count': users_count,
        'recent_actions': recent_actions,
    }

    return render(request, 'admin_dashboard.html', context)

@staff_member_required
def moderation_queue(request):
    """Черга модерації статей"""
    drafts = CreatureDraft.objects.filter(is_approved=False, is_rejected=False)
    return render(request, 'moderation_queue.html', {'drafts': drafts})


@staff_member_required
def reject_draft(request, draft_id):
    """Відхилення чернетки статті"""
    draft = get_object_or_404(CreatureDraft, id=draft_id)

    if request.method == 'POST':
        draft.admin_comment = request.POST.get('comment', '')
        draft.is_rejected = True
        draft.save()
        messages.success(request, 'Чернетку успішно відхилено')
        return redirect('moderation_queue')

    return render(request, 'reject_draft.html', {'draft': draft})

def draft_submitted(request):
    """Підтвердження відправки чернетки"""
    return render(request, 'draft_submitted.html')

def creature_history(request, creature_id):
    """Історія змін статті"""
    creature = get_object_or_404(Creature, id=creature_id)
    history = creature.history.order_by('-edited_at')
    return render(request, 'creature_history.html', {'creature': creature, 'history': history})


# Основні сторінки
def home(request):
    return render(request, 'home.html')


def usage(request):
    return render(request, 'usage.html')


def about_us(request):
    return render(request, 'about_us.html')


def creature_list(request):
    creatures = Creature.objects.all()
    return render(request, 'creature_list.html', {'creatures': creatures})


def chuhaister(request, creature_id):
    creature = get_object_or_404(Creature, id=creature_id)
    return render(request, 'chuhaister.html', {'creature': creature})


# Авторизація


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def user_profile(request):
    return render(request, 'user_profile.html')


class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('admin_dashboard')
        return reverse_lazy('user_profile')


def custom_logout(request):
    logout(request)
    return redirect('home')


# Допоміжні функції
def create_admin_log_entry(user, action, object_type, object_id, object_name, details=''):
    """Створення запису в лог адмін-дій"""
    AdminActionLog.objects.create(
        user=user,
        action=action,
        object_type=object_type,
        object_id=object_id,
        object_name=object_name,
        details=details
    )

@login_required
def user_profile(request):
    return render(request, 'user_profile.html')
