from django.shortcuts import render
from .models import Creature # Зверніть увагу на крапку перед models!

def home(request):
    return render(request, 'home.html')

def creature_list(request):
    creatures = Creature.objects.all()
    return render(request, 'creature_list.html', {'creatures': creatures})