from django.shortcuts import render, redirect
from django.views import View
from MainApp.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import NewsForm

from openpyxl import load_workbook
from tablib import Dataset
from .resources import BookResource


# Create your views here.
class Dashboard(View):
    def get(self, request):
        categories = Category.objects.all()
        books = Book.objects.all()
        history = History.objects.all()[:6]
        news = NewsAndEvents.objects.all()[:4]
        users = ReaderProfile.objects.all()
        lent_books = LendBook.objects.filter(status=0).count()

        if not request.user.is_authenticated:
            return redirect("/login")
        context = {
            "categories": categories,
            "books": books,
            "history": history,
            "news": news,
            "users": users,
            "lent_books": lent_books,
        }
        return render(request, "dashboard/index.html", context)


class Settings(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/")
        settings = SiteSettings.objects.first()
        partners = OurPartner.objects.all()

        context = {
            "settings": settings,
            "partners": partners,
        }
        return render(request, "dashboard/sitesettings.html", context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("/")

        if request.method == "POST":
            logo = request.FILES.get("logo") or None
            welcome_text = request.POST.get("welcome_text") or None
            address = request.POST.get("address") or None
            email = request.POST.get("email") or None
            phone = request.POST.get("phone") or None
            footer_text = request.POST.get("footer_text") or None

            user = User.objects.get(username=request.user)
            settings = SiteSettings.objects.first()
            history = History(by=user, action="Updated site Settings")
            try:
                if logo is not None:
                    settings.site_logo = logo
                if welcome_text is not None:
                    settings.welcome_text = welcome_text
                if address is not None:
                    settings.address = address
                if phone is not None:
                    settings.phone = phone
                if email is not None:
                    settings.email = email
                if footer_text is not None:
                    settings.footer_text = footer_text
                settings.save()
                history.save()
                messages.success(request, "Settings Updated Successfully!")
                return redirect("/dashboard/settings/")
            except Exception as e:
                messages.error(request, e)
                return redirect("/dashboard/settings/")


@login_required(login_url="/login")
def addPartner(request):
    if request.method == "POST":
        name = request.POST.get("name")
        logo = request.FILES.get("logo")
        facebook_page = request.POST.get("facebook_page")
        website = request.POST.get("website")

        try:
            user = User.objects.get(username=request.user)
            new_partner = OurPartner(
                name=name, logo=logo, facebook_page=facebook_page, website=website
            )
            history = History(by=user, action="Added a new Partner")
            new_partner.save()
            history.save()
            messages.success(request, "Partner Added Successfully!")
            return redirect("/dashboard/settings/")
        except Exception as e:
            messages.errir(request, e)
            return redirect("/dashboard/settings")


@login_required(login_url="/login")
def deletePartner(request, id):
    try:
        user = User.objects.get(username=request.user)
        partner = OurPartner.objects.get(id=id)
        partner.delete()
        history = History(by=user, action="Deleted A Partner !")
        history.save()
        messages.success(request, "Partner Deleted Successfully!")
        return redirect("/dashboard/settings/")
    except Exception as e:
        messages.error(request, e)
        return redirect("/dashboard/settings")


class News(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "You need to be logged in to view that page!")
            return redirect("/login")

        form = NewsForm()
        news = NewsAndEvents.objects.all()
        history = History.objects.all()[:6]

        context = {
            "news": news,
            "history": history,
            "form": form,
        }
        return render(request, "./dashboard/news.html", context)

    def post(self, request):
        if request.method == "POST":
            title = request.POST.get("title")
            image = request.FILES.get("image")
            content = request.POST.get("content")
            print(content)

            try:
                user = User.objects.get(username=request.user)
                news_obj = NewsAndEvents(title=title, image=image, content=content)
                history_obj = History(by=user, action="Added a News")
                news_obj.save()
                history_obj.save()
                messages.success(request, "A new information was added successfully!")
                return redirect("/dashboard/news")
            except Exception as e:
                messages.error(request, e)
                return redirect("/dashboard/news")


@login_required(login_url="/login")
def DashboardNewsDetail(request, slug):
    news_object = NewsAndEvents.objects.get(slug=slug)

    context = {
        "news": news_object,
    }
    return render(request, "dashboard/news-detail.html", context)


@login_required(login_url="/login")
def DeleteNews(request, slug):
    try:
        user = User.objects.get(username=request.user)
        news_object = NewsAndEvents.objects.get(slug=slug)
        history = History(by=user, action="Deleted Post")
        news_object.delete()
        history.save()
        messages.success(request, "Post deleted Successfully")
        return redirect("/dashboard/news")
    except Exception as e:
        messages.error(request, e)
        return redirect("/dashboard/news")


class Users(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "You have to be logged in to view this page!")
            return redirect("/login")

        users = ReaderProfile.objects.all()
        context = {
            "users": users,
        }

        return render(request, "dashboard/users.html", context)

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "You have to be logged in to view this page!")
            return redirect("/login")

        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        sex = request.POST.get("sex")
        age = request.POST.get("age")
        proffession = request.POST.get("proffession")
        address = request.POST.get("address")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        try:
            user_exist = ReaderProfile.objects.filter(
                first_name=fname, last_name=lname, phone=phone
            ).first()
            email_exist = ReaderProfile.objects.filter(email=email).first()

            if user_exist is not None or email_exist is not None:
                messages.error(request, "User already exist!")
                return redirect("/dashboard/users")

            new_user = ReaderProfile(
                first_name=fname,
                last_name=lname,
                sex=sex,
                age=age,
                proffession=proffession,
                address=address,
                email=email,
                phone=phone,
            )
            user = User.objects.get(username=request.user)
            history = History(by=user, action="Create A Reader Profile")
            new_user.save()
            history.save()
            try:
                the_user = ReaderProfile.objects.get(
                    first_name=fname,
                    last_name=lname,
                    sex=sex,
                    age=age,
                    proffession=proffession,
                    address=address,
                    email=email,
                    phone=phone,
                )
                the_user.reader_id = f"LPHR-{the_user.id}"
                the_user.save()
            except:
                messages.error(request, "Couldn't set the reader ID")
                return redirect("/dashboard/users")
            messages.success(request, "A Reader Profile Was Created Successfully!")
            return redirect("/dashboard/users")

        except Exception as e:
            messages.error(request, e)
            return redirect("/dashboard/users")


@login_required(login_url="/login")
def deleteUser(request, id):
    user = User.objects.get(username=request.user)
    try:
        user_obj = ReaderProfile.objects.get(id=id)
        history = History(by=user, action="Deleted a Reader Profile")
        user_obj.delete()
        history.save()
        messages.success(request, "User Deleted Successfully!")
        return redirect("/dashboard/users")

    except Exception as e:
        messages.error(request, e)
        return redirect("/dashboard/users")


@login_required(login_url="/login")
def editUser(request, id):
    user = User.objects.get(username=request.user)
    try:
        user_obj = ReaderProfile.objects.get(id=id)
        history = History(by=user, action="Edited a Reader Profile")

        if request.method == "POST":
            fname = request.POST.get("fname") or None
            lname = request.POST.get("lname") or None
            sex = request.POST.get("sex") or None
            age = request.POST.get("age") or None
            proffession = request.POST.get("proffession") or None
            address = request.POST.get("address") or None
            email = request.POST.get("email") or None
            phone = request.POST.get("phone") or None

            if fname is not None:
                user_obj.fname = fname
            if lname is not None:
                user_obj.lname = lname
            if sex is not None:
                user_obj.sex = sex
            if age is not None:
                user_obj.age = age
            if proffession is not None:
                user_obj.proffession = proffession
            if address is not None:
                user_obj.address = address
            if email is not None:
                user_obj.email = email
            if phone is not None:
                user_obj.phone = phone

            user_obj.save()
            history.save()
            messages.success(request, "User Profile Edited Successfully!")
            return redirect("/dashboard/users")

    except Exception as e:
        messages.error(request, e)
        return redirect("/dashboard/users")


@login_required(login_url="/login")
def history(request):
    history = History.objects.all()
    context = {
        "history": history,
    }
    return render(request, "dashboard/history.html", context)


class Books(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "You have to be logged in to view this page!")
            return redirect("/login")

        books = Book.objects.all()
        categories = Category.objects.all()
        context = {
            "books": books,
            "categories": categories,
        }

        return render(request, "dashboard/books.html", context)

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "You have to be logged in to view this page!")
            return redirect("/login")

        book_id = request.POST.get("book_id")
        title = request.POST.get("title")
        author = request.POST.get("author")
        language = request.POST.get("language")
        category = request.POST.get("category")
        price = request.POST.get("price")
        publisher = request.POST.get("publisher")

        try:
            category = Category.objects.get(id=category)
            book_exist = Book.objects.filter(book_id=book_id).first()

            if book_exist is not None:
                messages.error(request, "Book already exist!")
                return redirect("/dashboard/books")

            new_book = Book(
                book_id=book_id,
                title=title,
                author=author,
                language=language,
                category=category,
                price=price,
                publisher=publisher,
            )
            user = User.objects.get(username=request.user)
            history = History(by=user, action="Registered a new book!")
            new_book.save()
            history.save()
            messages.success(request, "Book Was Registered Successfully!")
            return redirect("/dashboard/books")

        except Exception as e:
            messages.error(request, e)
            return redirect("/dashboard/books")


