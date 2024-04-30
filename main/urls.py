from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "temp_registration",
        views.TempRegistrationView.as_view(),
        name="temp_registration",
    ),
    path(
        "temp_registration_done/<token>",
        views.TempRegistrationDoneView.as_view(),
        name="temp_registration_done",
    ),
    path(
        "signup/<token>",
        views.SignUpView.as_view(),
        name="signup",
    ),
    path(
        "temp_registration_done/<token>/resend",
        views.resend_registration_email,
        name="registration_resend",
    ),
    path("login", views.LoginView.as_view(), name="login"),
    path(
        "password_reset_email",
        views.PasswordResetEmailView.as_view(),
        name="password_reset_email",
    ),
    path(
        "password_reset_confirmation/<token>",
        views.PasswordResetConfirmationView.as_view(),
        name="password_reset_confirmation",
    ),
    path(
        "password_reset/<token>",
        views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset_confirmation/<token>/resend",
        views.resend_password_reset_email,
        name="password_reset_resend",
    ),
    path("video_upload", views.VideoUploadView.as_view(), name="video_upload"),
    path("search_video", views.SearchVideoView.as_view(), name="search_video"),
]
