from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(Category)
admin.site.register(Component)
admin.site.register(Course)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(LearnerCourse)
admin.site.register(Module)
admin.site.register(QuestionBank)
admin.site.register(User)