from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(LearnerAccount)
admin.site.register(InstructorAccount)
admin.site.register(Category)
admin.site.register(Courses)
admin.site.register(LearnerCourses)
admin.site.register(Modules)
admin.site.register(Components)
admin.site.register(QuestionBank)