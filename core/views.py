from django.shortcuts import render
import json
import os





def profile(request):
    # Prefer logged-in Discord user; otherwise, try owner profile from stored token
    session_user = request.session.get("discord_user")

    owner_user = None
    owner_avatar_url = None
    owner_banner_url = None

    if not session_user:
        owner_user = _get_owner_profile()
        if owner_user:
            # Build CDN URLs
            avatar_hash = owner_user.get("avatar")
            uid = str(owner_user.get("id")) if owner_user.get("id") else None
            if uid and avatar_hash:
                ext = "gif" if str(avatar_hash).startswith("a_") else "png"
                owner_avatar_url = f"https://cdn.discordapp.com/avatars/{uid}/{avatar_hash}.{ext}?size=512"
            else:
                try:
                    idx = int(uid) % 5 if uid else 0
                except Exception:
                    idx = 0
                owner_avatar_url = f"https://cdn.discordapp.com/embed/avatars/{idx}.png"

            banner_hash = owner_user.get("banner")
            if uid and banner_hash:
                ext = "gif" if str(banner_hash).startswith("a_") else "png"
                owner_banner_url = f"https://cdn.discordapp.com/banners/{uid}/{banner_hash}.{ext}?size=1024"

    context = {
        "owner_user": owner_user,
        "owner_avatar_url": owner_avatar_url,
        "owner_banner_url": owner_banner_url,
        "session_user": session_user,
    }
    return render(request, "profile/home.html", context)


def api_test(request):
    import requests
    source = request.GET.get("source", "public")
    result = None
    status = None
    error = None

    try:
        if source == "discord":
            token = request.session.get("discord_access_token")
            if not token:
                raise RuntimeError("Not logged in with Discord. Please login first.")
            r = requests.get(
                "https://discord.com/api/users/@me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            status = r.status_code
            r.raise_for_status()
            result = r.json()
        else:
            # Public sample API: GitHub Django repo info
            r = requests.get("https://api.github.com/repos/django/django", timeout=10)
            status = r.status_code
            r.raise_for_status()
            result = r.json()
    except Exception as e:
        error = str(e)

    return render(
        request,
        "core/api_test.html",
        {
            "source": source,
            "status": status,
            "error": error,
            "json_text": json.dumps(result, ensure_ascii=False, indent=2) if result is not None else None,
        },
    )


def _get_owner_profile():
    """Fetch owner Discord profile using stored refresh/access token if available.
    Returns a user dict compatible with /users/@me or None.
    """
    from django.utils import timezone
    import datetime as _dt
    import requests
    from oauthapp.models import OwnerToken

    owner_id = os.getenv("DISCORD_OWNER_ID")
    if not owner_id:
        return None
    try:
        tok = OwnerToken.objects.filter(owner_id=str(owner_id)).first()
    except Exception:
        return None
    if not tok:
        return None

    access_token = tok.access_token
    # Refresh if no token or expired
    if not access_token or (tok.expires_at and tok.expires_at <= timezone.now()):
        data = {
            "client_id": os.getenv("DISCORD_CLIENT_ID", ""),
            "client_secret": os.getenv("DISCORD_CLIENT_SECRET", ""),
            "grant_type": "refresh_token",
            "refresh_token": tok.refresh_token,
        }
        try:
            res = requests.post("https://discord.com/api/oauth2/token", data=data, timeout=10)
            res.raise_for_status()
            tj = res.json()
            tok.access_token = tj.get("access_token")
            tok.refresh_token = tj.get("refresh_token", tok.refresh_token)
            expires_in = tj.get("expires_in") or 3600
            tok.expires_at = timezone.now() + _dt.timedelta(seconds=int(expires_in))
            tok.scope = tj.get("scope")
            tok.token_type = tj.get("token_type")
            tok.save(update_fields=["access_token", "refresh_token", "expires_at", "scope", "token_type", "updated_at"])
            access_token = tok.access_token
        except Exception:
            return tok.profile_json or None

    # Fetch profile
    try:
        me = requests.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        me.raise_for_status()
        user = me.json()
        tok.profile_json = user
        tok.save(update_fields=["profile_json", "updated_at"])
        return user
    except Exception:
        # Fallback to cached
        return tok.profile_json or None


