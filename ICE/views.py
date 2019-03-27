from django.shortcuts import render, HttpResponse
from django.views.generic.list import ListView
from django.template import loader
from ICE.models import Module, Category, Component, Course, Instructor, LearnerTakesCourse, Learner, Question



from .forms import ModuleForm,QuizForm, ComponentForm, SomeForm

def quiz_form(request,id):
    if request.method == 'POST':
        instance=Module.objects.get(moduleID=id)
        print(instance.numOfComponents)
        quizform = QuizForm(request.POST,instance=instance)
        if quizform.is_valid():
            quizform.save()
    quizform=QuizForm()
    module = Module.objects.filter(moduleID=id)
    return render(request, 'quizform.html', {'quizform': quizform, 'module': module})


def module_form(request, id):
    print("Course ID inherited: ", id)
    if request.method == 'POST':


        form = ModuleForm(request.POST)

        if form.is_valid():
            instance=form.save(commit=False)
            course = Course.objects.get(courseID=id)
            instance.courseID=course
            instance.save()

    form=ModuleForm()
    module = Course.objects.filter(courseID=id)
    return render(request, 'form.html', {'form': form, 'course': module})

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

def learnerCourseView(request, course_ID, learner_ID):
    all_modules=Module.objects.filter(courseID = course_ID)
    course=Course.objects.filter(courseID = course_ID)
    instructor = ''
    title = ''
    components = ''
    done_Modules=Module.objects.none()
    left_Modules=Module.objects.none()
    curr_Modules=Module.objects.none()
    for c in course:
        instructor=Instructor.objects.filter(pk = c.instructorID)
    learnerDetails= Learner.objects.filter(userID=learner_ID)
    currModule=LearnerTakesCourse.objects.filter(courseID = course_ID, staffID = learner_ID)
    # components=Component.objects.filter(componentID = 1)
    # components1=Component.objects.filter(componentID = 2)
    for m in currModule:
        print(m.currentModule)
        title=Module.objects.filter(moduleID = m.currentModule)
        components=Component.objects.filter(moduleID = m.currentModule)
        curr_Modules=Module.objects.filter(moduleID = m.currentModule)
    for m in all_modules:
        for t in curr_Modules:
            if(m.pk < int(t.moduleID)):
                done_Modules = Module.objects.filter(moduleID = m.moduleID).union(done_Modules)
    for m in all_modules:
        for t in curr_Modules:
            if(m.pk > int(t.moduleID)):
                left_Modules = Module.objects.filter(moduleID = m.moduleID).union(left_Modules)
      
    template=loader.get_template("ICE/courseContent.html")
    context ={
        'all_modules':all_modules,
        'title': title,
        'instructor': instructor,
        'course': course,
        'components': components,
        'learnerDetails': learnerDetails,
        'left_Modules':left_Modules,
        'done_Modules':done_Modules,
        'currModule':curr_Modules,
        # 'components1': components1,
    }
    return HttpResponse(template.render(context,request))

def learnerModuleCourseView(request, course_ID, learner_ID, module_ID):
    all_modules=Module.objects.filter(courseID = course_ID)
    course=Course.objects.filter(courseID = course_ID)
    instructor = ''
    title = ''
    components = ''
    done_Modules=Module.objects.none()
    left_Modules=Module.objects.none()
    curr_Modules=Module.objects.none()
    learnerDetails= Learner.objects.filter(userID=learner_ID)
    for c in course:
        instructor=Instructor.objects.filter(pk = c.instructorID)
    title=Module.objects.filter(moduleID = module_ID)
    components=Component.objects.filter(moduleID = module_ID)
    # components1=Component.objects.filter(componentID = 2)
    currModule=LearnerTakesCourse.objects.filter(courseID = course_ID, staffID = learner_ID)
    
    for m in currModule:
        curr_Modules=Module.objects.filter(moduleID = m.currentModule)
    for m in all_modules:
        for t in curr_Modules:
            if(m.pk < int(t.moduleID)):
                done_Modules = Module.objects.filter(moduleID = m.moduleID).union(done_Modules)
    for m in all_modules:
        for t in curr_Modules:
            if(m.pk > int(t.moduleID)):
                left_Modules = Module.objects.filter(moduleID = m.moduleID).union(left_Modules)

    template=loader.get_template("ICE/courseContent.html")
    context ={
        'all_modules':all_modules,
        'title': title,
        'instructor': instructor,
        'course': course,
        'components': components,
        'learnerDetails': learnerDetails,
        'left_Modules':left_Modules,
        'done_Modules':done_Modules,
        'currModule':curr_Modules,
        # 'components1': components1,
    }
    return HttpResponse(template.render(context,request))

