from django import forms
from .models import Booking, CustomUser, Room
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

# class BookingForm(forms.ModelForm):
#     room_types = forms.ModelMultipleChoiceField(
#         queryset=Room.objects.all(),
#         widget=forms.CheckboxSelectMultiple,

#     )

#     quantities = forms.CharField(
#         widget=forms.HiddenInput()
#     )

#     class Meta:
#         model = Booking
#         fields = ['check_in', 'check_out']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('check_in', 'check_out', 'quantity', 'room')

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




# class RoomSelectionForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         room_types = Room.objects.all()
#         for room_type in room_types:
#             field_name = f"quantity_{room_type.id}"
#             self.fields[field_name] = forms.IntegerField(label=f"{room_type.name} Quantity", required=False)

#     def clean(self):
#         cleaned_data = super().clean()
#         for field_name, value in cleaned_data.items():
#             if field_name.startswith("quantity_") and value:
#                 room_type_id = int(field_name.split("_")[1])
#                 room_type = Room.objects.get(id=room_type_id)
#                 if value < 1:
#                     self.add_error(field_name, "Quantity must be a positive integer")
#         return cleaned_data


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
