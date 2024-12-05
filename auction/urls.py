from django.urls import path
from . import views
from .views import IndexView, AllListingsView

app_name = "auction"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("all/", AllListingsView.as_view(), name="all_listings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createListing", views.createlisting, name="createListing"),
    path("details/<int:id>", views.details, name="details"),
    path("categories", views.categories, name="categories"),
    path("filter/<str:name>", views.filter_by_category, name="filter"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("bid/<int:id>", views.place_bid, name="bid"),
    path("end/<int:item_id>", views.auction_ending, name="end"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watch", views.watch, name="watch")
]
