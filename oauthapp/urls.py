from django.urls import path
from .views import discord_login, discord_callback, discord_me

urlpatterns = [
    path("discord/login/", discord_login, name="discord_login"),
    path("discord/callback/", discord_callback, name="discord_callback"),
    path("discord/me/", discord_me, name="discord_me"),
]

