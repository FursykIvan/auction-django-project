from django.urls import include, path

from accounts.views import UserDetailView, activate, register

app_name = "accounts"

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register/", register, name="register"),
    path("activate/<str:uid>/<str:token>/", activate, name="activate"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
