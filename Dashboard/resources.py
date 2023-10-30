from import_export import resources
from MainApp.models import Book

class BookResource(resources.ModelResource):
    class meta:
        model = Book