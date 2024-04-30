import random

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import signing
from django.core.mail import send_mail
from django.db.models import Case, Count, Prefetch, When
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy, reverse
from django.utils.crypto import get_random_string
from django.views import View
from django.views.generic import FormView, TemplateView, ListView, DetailView, DeleteView, UpdateView
from django.views.decorators.http import require_POST

from .forms import (
    AccountUpdateForm,
    EmailForm,
    EmailAuthenticationForm,
    PasswordForm,
    PasswordResetForm,
    PasswordChangeForm,
    PasswordResetEmailForm,
    RegistrationCodeForm,
    ViewsCountForm,
    VideoUploadForm,
    VideoSearchForm,
)
from .models import AuthenticationCode, Video

User = get_user_model()


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = Video.objects.all().order_by("-uploaded_at")
        context["videos"] = video
        return context


def generate_random_code(email):
    random_number = get_random_string(4, "0123456789")
    AuthenticationCode.objects.update_or_create(
        email=email, defaults={"code": random_number}
    )
    return random_number


def email_reset_send_email(email):
    random_code = generate_random_code(email)
    context = {
        "email": email,
        "random_code": random_code,
    }
    subject = "メール再設定について"
    message = render_to_string("mail_text/email_reset.txt", context)
    from_email = None
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


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


@require_POST
def resend_email_reset_email(request, token):
    try:
        email = signing.loads(token)
    except signing.BadSignature:
        return HttpResponseBadRequest("不正なURLです。")
    form = RegistrationCodeForm
    email_reset_send_email(email)
    messages.success(request, "入力されたメールアドレスに送信しました。")
    context = {
        "form": form,
        "email": email,
        "token": token,
    }
    return render(request, "main/email_reset_confirmation.html", context)


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

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs["email"] = self.email
        return kwargs


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
        "email": email,
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


class VideoUploadView(LoginRequiredMixin, FormView):
    template_name = "main/video_upload.html"
    form_class = VideoUploadForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        video = form.save(commit=False)
        video.user = self.request.user
        video.save()
        return super().form_valid(form)
    
class SearchVideoView(LoginRequiredMixin, ListView):
    template_name = "main/video_search.html"
    model = Video
    context_object_name = "videos"

    def get(self, request, *args, **kwargs):
        self.form = VideoSearchForm(self.request.GET)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        if self.form.is_valid():
            context["keyword"] = self.form.cleaned_data["keyword"]
        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-uploaded_at")
        if self.form.is_valid():
            keyword = self.form.cleaned_data["keyword"]
            if keyword:
                queryset = queryset.filter(title__icontains=keyword)
        if "btnType" in self.request.GET:
            btn_type = self.request.GET.get("btnType")
            if btn_type == "new":
                queryset = queryset.order_by("-uploaded_at")[:5]
            else:
                queryset = queryset.order_by("-views_count")[:5]
        return queryset
    
class PlayVideoView(LoginRequiredMixin, DetailView):
    template_name = "main/video_play.html"
    model = Video

    def post(self, request, *args, **kwargs):
        views_count_form = ViewsCountForm(request.POST)
        if views_count_form.is_valid():
            views_count = views_count_form.cleaned_data["views_count"]
            video = Video.objects.filter(pk=kwargs["pk"])
            video.update(views_count=views_count)
        return redirect("video_play", kwargs["pk"])

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(pk=self.kwargs["pk"])
        return queryset
    

class AccountView(LoginRequiredMixin, DetailView):
    template_name = "main/account.html"
    model = User
    context_object_name = "user"

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.prefetch_related(
            Prefetch("videos", queryset=Video.objects.order_by("-uploaded_at"))
        ).annotate(
            follower_count=Count("followed", distinct=True),
            video_count=Count("videos", distinct=True),
        )
        if self.kwargs["pk"] != self.request.user.pk:
            follow_list = self.request.user.follow.all().values_list("id", flat=True)
            queryset = queryset.annotate(
                is_follow=Case(
                    When(id__in=follow_list, then=True),
                    default=False,
                )
            )
        return queryset
    
class FollowingView(LoginRequiredMixin, ListView):
    template_name = "main/following.html"
    context_object_name = "followings"

    def get_queryset(self):
        queryset = get_object_or_404(User, id=self.request.user.id).follow.all()
        return queryset
    
class FollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follow = User.objects.get(pk=kwargs["pk"])
        request.user.follow.add(follow)
        return redirect("account", kwargs["pk"])

class UnfollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follow = User.objects.get(pk=kwargs["pk"])
        request.user.follow.remove(follow)
        return redirect("account", kwargs["pk"])

class TermsView(LoginRequiredMixin, TemplateView):
    template_name = "main/terms.html"

class PrivacyPolicyView(LoginRequiredMixin, TemplateView):
    template_name = "main/privacy_policy.html"

class LogoutView(LogoutView):
    pass

class EmailResetView(LoginRequiredMixin, FormView):
    template_name = "main/email_reset.html"
    form_class = EmailForm

    def form_valid(self, form):
        new_email = form.cleaned_data["email"]
        self.token = signing.dumps(new_email)
        email_reset_send_email(new_email)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("email_reset_confirmation", kwargs={"token": self.token})
    

class EmailResetConfirmationView(LoginRequiredMixin, FormView):
    template_name = "main/email_reset_confirmation.html"
    form_class = RegistrationCodeForm

    def dispatch(self, request, *args, **kwargs):
        self.token = self.kwargs["token"]
        try:
            self.new_email = signing.loads(self.token)
        except signing.BadSignature:
            return HttpResponseBadRequest("不正なURLです。")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = User.objects.filter(id=self.request.user.id)
        user.update(email=self.new_email)
        return super().form_valid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs["email"] = self.new_email
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.new_email
        context["token"] = self.token
        return context

    def get_success_url(self):
        return reverse("account", kwargs={"pk": self.request.user.id})
    
class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "main/password_change.html"
    form_class = PasswordChangeForm

    def get_success_url(self):
        return reverse("account", kwargs={"pk": self.request.user.pk})
    
class AccountDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "main/account_delete.html"
    model = User
    object_context_name = "user"
    success_url = reverse_lazy("account_delete_done")

    def get_object(self):
        return self.request.user

class AccountDeleteDoneView(TemplateView):
    template_name = "main/account_delete_done.html"

class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = AccountUpdateForm
    template_name = "main/account_update.html"

    def get_success_url(self):
        return reverse_lazy("account", kwargs={"pk": self.request.user.pk})

    def get_object(self):
        return self.request.user