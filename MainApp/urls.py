from django.urls import path
from .views import *

urlpatterns = [
    path(
        "",
        Home.as_view(),
    ),
    path("gallery/", Gallery.as_view()),
    path("our-books/", ourBooks),
    path("news/", News),
    path("news/<slug:slug>", NewsDetail),
    path("support", HelpUs),
    path("login/", Login.as_view()),
    path("logout/", Logout),
]
