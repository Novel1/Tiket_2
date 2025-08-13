from django import forms
from .models import Rental

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['rental_period']
        widgets = {
            'rental_period': forms.Select(attrs={'class': 'form-select'}),
        }