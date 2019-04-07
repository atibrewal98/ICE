from django.db import models
import random, string
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class MyUserManager(BaseUserManager):
    def create_user(self, userID, emailID, firstName=None, lastName=None, password=None, userName=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not emailID:
            raise ValueError('Users must have an email address')

        user = self.model(
            emailID=self.normalize_email(emailID),
            userID = userID,
            firstName = firstName,
            lastName = lastName,
            userName = userName
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, password, emailID, userID=None,firstName=None, lastName=None, userName=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            userID,
            emailID, 
            firstName,
            lastName,
            password,
            userName
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active=True
        
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    userID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=50, null=True)
    lastName = models.CharField(max_length=50, null = True)
    emailID = models.EmailField(max_length=50, null=True, unique = True)
    userName = models.CharField(max_length=50, unique=True, null = True)
    password = models.CharField(max_length=50, null = True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    USERNAME_FIELD = 'emailID'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return str(self.userID)
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True

    
class Learner(User):
    #learnerID = models.AutoField(primary_key = True)
    #staffID = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    totalCECU = models.PositiveIntegerField(default=0)
    def __str__(self):
        return str(self.userID)

class Instructor(User):
    #instructorID = models.AutoField(primary_key = True)
    #instructorID = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    biography = models.CharField(max_length=250, null = True)
    def __str__(self):
        return self.firstName + " " + self.lastName

class Category(models.Model):
    categoryID = models.AutoField(primary_key = True)
    categoryName = models.CharField(max_length=100, unique = True)
    def __str__(self):
        return self.categoryName

class Course(models.Model):
    courseID = models.AutoField(primary_key = True)
    instructorID = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    courseName = models.CharField(max_length=100)
    courseCECU = models.PositiveIntegerField(default=0)
    courseDescription = models.CharField(max_length=200)
    # 'L' for live
    # 'U' for course under development
    # 'R' for under review by HR
    # 'N' for course not live and unavailable
    courseStatus = models.CharField(max_length=1)
    numOfModules = models.IntegerField(default = 0)
    totalEnrolled = models.IntegerField(default = 0)
    currentEnrolled = models.IntegerField(default = 0)
    def __str__(self):
        return str(self.courseID)

class LearnerTakesCourse(models.Model):
    staffID = models.ForeignKey(Learner, on_delete=models.CASCADE)
    courseID = models.ForeignKey(Course, on_delete=models.CASCADE)
    # 'Y' for completed
    # 'N' for course under process
    completeStatus = models.CharField(max_length=1)
    completionDate = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    currentModule = models.IntegerField(null=True, blank = True)
    def __str__(self):
        return f'{self.staffID} ({self.courseID})'

class Module(models.Model):
    moduleID = models.AutoField(primary_key = True)
    courseID = models.ForeignKey(Course, on_delete=models.CASCADE)
    moduleTitle = models.CharField(max_length=100)
    orderNumber = models.IntegerField()
    numOfComponents = models.IntegerField(default = 0)
    numOfQuestions = models.IntegerField(null = True, blank = True)
    passingMark = models.IntegerField(null = True, blank = True)
    def __str__(self):
        return str(self.courseID) + ":" + str(self.moduleID) + " : " + self.moduleTitle

class Component(models.Model):
    componentID = models.AutoField(primary_key = True)
    moduleID = models.ForeignKey(Module, on_delete=models.CASCADE)
    componentTitle = models.CharField(max_length=100)
    componentText = models.CharField(max_length=100, null=True, blank = True)
    componentImage = models.ImageField(upload_to='images/',null=True, blank=True)
    orderNumber = models.IntegerField()
    createdAt = models.DateField(auto_now=False, auto_now_add=True)
    updatedAt = models.DateField(auto_now=True)
    def __str__(self):
        return str(self.componentID)

class Question(models.Model):
    questionID = models.AutoField(primary_key = True)
    moduleID = models.ForeignKey(Module, on_delete=models.CASCADE)
    questionStatement = models.CharField(max_length=200)
    qOption1 = models.CharField(max_length=50)
    qOption2 = models.CharField(max_length=50)
    qOption3 = models.CharField(max_length=50)
    qOption4 = models.CharField(max_length=50)
    # answer is 'i' where i is 1, 2, 3, 4
    answer = models.CharField(max_length=1)
    def __str__(self):
        return self.questionStatement

class Token(models.Model):
    def generateToken():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(6))
    
    email = models.EmailField(max_length=50, unique = True)
    token = models.CharField(max_length=6, default=generateToken(), editable=False)

    def __str__(self):
        return (self.email + ":" + self.token)