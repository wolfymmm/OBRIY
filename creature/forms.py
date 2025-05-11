from django import forms
from .models import Creature
from django import forms
from .models import CreatureDraft

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

