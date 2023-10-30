from django.db import models
from django.contrib.auth.models import User
from froala_editor.fields import FroalaField
from django.utils.text import slugify


# Create your models here.
class Gallery(models.Model):
    image = models.ImageField(upload_to="gallery/")
    caption = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class Category(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS = ((0, "AVAILABLE"), (1, "LENT"))

    book_id = models.CharField(max_length=10, null=False, blank=False)
    title = models.CharField(max_length=50, null=False, blank=False)
    author = models.CharField(max_length=50, null=True, blank=True)
    language = models.CharField(max_length=20, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.CharField(max_length=10, null=True)
    publisher = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return self.title


class History(models.Model):
    by = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class Message(models.Model):
    STATUS = (
        (0, "UnRead"),
        (1, "Read"),
    )
    name_sender = models.CharField(max_length=255)
    email_sender = models.EmailField(null=True, blank=True)
    message = models.TextField()
    status = models.IntegerField(choices=STATUS, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class SiteSettings(models.Model):
    site_logo = models.ImageField(upload_to="logo/")
    welcome_text = models.TextField()
    address = models.CharField(max_length=255)
    email = models.EmailField(default="")
    phone = models.CharField(max_length=20, default="0")
    footer_text = models.TextField()
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_edited"]


class AboutComponents(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_edited"]


class OurPartner(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="partners/")
    facebook_page = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_edited"]


class OurGallery(models.Model):
    image = models.ImageField(upload_to="gallery/")
    caption = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class ReaderProfile(models.Model):
    SEX = (
        (0, "MALE"),
        (1, "FEMALE"),
    )
    reader_id = models.CharField(max_length=255, default="0")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    sex = models.IntegerField(choices=SEX)
    age = models.IntegerField()
    proffession = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class LendBook(models.Model):
    STATUS = (
        (0, "NOT RETURNED"),
        (1, "RETURNED"),
    )

    reader = models.ForeignKey(ReaderProfile, on_delete=models.RESTRICT)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    return_date = models.DateField()
    status = models.IntegerField(choices=STATUS, default=0)
    last_edited = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class NewsAndEvents(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="news/", null=True, blank=True)
    content = FroalaField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(NewsAndEvents, self).save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
