from django.urls import path
from .views import (
    custom_password_reset_request,
    custom_password_reset_confirm,
    custom_password_reset_done,
    custom_password_reset_complete,
)


urlpatterns = [
    path("password_reset/", custom_password_reset_request, name="custom_password_reset_request"),
    path("password_reset_done/", custom_password_reset_done, name="custom_password_reset_done"),
    path("password_reset_confirm/<uidb64>/<token>/", custom_password_reset_confirm, name="custom_password_reset_confirm"),
    path("password_reset_complete/", custom_password_reset_complete, name="custom_password_reset_complete"),
]
