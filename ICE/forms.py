from django import forms
from .models import Module, Component, Question, User, Course

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=('emailID','firstName','lastName','userName','password')

class CourseForm(forms.ModelForm):
    class Meta:
        model=Course
        fields=('categoryID','courseName','courseCECU','courseDescription',)

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
        fields=('componentTitle','componentText','componentImage','orderNumber',)

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