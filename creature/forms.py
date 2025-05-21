from django import forms
from .models import Creature
from .models import CreatureDraft
from .models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Role



class CreatureDraftForm(forms.ModelForm):
    symbols = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Введіть символи через кому'}),
        help_text="Наприклад: вогонь, вода, вітер"
    )

    class Meta:
        model = CreatureDraft
        fields = [
            'name', 'type', 'region', 'appearance',
            'behavior', 'role_in_mythology', 'symbols',
            'description', 'sources', 'image_url'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'sources': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_symbols(self):
        data = self.cleaned_data.get('symbols', '')
        if data:
            return [symbol.strip() for symbol in data.split(',')]
        return []

class CreatureForm(forms.ModelForm):
    class Meta:
        model = Creature
        fields = [
            'name', 'type', 'region',
            'appearance', 'behavior',
            'role_in_mythology', 'description',
            'sources', 'image_url'
        ]

        widgets = {
            'appearance': forms.Textarea(attrs={'rows': 3}),
            'behavior': forms.Textarea(attrs={'rows': 3}),
            'role_in_mythology': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'sources': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_symbols(self):
        data = self.cleaned_data['symbols']
        if data:
            return [s.strip() for s in data.split(',')]
        return []


class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True, label="Ім'я")
    surname = forms.CharField(max_length=100, required=True, label="Прізвище")
    email = forms.EmailField(required=True, label="Email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Використовуємо .all() з ітератором для уникнення проблем з курсором
        self.fields['role'] = forms.ModelChoiceField(
            queryset=Role.objects.all().iterator(),
            required=True,
            label="Роль"
        )

    profile_picture = forms.ImageField(
        required=False,
        label="Фото профілю"
    )

    class Meta:
        model = User
        fields = ['username', 'name', 'surname', 'email', 'password1', 'password2', 'role', 'profile_picture']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.name = self.cleaned_data['name']
        user.surname = self.cleaned_data['surname']
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']

        if commit:
            user.save()
        return user