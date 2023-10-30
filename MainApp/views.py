from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import *
from datetime import date
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.
class Home(View):
    def get(self, request):
        settings = SiteSettings.objects.first()
        partners = OurPartner.objects.all()
        context = {
            "settings": settings,
            "partners": partners,
        }
        return render(request, "index.html", context)

    def post(self, request):
        if request.method == "POST":
            name = request.POST.get("name")
            email = request.POST.get("email")
            message = request.POST.get("message")

            try:
                send_mail(
                    subject="Message | Le Phare",
                    message=f"Hello Admin \n{name}You have  new message from {name};\n\n\n{message} \n\n\n-------------------------------\nLe Phare,",
                    from_email=email,
                    recipient_list=[
                        settings.EMAIL_HOST_USER,
                        "nsengitech@gmail.com",
                        "bibliothequelephare@gmail.com",
                    ],
                    fail_silently=False,
                )
            except:
                messages.error(
                    request, "A connection error occurred while sending message retry!."
                )
                return redirect("/")


class Gallery(View):
    def get(self, request):
        images = OurGallery.objects.all()
        context={
            'images':images
        }
        return render(request, "gallery.html",context)

    def post(self, request):
        if request.method == "POST":
            caption = request.POST.get("caption")
            image = request.FILES.get("image")

            try:
                OurGallery.objects.create(caption=caption, image=image)
                messages.success(request, "Image Added Successfully!")
                return redirect("/gallery")
            except Exception as e:
                messages.error(request, e)
                return redirect("gallery")


def News(request):
    news = NewsAndEvents.objects.all()
    context = {
        "news": news,
    }
    return render(request, "news.html", context)


def NewsDetail(request, slug):
    try:
        news = NewsAndEvents.objects.get(slug=slug)
        context = {
            "news": news,
        }
    except Exception as e:
        messages.error(request, e)
        return redirect("/news")
    return render(request, "news-detail.html", context)


def ourBooks(request):
    books = Book.objects.all()
    context = {
        "books": books,
    }
    return render(request, "books/our_books.html", context)


def HelpUs(request):
    if request.method == "POST":
        message = request.POST.get("message")
        help_title = request.POST.get("help_title")
        email = request.POST.get("email")
        name = request.POST.get("name")
        phone = request.POST.get("phone")

        try:
            send_mail(
                subject="Message | Le Phare",
                message=f"Hello Admin \n{name} Wants to support our library for {help_title}, ({phone})\nThis is the message:\n\n\n{message} \n\n\n-------------------------------\nLe Phare AI Bot",
                from_email=email,
                recipient_list=[
                    settings.EMAIL_HOST_USER,
                    "nsengitech@gmail.com",
                    "bibliothequelephare@gmail.com",
                ],
                fail_silently=False,
            )
            send_mail(
                subject="Message | Le Phare",
                message=f"Hello {name} for contacting us! \nWe will get back to you in short thank you!\n\n-------------------------------\nLe Phare AI Bot\n",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[
                    email,
                ],
                fail_silently=False,
            )
        except:
            messages.error(
                request, "A connection error occurred while sending message retry!."
            )
            return redirect("/")
        messages.success(request, "Message Sent Successfully!")
        return redirect("/")
    return redirect("/")


class Login(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, "User not found!")
            return redirect("/login")


def Logout(request):
    logout(request)
    return redirect("/login")
