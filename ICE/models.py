from django.db import models
import random, string
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import datetime

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
    ADMIN = 0
    INSTRUCTOR = 1
    LEARNER = 2
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (INSTRUCTOR, 'Instructor'),
        (LEARNER, 'Learner'),
    )
    userID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=50, null=True)
    lastName = models.CharField(max_length=50, null = True)
    emailID = models.EmailField(max_length=50, null=True, unique = True)
    userName = models.CharField(max_length=50, unique=True, null = True)
    password = models.CharField(max_length=50, null = True)
    is_staff = models.BooleanField(default=False) #for django admin
    is_active = models.BooleanField(default=False) #for django admin
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True)

    USERNAME_FIELD = 'emailID'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return str(self.userID)
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True

class Staff(models.Model):
    staffID = models.AutoField(primary_key = True)
    emailID = models.EmailField(max_length=50, null=True, unique = True)
    firstName = models.CharField(max_length=50, null=True)
    lastName = models.CharField(max_length=50, null = True)

class Learner(User):
    totalCECU = models.PositiveIntegerField(default=0)
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)
    
    def updateCECU(self,value):
        self.totalCECU+=value

    def __str__(self):
        return str(self.userID)

class Instructor(User):
    biography = models.CharField(max_length=250, null = True)
    def __str__(self):
        return str(self.userID)

class Category(models.Model):
    categoryID = models.AutoField(primary_key = True)
    categoryName = models.CharField(max_length=100, unique = True)

    def __str__(self):
        return str(self.categoryID)

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
    courseStatus = models.CharField(max_length=1, default = 'U')
    numOfModules = models.IntegerField(default = 0)
    totalEnrolled = models.IntegerField(default = 0)
    currentEnrolled = models.IntegerField(default = 0)

    def getModule(self):
        return Module.objects.filter(courseID=self.courseID)
    
    def getComponent(self):
        return Component.objects.filter(courseID=self.courseID)

    def getQuiz(self):
        return Quiz.objects.filter(courseID=self.courseID)    

    def __str__(self):
        return str(self.courseID)

class LearnerTakesCourse(models.Model):
    staffID = models.ForeignKey(Learner, on_delete=models.CASCADE)
    courseID = models.ForeignKey(Course, on_delete=models.CASCADE)
    # 'Y' for completed
    # 'N' for course under process
    completeStatus = models.CharField(max_length=1,default='N')
    completionDate = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    currentModule = models.IntegerField(null=True, blank = True)

    def updateCourse(self):
        course = Course.objects.get(courseID=str(self.courseID))
        if self.currentModule==course.numOfModules:
            course.currentEnrolled -= 1
            course.save()
            self.completeStatus='Y'
            self.completionDate=datetime.date.today()
            self.currentModule=1
        else:
            self.currentModule+=1

    def __str__(self):
        return f'{self.staffID} ({self.courseID})'

class Module(models.Model):
    moduleID = models.AutoField(primary_key = True)
    courseID = models.ForeignKey(Course, on_delete=models.CASCADE)
    moduleTitle = models.CharField(max_length=100)
    orderNumber = models.IntegerField(null = True, blank = True)
    numOfComponents = models.IntegerField(default = 0)
    
    def getQuiz(self):
        return Quiz.objects.get(moduleID=self.moduleID)

    def getComponent(self):
        return Component.objects.filter(moduleID=self.moduleID)

    def getCourse(self):
        return Course.objects.get(courseID=str(self.courseID))

    def __str__(self):
        return str(self.courseID) + ":" + str(self.moduleID) + " : " + self.moduleTitle

class Component(models.Model):
    componentID = models.AutoField(primary_key = True)
    courseID = models.ForeignKey(Course, null = True, blank = True, on_delete=models.CASCADE)
    moduleID = models.ForeignKey(Module, null = True, blank = True, on_delete=models.CASCADE)
    componentTitle = models.CharField(max_length=100)
    componentText = models.CharField(max_length=100, null=True, blank = True)
    componentImage = models.ImageField(upload_to='images/',null=True, blank=True)
    orderNumber = models.IntegerField(null = True, blank = True)
    createdAt = models.DateField(auto_now=False, auto_now_add=True)
    updatedAt = models.DateField(auto_now=True)
    def __str__(self):
        return str(self.componentID)

class Quiz(models.Model):
    quizID=models.AutoField(primary_key = True)
    moduleID = models.ForeignKey(Module, on_delete=models.CASCADE,null=True, blank = True)
    courseID = models.ForeignKey(Course, on_delete=models.CASCADE)
    numOfQuestions = models.IntegerField(null = False, default=1)
    passingMark = models.IntegerField(null = False, default=1)

    def getQuestions(self):
        return sorted(Question.objects.filter(quizID=self.quizID)[:self.numOfQuestions], key=lambda x: random.random())
    
    def __str__(self):
        return str(self.quizID)
class Question(models.Model):
    questionID = models.AutoField(primary_key = True)
    quizID = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    questionStatement = models.CharField(max_length=200,blank=False)
    qOption1 = models.CharField(max_length=50,blank=False)
    qOption2 = models.CharField(max_length=50,blank=False)
    qOption3 = models.CharField(max_length=50,blank=False)
    qOption4 = models.CharField(max_length=50,blank=False)
    # answer is 'i' where i is 1, 2, 3, 4
    answer = models.CharField(max_length=1)
        
    def getAnswer(self):
        return self.answer

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