from django.shortcuts import render, HttpResponse
from django.views.generic.list import ListView
from django.template import loader
from ICE.models import Module, Category, Component, Course, Instructor, LearnerTakesCourse



from .forms import ModuleForm,QuizForm, ComponentForm

def quiz_form(request,id):
    if request.method == 'POST':
        instance=Module.objects.get(moduleID=id)
        print(instance.numOfComponents)
        quizform = QuizForm(request.POST,instance=instance)
        if quizform.is_valid():
            quizform.save()
    quizform=QuizForm()
    return render(request, 'quizform.html', {'quizform': quizform})


def module_form(request, id):
    print("Course ID inherited: ", id)
    if request.method == 'POST':
        instance=Course.objects.get(courseID=id)
        print("Instance: ", instance)
        form = ModuleForm(request.POST)
        if form.is_valid():
            form.save()
    form=ModuleForm()
    return render(request, 'form.html', {'form': form})

def component_form(request):

    if request.method == 'POST':
        form = ComponentForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
    componentform=ComponentForm()
    return render(request, 'component.html', {'componentform': componentform})

def component(request):
    component=Component.objects.all()
    template=loader.get_template("ICE/component.html")
    context ={
        'component':component,
    }
    return HttpResponse(template.render(context,request))

# Create your views here.
def monkeyPageView(request):
    return render(request, 'ICE/monkey.html')

def learnerCourseView(request, course_ID, module_ID, learner_ID):
    all_modules=Module.objects.filter(courseID = course_ID)
    course=Course.objects.filter(courseID = course_ID)
    instructor = ''
    title = ''
    components = ''
    for c in course:
        instructor=Instructor.objects.filter(pk = c.instructorID)
    currModule=LearnerTakesCourse.objects.filter(courseID = course_ID, staffID = learner_ID)
    for m in currModule:
        title=Module.objects.filter(moduleID = m.currentModule)
        components=Component.objects.filter(moduleID = m.currentModule)
    template=loader.get_template("ICE/courseContent.html")
    context ={
        'all_modules':all_modules,
        'title': title,
        'instructor': instructor,
        'course': course,
        'components': components
    }
    return HttpResponse(template.render(context,request))

def instructorCourseView(request, course_ID, module_ID):
    all_modules=Module.objects.filter(courseID = course_ID)
    course=Course.objects.filter(courseID = course_ID)
    instructor = ''
    title = ''
    components = ''
    for c in course:
        instructor=Instructor.objects.filter(pk = c.instructorID)
    title=Module.objects.filter(moduleID = module_ID)
    components=Component.objects.filter(moduleID = module_ID)
    template=loader.get_template("ICE/instructorCourse.html")
    context ={
        'all_modules':all_modules,
        'title': title,
        'instructor': instructor,
        'course': course,
        'components': components
    }
    return HttpResponse(template.render(context,request))

def category_list_view(request):
    all_categories=Category.objects.all()
    template=loader.get_template("ICE/category.html")
    context ={
        'all_categories':all_categories,
    }
    return HttpResponse(template.render(context,request))

def module_list_view(request):
    all_modules=Module.objects.all()
    template=loader.get_template("ICE/module_List.html")
    context ={
        'all_modules':all_modules,
    }
    return HttpResponse(template.render(context,request))

def component_list_view(request, module_ID):
    all_components=Component.objects.filter(moduleID = module_ID)
    template=loader.get_template("ICE/component_List.html")
    context ={
        'all_components':all_components,
    }
    return HttpResponse(template.render(context,request))