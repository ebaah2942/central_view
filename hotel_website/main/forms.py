from django import forms
from .models import Booking, CustomUser, Room, Inquiry, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.utils import timezone



class BookingForm(forms.ModelForm):
    check_in = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }
        )
    )
    check_out = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }
        )
    )

    class Meta:
        model = Booking
        fields = ('check_in', 'check_out', 'quantity')

    def clean_check_in(self):
        check_in = self.cleaned_data.get('check_in')
        if check_in and check_in < timezone.now().date():
            raise forms.ValidationError("Check-in date cannot be in the past.")
        return check_in

    def clean_check_out(self):
        check_out = self.cleaned_data.get('check_out')
        if check_out and check_out < timezone.now().date():
            raise forms.ValidationError("Check-out date cannot be in the past.")
        return check_out




class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'phone_number', 'address', 'email', 'first_name', 'last_name', 'wants_emails']

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




class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your message here...'})
        }

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['response']
        widgets = {
            'response': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your response here...'})
        }  

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone_number', 'address', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password'] 



class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ["old_password", "new_password1", "new_password2"]
                  


class EmailPreferenceForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['wants_emails']
        labels = {
            'wants_emails': 'I want to receive email notifications',
        }                  




class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = Review
        fields = ['rating', 'comment']        