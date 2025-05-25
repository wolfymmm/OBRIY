from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from creature.models import User
from django.contrib.auth import login
from .models import Creature, CreatureDraft, AdminActionLog
from .forms import CreatureForm, RegisterForm
from django.contrib.admin.views.decorators import staff_member_required
import logging
logger = logging.getLogger(__name__)


def search_creatures(request):
    query = request.GET.get('q')
    results = []
    exact_match = False

    if query:
        exact_results = Creature.objects.filter(name__iexact=query)
        if exact_results.exists():
            results = exact_results
            exact_match = True
        else:
            results = Creature.objects.filter(
                name__icontains=query
            ) | Creature.objects.filter(
                type__icontains=query
            ) | Creature.objects.filter(
                region__icontains=query
            )

    return render(request, 'search_results.html', {
        'results': results,
        'query': query,
        'exact_match': exact_match
    })


def is_admin(user):
    return user.is_staff


def check_auth(request):
    if not request.user.is_authenticated:
        return redirect('edit_auth_required')
    return None

@login_required
def edit_creature(request, creature_id):
    creature = get_object_or_404(Creature, id=creature_id)

    if request.method == 'POST':
        form = CreatureForm(request.POST, instance=creature)

        if form.is_valid():
            if request.user.is_staff:
                form.save()

                AdminActionLog.objects.create(
                    user=request.user,
                    action='edit',
                    object_type='Creature',
                    object_id=creature.id,
                    object_name=creature.name,
                    details='Редагування існуючої істоти адміністратором.'
                )

                messages.success(request, 'Зміни успішно збережено.')
                return redirect('chuhaister', creature_id=creature.id)

            else:
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

                AdminActionLog.objects.create(
                    user=request.user,
                    action='create',
                    object_type='CreatureDraft',
                    object_id=draft.id,
                    object_name=draft.name,
                    details=f'Запит на редагування істоти #{creature.id} ({creature.name})'
                )

                messages.success(request, 'Запит на редагування надіслано на модерацію.')
                return redirect('draft_submitted')

    else:
        form = CreatureForm(instance=creature)

    return render(request, 'edit_creature.html', {
        'form': form,
        'creature': creature
    })

@user_passes_test(is_admin)
def approve_creature_drafts(request):
    drafts = CreatureDraft.objects.filter(is_approved=False)
    return render(request, 'approve_draft.html', {'drafts': drafts})


@user_passes_test(is_admin)
def approve_draft(request, draft_id):
    draft = get_object_or_404(CreatureDraft, id=draft_id)

    if request.method == 'POST':
        creature = None

        if draft.creature:
            creature = draft.creature
        else:
            creature = Creature.objects.filter(name__iexact=draft.name).first()

        if creature:
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
            draft.save()
            symbols = request.POST.get('symbols', '')
            if symbols:
                draft.symbols = [s.strip() for s in symbols.split(',')]
                draft.save(update_fields=['symbols'])

            AdminActionLog.objects.create(
                user=request.user,
                action='create',
                object_type='CreatureDraft',
                object_id=draft.id,
                object_name=draft.name,
                details='Створено нову чернетку істоти'
            )

            messages.success(request, 'Чернетку успішно надіслано на модерацію!')
            return redirect('draft_submitted')

        except Exception as e:
            messages.error(request, f'Помилка при збереженні: {str(e)}')
            return render(request, 'create_draft.html', {'form_data': request.POST})

    return render(request, 'create_draft.html')


@staff_member_required
def admin_dashboard(request):

    pending_count = CreatureDraft.objects.filter(
        is_approved=False,
        is_rejected=False
    ).count()


    total_articles = Creature.objects.count()
    rejected_count = CreatureDraft.objects.filter(is_rejected=True).count()
    users_count = User.objects.filter(is_active=True).count()
    recent_actions = AdminActionLog.objects.select_related('user').order_by('-timestamp')[:5]

    context = {
        'pending_count': pending_count,
        'total_articles': total_articles,
        'rejected_count': rejected_count,
        'users_count': users_count,
        'recent_actions': recent_actions,
    }

    return render(request, 'admin_dashboard.html', context)

def log_admin_action(user, action, obj, details=''):
    AdminActionLog.objects.create(
        user=user,
        action=action,
        object_type=obj.__class__.__name__,
        object_id=obj.id,
        object_name=str(obj),
        details=details
    )

    log_admin_action(request.user, 'create', instance)

@staff_member_required
def moderation_queue(request):
    drafts = CreatureDraft.objects.filter(is_approved=False, is_rejected=False)
    return render(request, 'moderation_queue.html', {'drafts': drafts})


@staff_member_required
def reject_draft(request, draft_id):
    draft = get_object_or_404(CreatureDraft, id=draft_id)

    if request.method == 'POST':
        draft.admin_comment = request.POST.get('comment', '')
        draft.is_rejected = True
        draft.save()
        messages.success(request, 'Чернетку успішно відхилено')
        return redirect('moderation_queue')

    return render(request, 'reject_draft.html', {'draft': draft})

def draft_submitted(request):
    return render(request, 'draft_submitted.html')

def creature_history(request, creature_id):
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

@login_required
def profile_settings(request):
    return render(request, 'profile_settings.html')