@login_required(login_url="/login")
def deleteBook(request, id):
    user = User.objects.get(username=request.user)
    try:
        book_obj = Book.objects.get(id=id)
        if book_obj.status == 1:
            messages.error(request, "You can't remove a book that was lent")
            return redirect("/dashboard/books")
        history = History(by=user, action="Deleted a book")
        book_obj.delete()
        history.save()
        messages.success(request, "Book Deleted Successfully!")
        return redirect("/dashboard/books")

    except Exception as e:
        messages.error(request, e)
        return redirect("/dashboard/books")


@login_required(login_url="/login")
def editBook(request, id):
    user = User.objects.get(username=request.user)
    try:
        book_obj = Book.objects.get(id=id)
        history = History(by=user, action="Edited a Book Information")

        if request.method == "POST":
            book_id = request.POST.get("book_id") or None
            title = request.POST.get("title") or None
            author = request.POST.get("author") or None
            language = request.POST.get("language") or None
            category = request.POST.get("category") or None
            price = request.POST.get("price") or None
            publisher = request.POST.get("publisher") or None

            if book_id is not None:
                book_obj.book_id = book_id
            if title is not None:
                book_obj.title = title
            if author is not None:
                book_obj.author = author
            if language is not None:
                book_obj.language = language
            if category is not None:
                category = Category.objects.get(id=category)
                book_obj.category = category
            if price is not None:
                book_obj.price = price
            if publisher is not None:
                book_obj.publisher = publisher

            book_obj.save()
            history.save()
            messages.success(request, "Book Information Edited Successfully!")
            return redirect("/dashboard/books")

    except Exception as e:
        messages.error(request, e)
        return redirect("/dashboard/books")


