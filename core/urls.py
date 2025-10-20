from django.urls import path
from .views import profile, api_test

urlpatterns = [
    path("", profile, name="profile"),
    path("profile/", profile, name="profile"),
    path("api-test/", api_test, name="api_test"),
]
