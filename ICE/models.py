from django.db import models

# Create your models here.
class LearnerAccount(models.Model):
    staffID = models.IntegerField(primary_key = True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    emailID = models.EmailField(max_length=50)
    userName = models.CharField(max_length=50, unique = True)
    password = models.CharField(max_length=50)
    totalCECU = models.IntegerField()
    def __str__(self):
        return self.userName