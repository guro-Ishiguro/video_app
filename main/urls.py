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
    path("video_play/<int:pk>", views.PlayVideoView.as_view(), name="video_play"),
    path(
        "account/<int:pk>",
        views.AccountView.as_view(),
        name="account",
    ),
    path(
        "following",
        views.FollowingView.as_view(),
        name="following",
    ),
    path(
        "follow/<int:pk>",
        views.FollowView.as_view(),
        name="follow",
    ),
    path(
        "unfollow/<int:pk>",
        views.UnfollowView.as_view(),
        name="unfollow",
    ),
    path(
        "terms",
        views.TermsView.as_view(),
        name="terms",
    ),
    path(
        "privacy_policy",
        views.PrivacyPolicyView.as_view(),
        name="privacy_policy",
    ),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("email_reset", views.EmailResetView.as_view(), name="email_reset"),
    path(
        "email_reset_confirmation/<token>",
        views.EmailResetConfirmationView.as_view(),
        name="email_reset_confirmation",
    ),
    path(
        "email_reset_confirmation/<token>/resend",
        views.resend_email_reset_email,
        name="email_reset_resend",
    ),
    path(
        "password_change/", views.PasswordChangeView.as_view(), name="password_change"
    ),
    path(
        "account_delete",
        views.AccountDeleteView.as_view(),
        name="account_delete",
    ),
    path(
        "account_delete_done",
        views.AccountDeleteDoneView.as_view(),
        name="account_delete_done",
    ),
    path(
        "account_update",
        views.AccountUpdateView.as_view(),
        name="account_update",
    ),
    path("video_update/<int:pk>", views.VideoUpdateView.as_view(), name="video_update"),
    path("video_delete/<int:pk>", views.video_delete, name="video_delete"),
]
