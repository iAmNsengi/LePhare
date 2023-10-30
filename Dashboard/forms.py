from django import forms
from MainApp.models import NewsAndEvents
from froala_editor.widgets import FroalaEditor


class NewsForm(forms.ModelForm):
    content = forms.CharField(widget=FroalaEditor)

    class Meta:
        model = NewsAndEvents
        fields = ("content",)
