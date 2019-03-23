from django import forms
from .models import Module

class ModuleForm(forms.ModelForm):
    class Meta:
        model=Module
        fields=('moduleTitle','courseID','orderNumber','numOfComponents',)

class QuizForm(forms.ModelForm):
    class Meta:
        model=Module
        fields=('numOfQuestions','passingMark',)
