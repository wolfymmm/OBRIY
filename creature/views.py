from django.shortcuts import render, get_object_or_404, redirect
from .models import Creature,  CreatureHistory
from .forms import CreatureForm
from django.contrib.auth import authenticate, login

def edit_creature(request, creature_id):
    creature = get_object_or_404(Creature, id=creature_id)

    if request.method == 'POST':
        form = CreatureForm(request.POST, instance=creature)

        if form.is_valid():
            # Зберегти стару версію в історію
            CreatureHistory.objects.create(
                creature=creature,
                name=creature.name,
                type=creature.type,
                behavior=creature.behavior,
                appearance=creature.appearance,
            )

            # Зберегти зміни у формі
            updated_creature = form.save(commit=False)

            # Обробити symbols
            symbols_list = request.POST.getlist('symbols')
            updated_creature.symbols = symbols_list

            updated_creature.save()
            return redirect('chuhaister', creature_id=creature.id)
    else:
        form = CreatureForm(instance=creature)

    return render(request, 'edit_creature.html', {
        'form': form,
        'creature': creature
    })


def creature_history(request, creature_id):
    creature = get_object_or_404(Creature, id=creature_id)
    history = creature.history.order_by('-edited_at')
    return render(request, 'creature_history.html', {'creature': creature, 'history': history})


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


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
        else:
            from django.contrib import messages
            messages.error(request, 'Невірний логін або пароль')

    return render(request, 'login.html')


def register_view(request):
    # You'll need to implement registration logic here
    return render(request, 'register.html')  # Create this template if needed


def user_profile(request):
    # You'll need to implement registration logic here
    return render(request, 'user_profile.html')