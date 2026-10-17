from django.urls import path

from .views import overview

app_name = "cockpit"
urlpatterns = [path("", overview, name="overview")]
