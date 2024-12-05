from django.urls import path
from .views import IndexView, AllListingsView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("all/", AllListingsView.as_view(), name="all_listings"),
]
