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
    CHOICES.append(('1', Q[0].qOption1))
    CHOICES.append(('2', Q[0].qOption2))
    CHOICES.append(('3', Q[0].qOption3))
    CHOICES.append(('4', Q[0].qOption4))
    choices = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())
    correct=Q[0].answer

