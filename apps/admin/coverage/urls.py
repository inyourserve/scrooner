from django.urls import path

from .views import dashboard

app_name = "coverage"
urlpatterns = [path("", dashboard, name="dashboard")]
