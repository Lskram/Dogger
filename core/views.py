from django.shortcuts import render


def home(request):
    return render(request, "core/index.html")


def about(request):
    return render(request, "core/about.html")


def contact(request):
    return render(request, "core/contact.html")


def profile(request):
    return render(request, "templest profile/home.html")
