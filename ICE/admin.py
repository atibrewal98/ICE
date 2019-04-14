from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(Category)
admin.site.register(Component)
admin.site.register(Course)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(LearnerTakesCourse)
admin.site.register(Module)
admin.site.register(Question)
admin.site.register(Token)
admin.site.register(User)
admin.site.register(Staff)
admin.site.register(Quiz)