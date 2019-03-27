from django import forms
from .models import Module, Component, Question

class ModuleForm(forms.ModelForm):
    class Meta:
        model=Module
        fields=('moduleTitle', 'orderNumber','numOfComponents',)

class QuizForm(forms.ModelForm):
    class Meta:
        model=Module
        fields=('numOfQuestions','passingMark',)

class ComponentForm(forms.ModelForm):
    class Meta:
        model=Component
        fields=('componentID','moduleID','componentTitle','componentText','componentImage','orderNumber',)

class SomeForm(forms.Form):
    Q = Question.objects.filter(moduleID=1)
    CHOICES=[]
    for q in Q:
        CHOICES.append(('1', q.qOption1))
        CHOICES.append(('2', q.qOption2))
        CHOICES.append(('3', q.qOption3))
        CHOICES.append(('4', q.qOption4))
        choices = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())
        correct=q.answer
        CHOICES = []

