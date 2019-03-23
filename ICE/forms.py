from django import forms
from .models import Module
class ContactForm(forms.Form):
    title=forms.CharField()
    courseID=forms.IntegerField()
    orderNumber=forms.IntegerField()
    numOfComponents=forms.IntegerField()

class ModuleForm(forms.ModelForm):
    class Meta:
        model=Module
        fields=('moduleTitle','courseID','orderNumber','numOfComponents',)