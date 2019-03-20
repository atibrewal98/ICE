from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Learner)
admin.site.register(Instructor)
admin.site.register(Category)
admin.site.register(Courses)
admin.site.register(LearnerCourse)
admin.site.register(Module)
admin.site.register(Component)
admin.site.register(QuestionBank)