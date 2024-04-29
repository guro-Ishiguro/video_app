from django.contrib import admin

from .models import AuthenticationCode, User

admin.site.register(AuthenticationCode)
admin.site.register(User)
