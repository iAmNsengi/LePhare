from django.urls import path
from .views import *

urlpatterns = [
    path("", Dashboard.as_view()),
    path("books/", Books.as_view()),
    path("books/<int:id>/delete", deleteBook),
    path("books/<int:id>/edit", editBook),
    path("books/upload", uploadBooksFile),
    path("books/lend", LendBooks.as_view()),
    path("books/return", returnBook),
    path("books/add-category", addBookCategory),
    path("settings/", Settings.as_view()),
    path("settings/delete-partner/<int:id>", deletePartner),
    path("settings/add-partner/", addPartner),
    path("news/", News.as_view()),
    path("news/<slug:slug>", DashboardNewsDetail),
    path("news/<slug:slug>/delete", DeleteNews),
    path("users/", Users.as_view()),
    path("users/<int:id>/delete", deleteUser),
    path("users/<int:id>/edit", editUser),
    path("history", history),
]
