from django.shortcuts import render
import json
import os
from datetime import datetime, timezone as _tz





def profile(request):
    # Prefer logged-in Discord user; otherwise, use stored owner profile
    session_user = request.session.get("discord_user")
    owner_user = None

    display_user = session_user
    if not display_user:
        owner_user = _get_owner_profile()
        display_user = owner_user

    display_avatar_url = _build_avatar_url(display_user) if display_user else None
    display_banner_url = _build_banner_url(display_user) if display_user else None
    # Precompute display name (avoid complex template filters showing literally)
    if display_user:
        display_name = display_user.get("global_name") or display_user.get("username") or "Your Name"
    else:
        display_name = "Your Name"

    # Presence via Server Widget (if configured)
    presence_status = None
    presence_elapsed_th = None
    widget_guild = os.getenv("DISCORD_WIDGET_GUILD_ID")
    # Prefer presence from bot (gateway) if available
    if display_user and display_user.get("id"):
        info = _get_presence_info_via_bot(str(display_user.get("id")))
        if info:
            presence_status = info.get("status")
            ts = info.get("ts")
            if presence_status == "offline" and ts:
                now = datetime.now(_tz.utc)
                delta = max(0, int((now - ts).total_seconds()))
                presence_elapsed_th = _format_duration_th(delta)
        if not presence_status and widget_guild:
            presence_status = _get_presence_via_widget(widget_guild, str(display_user.get("id")))

    about_me = os.getenv("DISCORD_OWNER_ABOUT")

    context = {
        "session_user": session_user,
        "owner_user": owner_user,
        "display_user": display_user,
        "display_avatar_url": display_avatar_url,
        "display_banner_url": display_banner_url,
        "display_name": display_name,
        "presence_status": presence_status,
        "presence_elapsed_th": presence_elapsed_th,
        "about_me": about_me,
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
            import requests  # local import; may be missing during dev
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
        import requests  # local import; may be missing during dev
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


def _build_avatar_url(user):
    if not user:
        return None
    uid = str(user.get("id")) if user.get("id") else None
    avatar = user.get("avatar")
    if uid and avatar:
        ext = "gif" if str(avatar).startswith("a_") else "png"
        return f"https://cdn.discordapp.com/avatars/{uid}/{avatar}.{ext}?size=512"
    try:
        idx = int(uid) % 5 if uid else 0
    except Exception:
        idx = 0
    return f"https://cdn.discordapp.com/embed/avatars/{idx}.png"


def _build_banner_url(user):
    if not user:
        return None
    uid = str(user.get("id")) if user.get("id") else None
    banner = user.get("banner")
    if uid and banner:
        ext = "gif" if str(banner).startswith("a_") else "png"
        return f"https://cdn.discordapp.com/banners/{uid}/{banner}.{ext}?size=1024"
    return None


def _get_presence_via_widget(guild_id, user_id):
    """Fetch presence via Discord Server Widget JSON. Requires widget enabled in server settings.
    Returns one of: online, idle, dnd, offline (or None if not found).
    """
    import requests
    try:
        url = f"https://discord.com/api/guilds/{guild_id}/widget.json"
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return None
        data = r.json()
        for m in data.get("members", []):
            if str(m.get("id")) == str(user_id):
                return m.get("status")
        return None
    except Exception:
        return None


def _get_presence_via_bot(user_id):
    """Read presence from shared file written by bot service."""
    path = os.getenv("DISCORD_PRESENCE_FILE", "runtime/presence.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if str(data.get("user_id")) == str(user_id):
            return data.get("status")
        return None
    except Exception:
        return None


def _get_presence_info_via_bot(user_id):
    """Return dict {status, ts(datetime)} from bot presence file if matches user_id."""
    path = os.getenv("DISCORD_PRESENCE_FILE", "runtime/presence.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if str(data.get("user_id")) != str(user_id):
            return None
        status = data.get("status")
        ts_raw = data.get("ts")
        ts = None
        if ts_raw:
            try:
                ts = datetime.fromisoformat(ts_raw)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=_tz.utc)
            except Exception:
                ts = None
        return {"status": status, "ts": ts}
    except Exception:
        return None


def _format_duration_th(seconds: int) -> str:
    """Format seconds into English: '2 days 3 hours', '5 minutes'."""
    mins = seconds // 60
    hrs = mins // 60
    days = hrs // 24
    mins = mins % 60
    hrs = hrs % 24
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hrs > 0:
        parts.append(f"{hrs} hour{'s' if hrs != 1 else ''}")
    if days == 0 and mins > 0:
        parts.append(f"{mins} minute{'s' if mins != 1 else ''}")
    if not parts:
        return "a few seconds"
    return " ".join(parts)


