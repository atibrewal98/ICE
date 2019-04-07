from django import forms
from .models import Module, Component, Question, User, Instructor, Learner
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

#class SomeForm(forms.Form):
    #Q = Question.objects.filter(moduleID=1)
    #CHOICES=[]
    #for q in Q:
        #CHOICES.append(('1', q.qOption1))
        #CHOICES.append(('2', q.qOption2))
        #CHOICES.append(('3', q.qOption3))
        #CHOICES.append(('4', q.qOption4))
        #choices = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())
        #correct=q.answer
        #CHOICES = []