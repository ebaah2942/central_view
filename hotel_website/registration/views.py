from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.urls import reverse
from .forms import CustomPasswordResetForm
from main.models import CustomUser

# Create your views here.




def custom_password_reset_request(request):
    form = CustomPasswordResetForm()  # Initialize form at the beginning to avoid UnboundLocalError

    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = CustomUser.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = request.build_absolute_uri(
                    reverse("custom_password_reset_confirm", kwargs={"uidb64": uid, "token": token})
                )

                # Send the email
                send_mail(
                    "Reset Your Password",
                    f"Click the link to reset your password: {reset_url}",
                    "acvh@accracentralviewhotels.com",
                    [email],
                    fail_silently=False,
                )
                messages.success(request, "A password reset link has been sent to your email.")
                return redirect("custom_password_reset_done")
            except CustomUser.DoesNotExist:
                messages.error(request, "No user found with this email.")
    
    return render(request, "registration/custom_password_reset_form.html", {"form": form})

def custom_password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect("custom_password_reset_complete")
            else:
                messages.error(request, "Passwords do not match.")

        return render(request, "registration/custom_password_reset_confirm.html")
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect("custom_password_reset_request")

    

def custom_password_reset_done(request):
    return render(request, "registration/custom_password_reset_done.html")    



def custom_password_reset_complete(request):
    return render(request, "registration/custom_password_reset_complete.html")