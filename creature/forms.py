from django import forms
from .models import Creature

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
