from django import forms
from .models import Booking, CustomUser, Room
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('check_in', 'check_out', 'quantity')

    check_in = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'  # Example placeholder
            }
        )
    )
    check_out = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'  # Example placeholder
            }
        )
    )


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'phone_number', 'address', 'email', 'first_name', 'last_name']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ['username', 'phone_number', 'address', 'email', 'first_name', 'last_name', 'password1', 'password2']       


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
