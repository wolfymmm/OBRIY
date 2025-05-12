from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.views import View
from .models import Creature, CreatureHistory, CreatureDraft, AdminActionLog
from .forms import CreatureForm, CreatureDraftForm
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin


def edit_creature(request, creature_id):
    creature = get_object_or_404(Creature, id=creature_id)  # Отримуємо істоту тут

    if not request.user.is_authenticated:
        return render(request, 'edit_auth_required.html', {
            'creature': creature  # Передаємо об'єкт істоти у шаблон
        })

    if request.method == 'POST':
        form = CreatureForm(request.POST, instance=creature)
        if form.is_valid():
            form.save()
            return redirect('chuhaister', creature_id=creature.id)
    else:
        form = CreatureForm(instance=creature)

    return render(request, 'edit_creature.html', {
        'form': form,
        'creature': creature
    })
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
    """Адмін-панель для суперкористувачів"""
    pending_count = CreatureDraft.objects.filter(is_approved=False, is_rejected=False).count()
    total_articles = Creature.objects.count()
    rejected_count = CreatureDraft.objects.filter(is_rejected=True).count()
    users_count = User.objects.count()

    recent_actions = AdminActionLog.objects.all().order_by('-timestamp')[:5]

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
def approve_draft(request, draft_id):
    """Затвердження чернетки статті"""
    draft = get_object_or_404(CreatureDraft, id=draft_id)

    try:
        creature = Creature.objects.create(
            name=draft.name,
            type=draft.type,
            region=draft.region,
            appearance=draft.appearance,
            behavior=draft.behavior,
            role_in_mythology=draft.role_in_mythology,
            symbols=draft.symbols,
            description=draft.description,
            sources=draft.sources,
            image_url=draft.image_url
        )

        AdminActionLog.objects.create(
            user=request.user,
            action='approve',
            object_type='creature',
            object_id=creature.id,
            object_name=creature.name,
            details=f'Затверджено чернетку {draft.name}'
        )

        draft.delete()
        messages.success(request, f'Статтю "{creature.name}" успішно опубліковано!')
        return redirect('moderation_queue')

    except Exception as e:
        messages.error(request, f'Помилка при затвердженні: {str(e)}')
        return redirect('moderation_queue')


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
    return render(request, 'register.html')


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