@login_required(login_url="/login")
def uploadBooksFile(request):
    if request.method == "POST":
        file_sheet = request.FILES["file_sheet"]
        try:
            user = User.objects.get(username=request.user)
            dataset = Dataset()
            imported_data = dataset.load(file_sheet.read(), format="xlsx")
            counter = 0

            for data in imported_data:
                try:
                    category = Category.objects.filter(name=data[2]).first()

                    if data[2] is None:
                        category = Category.objects.filter(name = 'UNCATEGORIZED').first()
                   
                    if category is None:
                        Category.objects.create(name = data[2])
                        category = Category.objects.filter(name=data[2]).first()


                    data_exist = Book.objects.filter(book_id=data[0]).first()
                    if data_exist is None:
                        Book.objects.create(
                            book_id=data[0],
                            title=data[1],
                            author=data[4],
                            language=data[5],
                            category=category,
                            price=data[7],
                            publisher=data[3],
                        )
                        counter += 1
                except Exception as e:
                    messages.error(request, f'{e}')
                    return redirect("/dashboard/books")
            if counter > 0:
                History.objects.create(by=user, action=f"Added {counter} books!")
            messages.success(request, f"{counter} data was registered successfully!")
            return redirect("/dashboard/books")
        except Exception as e:
            messages.error(request, e)
            return redirect("/dashboard/books")


@login_required(login_url="/login")
def addBookCategory(request):
    if request.method == "POST":
        name = request.POST.get("name")
        category_exist = Category.objects.filter(name=name).first()
        if category_exist is None:
            user = User.objects.get(username=request.user)
            Category.objects.create(name=name)
            History.objects.create(by=user, action="Added A Category!")
            messages.success(request, "Book Category Added Successfully!")
            return redirect("/dashboard/books")
        else:
            messages.error(request, "Category Already Exists!")
            return redirect("/dashboard/books")


class LendBooks(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "You have to be logged in to access this page!")
            return redirect("/login")

        books = Book.objects.all()
        accounts = ReaderProfile.objects.all()
        lent_books = LendBook.objects.all()

        context = {
            "books": books,
            "accounts": accounts,
            "lentbooks": lent_books,
        }
        return render(request, "dashboard/lend-book.html", context)

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "You have to be logged in to access this page")
            return redirect("/login")
        if request.method == "POST":
            reader_id = request.POST.get("reader_id")
            book_id = request.POST.get("book_id")
            return_date = request.POST.get("return_date")

            try:
                reader = ReaderProfile.objects.get(reader_id=reader_id)

                book = Book.objects.get(book_id=book_id)
                user_has_book = LendBook.objects.filter(reader=reader, status=0).first()

                if user_has_book is None:
                    if book.status == 0:
                        LendBook.objects.create(
                            reader=reader, book=book, return_date=return_date
                        )
                        book.status = 1
                        book.save()
                        user = User.objects.get(username=request.user)
                        History.objects.create(by=user, action="Lent A Book")
                        messages.success(request, "Book lending recorded sucessfully!")
                        return redirect("/dashboard/books/lend")
                    else:
                        messages.error(request, "Book is not available!")
                        return redirect("/dashboard/books/lend")
                else:
                    messages.error(request, "Reader Has Another book not yet returned!")
                    return redirect("/dashboard/books/lend")
            except Exception as e:
                messages.error(request, e)
                return redirect("/dashboard/books/lend")


@login_required
def returnBook(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")

        try:
            book = Book.objects.get(book_id=book_id)
            lend_object = LendBook.objects.get(book=book, status=0)
            user = User.objects.get(username=request.user)
            if book.status == 1:
                book.status = 0
                lend_object.status = 1
                book.save()
                lend_object.save()
                History.objects.create(by=user, action="User returned a book!")
                messages.success(
                    request,
                    f"Book: {book.title} , lent by {lend_object.reader.first_name} {lend_object.reader.last_name} was returned successfully! ",
                )
                return redirect("/dashboard/books/lend")
            else:
                messages.error(request, "Book is in the Library already !")
                return redirect("/dashboard/books/lend")
        except Exception as e:
            messages.error(request, e)
            return redirect("/dashboard/books/lend")
