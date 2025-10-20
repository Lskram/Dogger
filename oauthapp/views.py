import os
from urllib.parse import urlencode

import requests
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import redirect


DISCORD_AUTH_BASE = "https://discord.com/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_ME_URL = "https://discord.com/api/users/@me"


def discord_login(request):
    client_id = os.getenv("DISCORD_CLIENT_ID", "")
    redirect_uri = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8000/auth/discord/callback/")
    scope = os.getenv("DISCORD_SCOPE", "identify")
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
        "prompt": "consent",
    }
    return HttpResponseRedirect(f"{DISCORD_AUTH_BASE}?{urlencode(params)}")


def discord_callback(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Missing code", status=400)

    data = {
        "client_id": os.getenv("DISCORD_CLIENT_ID", ""),
        "client_secret": os.getenv("DISCORD_CLIENT_SECRET", ""),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8000/auth/discord/callback/"),
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        token_res = requests.post(DISCORD_TOKEN_URL, data=data, headers=headers, timeout=10)
        token_res.raise_for_status()
    except Exception as e:
        return HttpResponse(f"Token exchange failed: {e}", status=500)

    token_json = token_res.json()
    access_token = token_json.get("access_token")
    if not access_token:
        return JsonResponse(token_json, status=500)

    try:
        me_res = requests.get(DISCORD_ME_URL, headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
        me_res.raise_for_status()
    except Exception as e:
        return HttpResponse(f"Fetch user failed: {e}", status=500)

    request.session["discord_user"] = me_res.json()
    request.session["discord_access_token"] = access_token
    return redirect("profile")


def discord_me(request):
    data = request.session.get("discord_user")
    if not data:
        return JsonResponse({"detail": "no user"}, status=404)
    return JsonResponse(data)


def discord_logout(request):
    request.session.pop("discord_user", None)
    return redirect("profile")


def _discord_cdn_avatar(user):
    try:
        uid = str(user.get("id"))
    except Exception:
        return None
    avatar = user.get("avatar")
    if avatar:
        ext = "gif" if str(avatar).startswith("a_") else "png"
        return f"https://cdn.discordapp.com/avatars/{uid}/{avatar}.{ext}?size=512"
    # Fallback default avatar (approximation using id % 5)
    try:
        idx = int(uid) % 5
    except Exception:
        idx = 0
    return f"https://cdn.discordapp.com/embed/avatars/{idx}.png"


def _discord_cdn_banner(user):
    try:
        uid = str(user.get("id"))
    except Exception:
        return None
    banner = user.get("banner")
    if not banner:
        return None
    ext = "gif" if str(banner).startswith("a_") else "png"
    return f"https://cdn.discordapp.com/banners/{uid}/{banner}.{ext}?size=1024"


def discord_profile(request):
    user = request.session.get("discord_user")
    if not user:
        return HttpResponseRedirect("/auth/discord/login/")

    context = {
        "username": user.get("global_name") or user.get("username"),
        "id": user.get("id"),
        "avatar_url": _discord_cdn_avatar(user),
        "banner_url": _discord_cdn_banner(user),
        # Presence/status and "about me" are not available via public OAuth REST
        "presence_note": "Discord ไม่เปิดให้ดึงสถานะออนไลน์ผ่าน OAuth REST ต้องใช้ Bot + Gateway (Privileged Intent)",
        "about_note": "About me (bio) ไม่มีใน REST มาตรฐานผ่าน OAuth",
        "raw": user,
    }
    from django.shortcuts import render

    return render(request, "oauthapp/discord_profile.html", context)
