from django import forms
from .models import Module, Component, Question, User, Course
from django.forms import modelformset_factory
from django.forms.widgets import RadioSelect

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

class QuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        choices = [x for x in question.get_options()]
        self.fields["answers"] = forms.ChoiceField(choices=choices,widget=RadioSelect)