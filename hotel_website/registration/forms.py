from django import forms
from main.models import CustomUser



class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            return email
        raise forms.ValidationError("No user registered with this email address.")
