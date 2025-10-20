from django.shortcuts import render





def profile(request):
    return render(request, "profile/home.html")


