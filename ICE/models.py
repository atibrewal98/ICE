from django.db import models
import random, string

# Create your models here.

class User(models.Model):
    userID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    emailID = models.EmailField(max_length=50, null=True, unique = True)
    userName = models.CharField(max_length=50, unique=True, null = True)
    password = models.CharField(max_length=50, null = True)
    def __str__(self):
        return str(self.userID)
    
class Learner(User):
    #learnerID = models.AutoField(primary_key = True)
    #staffID = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    totalCECU = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.firstName + " " + self.lastName + " " + str(self.userID)

class Instructor(User):
    #instructorID = models.AutoField(primary_key = True)
    #instructorID = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    biography = models.CharField(max_length=250)
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
        return self.courseName

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
        return str(self.moduleID) + " : " + self.moduleTitle

class Component(models.Model):
    componentID = models.AutoField(primary_key = True)
    moduleID = models.ForeignKey(Module, on_delete=models.CASCADE)
    componentTitle = models.CharField(max_length=100)
    componentText = models.CharField(max_length=100, null=True, blank = True)
    componentImage = models.CharField(max_length=100, null = True, blank = True)
    orderNumber = models.IntegerField()
    createdAt = models.DateField(auto_now=False, auto_now_add=True)
    updatedAt = models.DateField(auto_now=True)
    def __str__(self):
        return self.componentTitle

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