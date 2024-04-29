import random

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy, reverse
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView, FormView
from django.views.decorators.http import require_POST

from .forms import (
    EmailForm,
    EmailAuthenticationForm,
    PasswordForm,
    PasswordResetForm,
    PasswordResetEmailForm,
    RegistrationCodeForm,
)
from .models import AuthenticationCode

User = get_user_model()

class HomeView(TemplateView):
    template_name = "main/home.html"

def generate_random_code(email):
    random_number = get_random_string(4, "0123456789")
    AuthenticationCode.objects.update_or_create(
        email=email, defaults={"code": random_number}
    )
    return random_number

def registration_send_email(email):
    random_code = generate_random_code(email)
    context = {
        "email": email,
        "random_code": random_code,
    }
    subject = "Video Appの本登録について"
    message = render_to_string("mail_text/registration.txt", context)
    from_email = None
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def password_reset_send_email(email):
    random_code = generate_random_code(email)
    context = {
        "email": email,
        "random_code": random_code,
    }
    subject = "パスワード再設定について"
    message = render_to_string("mail_text/password_reset.txt", context)
    from_email = None
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

class TempRegistrationView(FormView):
    template_name = "main/temp_registration.html"
    form_class = EmailForm

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        self.token = signing.dumps(email)
        registration_send_email(email)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("temp_registration_done", kwargs={"token": self.token})

class TempRegistrationDoneView(FormView):
    template_name = "main/temp_registration_done.html"
    form_class = RegistrationCodeForm

    def dispatch(self, request, *args, **kwargs):
        self.token = self.kwargs["token"]
        try:
            self.email = signing.loads(self.token)
        except signing.BadSignature:
            return HttpResponseBadRequest("不正なURLです。")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.email
        context["token"] = self.token
        return context

    def get_success_url(self):
        return reverse("signup", kwargs={"token": self.token})
    
@require_POST
def resend_registration_email(request, token):
    try:
        email = signing.loads(token)
    except signing.BadSignature:
        return HttpResponseBadRequest("不正なURLです。")
    form = RegistrationCodeForm
    registration_send_email(email)
    messages.success(request, "入力されたメールアドレスに送信しました。")
    context = {
        "form": form,
        "email":email,
        "token": token,
    }
    return render(request, "main/temp_registration_done.html", context)

class SignUpView(FormView):
    template_name = "main/signup.html"
    form_class = PasswordForm
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        self.token = self.kwargs["token"]
        try:
            self.email = signing.loads(self.token)
        except signing.BadSignature:
            return HttpResponseBadRequest("不正なURLです。")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        password = form.cleaned_data["password"]
        password = make_password(password)
        User.objects.create(username="ゲスト", email=self.email, password=password)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.email
        return context


class LoginView(LoginView):
    template_name = "main/login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True


class PasswordResetEmailView(FormView):
    template_name = "main/password_reset_email.html"
    form_class = PasswordResetEmailForm

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        self.token = signing.dumps(email)
        password_reset_send_email(email)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("password_reset_confirmation", kwargs={"token": self.token})
    
class PasswordResetConfirmationView(FormView):
    template_name = "main/password_reset_confirmation.html"
    form_class = RegistrationCodeForm

    def dispatch(self, request, *args, **kwargs):
        self.token = self.kwargs["token"]
        try:
            self.email = signing.loads(self.token)
        except signing.BadSignature:
            return HttpResponseBadRequest("不正なURLです。")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs["email"] = self.email
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["token"] = self.token
        context["email"] = self.email
        return context

    def get_success_url(self):
        return reverse("password_reset", kwargs={"token": self.token})
    
@require_POST
def resend_password_reset_email(request, token):
    try:
        email = signing.loads(token)
    except signing.BadSignature:
        return HttpResponseBadRequest("不正なURLです。")
    form = RegistrationCodeForm
    password_reset_send_email(email)
    messages.success(request, "入力されたメールアドレスに送信しました。")
    context = {
        "form": form,
        "email": email,
        "token": token,
    }
    return render(request, "main/password_reset_confirmation.html", context)

class PasswordResetView(FormView):
    template_name = "main/password_reset.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        self.token = self.kwargs["token"]
        try:
            self.email = signing.loads(self.token)[0]
        except signing.BadSignature:
            return HttpResponseBadRequest("不正なURLです。")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        new_password = form.cleaned_data["new_password1"]
        new_password = make_password(new_password)
        user = User.objects.filter(email=self.email)
        user.update(password=new_password)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.email
        return context