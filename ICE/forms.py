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

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields['courseName'].widget.attrs['placeholder'] = 'Course Title'
        self.fields['courseCECU'].widget.attrs['placeholder'] = 'CECU Value'
        # not showing placeholder cecu as positive integer field instead of integer field
        self.fields['courseDescription'].widget.attrs['placeholder'] = 'Course Description'

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

    def __init__(self, *args, **kwargs):
        super(ComponentForm, self).__init__(*args, **kwargs)
        self.fields['componentTitle'].widget.attrs['placeholder'] = 'Component Title'
        self.fields['componentText'].widget.attrs['placeholder'] = 'Component Text Content'
        # self.fields['componentImage'].widget.attrs['placeholder'] = 'No Image chosen'
        self.fields['orderNumber'].widget.attrs['placeholder'] = 'Component#'

# class SomeForm(forms.Form):
#     Q = Question.objects.filter(moduleID=1)
#     CHOICES=[]
#     for q in Q:
#         CHOICES.append(('1', q.qOption1))
#         CHOICES.append(('2', q.qOption2))
#         CHOICES.append(('3', q.qOption3))
#         CHOICES.append(('4', q.qOption4))
#         choices = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())
#         correct=q.answer
#         CHOICES = []