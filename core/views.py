from django.shortcuts import render
import json
import os
import requests





def profile(request):
    return render(request, "profile/home.html")


def api_test(request):
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


