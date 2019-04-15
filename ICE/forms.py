from django import forms

from django.forms import modelformset_factory
from django.forms.widgets import RadioSelect


from .models import Module, Component, Question, User, Instructor, Learner, Course, Quiz
from django.contrib.auth.forms import UserCreationForm

class InviteForm(forms.Form):
    emailID = forms.EmailField(max_length=200, help_text='Required')
    def clean_email(self):
        # Get the email
        emailID = self.cleaned_data.get('emailID')
        # Check to see if there's any user with the same email.
        try:
            match = User.objects.get(emailID=emailID)
        except User.DoesNotExist:
            # no duplicates 
            return emailID
        # duplicate exists - raise an error.
        raise forms.ValidationError('This email address is already in use.')

class SignupFormInstructor(forms.ModelForm):
    firstName = forms.CharField(max_length=30, required=True)
    lastName = forms.CharField(max_length=30, required=True)
    biography = forms.CharField(max_length=250, required=True)
    userName = forms.CharField(max_length=30, required=True)
    password = forms.CharField(max_length=50, required = True)
    class Meta:
        model = Instructor
        fields = ('userName', 'firstName', 'lastName', 'biography', 'password')


class SignupFormLearner(forms.ModelForm):
    userName = forms.CharField(max_length=30, required=True)
    password = forms.CharField(max_length=50, required = True)
    class Meta:
        model = Learner
        fields = ('userName', 'password')

class LearnerGetTokenForm(forms.Form):
    staffID = forms.IntegerField(max_value=9999)

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
        # not showing placeholder cecu as integer field with blank = true not done
        self.fields['courseDescription'].widget.attrs['placeholder'] = 'Course Description'

class ModuleForm(forms.ModelForm):
    class Meta:
        model=Module
        fields=('moduleTitle', 'orderNumber',)

    def __init__(self, *args, **kwargs):
        super(ModuleForm, self).__init__(*args, **kwargs)
        self.fields['moduleTitle'].widget.attrs['placeholder'] = 'Module Title'
        self.fields['orderNumber'].widget.attrs['placeholder'] = 'Module#'
        # self.fields['numOfComponents'].widget.attrs['placeholder'] = 'No. of Components'
        # not showing placeholder num of components as integer field with blank = true not done

class QuizForm(forms.ModelForm):
    class Meta:
        model=Quiz
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

class ImportComponentForm(forms.ModelForm):
    class Meta:
        model=Component
        fields=('orderNumber',)
        
    def __init__(self, component, *args, **kwargs):
        super(ImportComponentForm, self).__init__(*args, **kwargs)
        self.fields['components'] = forms.ModelChoiceField(queryset = component)
        self.fields['orderNumber'].widget.attrs['placeholder'] = 'Component#'

class EditModuleForm(forms.ModelForm):
    class Meta:
        model=Module
        fields=('orderNumber',)
        
    def __init__(self, *args, **kwargs):
        super(EditModuleForm, self).__init__(*args, **kwargs)
        self.fields['orderNumber'].widget.attrs['placeholder'] = 'Module#'


class ImportQuizForm(forms.ModelForm):
    class Meta:
        model=Quiz
        fields=('numOfQuestions','passingMark',)
    
    def __init__(self, quizzes, *args, **kwargs):
        super(ImportQuizForm, self).__init__(*args, **kwargs)
        self.fields['quizzes'] = forms.ModelChoiceField(queryset = quizzes)
        self.fields['numOfQuestions'].widget.attrs['placeholder'] = 'Question#'
        self.fields['passingMark'].widget.attrs['placeholder'] = 'Passing Mark'