def instructorCourseView(request, course_ID):
    all_modules=Module.objects.filter(courseID = course_ID)
    course=Course.objects.filter(courseID = course_ID)
    instructor = ''
    title = Module.objects.none()
    components = ''
    for c in course:
        instructor=Instructor.objects.filter(pk = c.instructorID)
    for m in all_modules:
        title = Module.objects.filter(moduleID = m.moduleID).union(title)
        break
    for t in title:
        components=Component.objects.filter(moduleID = t.moduleID)
    # components1=Component.objects.filter(componentID = 2)
    template=loader.get_template("ICE/instructorCourse.html")
    context ={
        'all_modules':all_modules,
        'title': title,
        'instructor': instructor,
        'course': course,
        'components': components,
        # 'components1': components1,
    }
    return HttpResponse(template.render(context,request))

def instructorCourseModuleView(request, course_ID, module_ID):
    all_modules=Module.objects.filter(courseID = course_ID)
    course=Course.objects.filter(courseID = course_ID)
    instructor = ''
    title = ''
    components = ''
    for c in course:
        instructor=Instructor.objects.filter(pk = c.instructorID)
    title=Module.objects.filter(moduleID = module_ID)
    components=Component.objects.filter(moduleID = module_ID)
    # components1=Component.objects.filter(componentID = 2)
    template=loader.get_template("ICE/instructorCourse.html")
    context ={
        'all_modules':all_modules,
        'title': title,
        'instructor': instructor,
        'course': course,
        'components': components,
        # 'components1': components1,
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

def course_list_view(request, learner_ID):
    all_courses=LearnerTakesCourse.objects.filter(staffID = learner_ID)
    courseDetails = Course.objects.none()
    learnerDetails= Learner.objects.filter(userID=learner_ID)
    for c in all_courses:
        print(c.courseID)
        courseDetails = Course.objects.filter(courseID = str(c.courseID)).union(courseDetails)
    template=loader.get_template("ICE/courseList.html")
    context ={
        'all_courses':all_courses,
        'courseDetails':courseDetails,
        'learnerDetails':learnerDetails,
    }
    return HttpResponse(template.render(context,request))

def intructor_view_quiz(request, id):
    all_questions = Question.objects.filter(moduleID=id)
    template = loader.get_template("ICE/question_list.html")
    context = {
        'all_questions': all_questions,
    }
    return HttpResponse(template.render(context, request))

def some_view(request):
    questions=Question.objects.filter(moduleID=1)
    if request.method == 'POST':


            form = SomeForm(request.POST)
            if form.is_valid():
                choices = form.cleaned_data.get('choices')

                if (choices[0] == form.correct):
                    learner=LearnerTakesCourse.objects.get(staffID=2, courseID=1)
                    learner.currentModule=learner.currentModule+1
                    learner.save()
                    ans = "Congrats you have passed"
                    return render(request, 'quiz_result.html', {'ans': ans})

                else:
                    ans = "Sorry try again"
                    return render(request, 'quiz_result.html', {'ans': ans})

    else:
        form = SomeForm

    return render(request,'some_template.html', {'form':form, 'questions': questions })