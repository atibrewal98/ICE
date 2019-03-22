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
        return self.userName
    
class Learner(models.Model):
    #learnerID = models.AutoField(primary_key = True)
    userID = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True)
    totalCECU = models.IntegerField()
    def __str__(self):
        return self.userID

class Instructor(models.Model):
    #instructorID = models.AutoField(primary_key = True)
    userID = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True)
    biography = models.CharField(max_length=250)
    def __str__(self):
        return self.userID

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
    courseCECU = models.IntegerField()
    courseDesc = models.CharField(max_length=200)
    # 'L' for live
    # 'U' for course under development
    # 'R' for under review by HR
    # 'N' for course not live and unavailable
    courseStatus = models.CharField(max_length=1)
    numOfModules = models.IntegerField(default = 0)
    def __str__(self):
        return self.courseName

class LearnerCourse(models.Model):
    learnerID = models.ForeignKey(Learner, on_delete=models.CASCADE)
    courseID = models.ForeignKey(Course, on_delete=models.CASCADE)
    # 'Y' for completed
    # 'N' for course under process
    completeStatus = models.CharField(max_length=1)
    completionDate = models.DateField(auto_now=False, auto_now_add=False, null=True)
    currentModule = models.IntegerField(null=True)
    def __str__(self):
        return f'{self.staffID} ({self.courseID})'

class Module(models.Model):
    moduleID = models.AutoField(primary_key = True)
    courseID = models.ForeignKey(Course, on_delete=models.CASCADE)
    moduleTitle = models.CharField(max_length=100)
    orderNumber = models.IntegerField()
    numOfComponents = models.IntegerField(default = 0)
    numOfQuestions = models.IntegerField(null = True)
    passingMark = models.IntegerField(null = True)
    def __str__(self):
        return self.moduleTitle

class Component(models.Model):
    componentID = models.AutoField(primary_key = True)
    moduleID = models.ForeignKey(Module, on_delete=models.CASCADE)
    componentTitle = models.CharField(max_length=100)
    componentText = models.CharField(max_length=100, null=True)
    componentImage = models.CharField(max_length=100, null = True)
    orderNumber = models.IntegerField()
    createdAt = models.DateField(auto_now=False, auto_now_add=True)
    updatedAt = models.DateField(auto_now=True)
    def __str__(self):
        return self.componentTitle

class QuestionBank(models.Model):
    questionID = models.AutoField(primary_key = True)
    moduleID = models.ForeignKey(Module, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    qAnswer1 = models.CharField(max_length=50)
    qAnswer2 = models.CharField(max_length=50)
    qAnswer3 = models.CharField(max_length=50)
    qAnswer4 = models.CharField(max_length=50)
    # answer is 'i' where i is 1, 2, 3, 4
    answer = models.CharField(max_length=1)
    def __str__(self):
        return self.question

class Token(models.Model):
    def generateToken():
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(6))
    
    email = models.EmailField(max_length=50, unique = True)
    token = models.CharField(max_length=6, default=generateToken(), editable=False)

    def __str__(self):
        return self.email