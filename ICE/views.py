from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from django.views.generic.list import ListView
from django.views.generic import View
from django.template import loader
from ICE.models import Module, Category, Component, Course, Instructor, LearnerTakesCourse, Learner, Question
from .forms import ModuleForm,QuizForm, ComponentForm, UserForm, CourseForm #SomeForm
import operator

class UserFormView(View):	
	userform = UserForm
	template = 'userform.html'

	def get(self,request):
		form = self.userform(None)
		return render(request, self.template, {'userform':form})

	def post(self,request):
		form = self.userform(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			username = form.cleaned_data['userName']
			password = form.cleaned_data['password']
			user.save()
			print("User: ",username," ",password)
			user = authenticate(username=username, password=password)
			print("User: ",user)
			
			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect('../comp/')
		return render(request, self.template, {'userform':form})

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

def course_form(request,instructor_id):
    if request.method=='POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            instance =form.save(commit=False)
            instructor=Instructor.objects.get(userID=instructor_id)
            instance.instructorID = instructor
            instance.save()
            return redirect('../../addModule/instructorID='+instructor_id+'&courseID='+str(instance.courseID)+'/')
    form=CourseForm()
    return render(request,'courseform.html',{'form': form})

def module_form(request,instructor_id,course_id):
    if request.method=='POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            instance=form.save(commit=False)
            course=Course.objects.get(courseID=course_id)
            course.numOfModules = course.numOfModules+1
            course.save()
            instance.courseID=course
            if form.instance.orderNumber is None:
                instance.orderNumber=course.numOfModules
            else:
                modules = Module.objects.filter(courseID=course_id)
                maxOrd = 0
                sameOrd = 0
                for m in modules:
                    if m.orderNumber > maxOrd:
                        maxOrd = m.orderNumber
                print(maxOrd)
                if maxOrd < form.instance.orderNumber:
                    instance.orderNumber=course.numOfModules
                for m in modules:
                    if m.orderNumber == form.instance.orderNumber:
                        sameOrd = m.orderNumber
                if sameOrd != 0:
                    for m in modules:
                        if m.orderNumber >= sameOrd:
                            mod = Module.objects.get(moduleID=m.moduleID)
                            mod.orderNumber = mod.orderNumber + 1
                            mod.save()
            
            instance.save()
            return redirect('../../instructorCourse/instructorID='+instructor_id+'&courseID='+course_id+'&moduleID='+str(instance.moduleID)+'/')
    form=ModuleForm()
    module=Course.objects.filter(courseID=course_id)
    return render(request,'form.html',{'form': form, 'course': module})

def component_form(request,instructor_id,module_id):

    if request.method == 'POST':
        form = ComponentForm(request.POST,request.FILES)
        if form.is_valid():
            instance=form.save(commit=False)
            module=Module.objects.get(moduleID=module_id)
            module.numOfComponents = module.numOfComponents+1
            module.save()
            instance.moduleID=module
            if form.instance.orderNumber is None:
                instance.orderNumber=module.numOfComponents
            else:
                components = Component.objects.filter(moduleID=module_id)
                maxOrd = 0
                sameOrd = 0
                for c in components:
                    if c.orderNumber > maxOrd:
                        maxOrd = c.orderNumber
                print(maxOrd)
                if maxOrd < form.instance.orderNumber:
                    instance.orderNumber=module.numOfComponents
                for c in components:
                    if c.orderNumber == form.instance.orderNumber:
                        sameOrd = c.orderNumber
                if sameOrd != 0:
                    for c in components:
                        if c.orderNumber >= sameOrd:
                            com = Component.objects.get(componentID=c.componentID)
                            com.orderNumber = com.orderNumber + 1
                            com.save()
            instance.save()
            return redirect('../../instructorCourse/instructorID='+instructor_id+'&courseID=1'+'&moduleID='+module_id+'/')
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

def learnerModuleCourseView(request, course_ID, learner_ID, module_ID):
    all_modules=Module.objects.filter(courseID = course_ID)
    all_modules = sorted(all_modules, key=operator.attrgetter('orderNumber'))
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
    components = sorted(components, key=operator.attrgetter('orderNumber'))
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
    }
    return HttpResponse(template.render(context,request))

def instructorCourseModuleView(request, instructor_ID,course_ID, module_ID):
    all_modules=Module.objects.filter(courseID = course_ID)
    all_modules = sorted(all_modules, key=operator.attrgetter('orderNumber'))
    course=Course.objects.get(courseID = course_ID)
    instructor = ''
    title = ''
    components = ''
    instructor=Instructor.objects.get(pk = course.instructorID)
    title=Module.objects.get(moduleID = module_ID)
    components=Component.objects.filter(moduleID = module_ID)
    components = sorted(components, key=operator.attrgetter('orderNumber'))
    template=loader.get_template("ICE/instructorCourse.html")
    context ={
        'all_modules':all_modules,
        'title': title,
        'instructor': instructor,
        'course': course,
        'components': components,
    }
    return HttpResponse(template.render(context,request))

def category_list_view(request, category_id, learner_id):
    all_categories=Category.objects.all()
    courseList=Course.objects.filter(categoryID = category_id)
    categoryCurr=Category.objects.get(categoryID=category_id)
    learnerDetails=Learner.objects.get(userID=learner_id)
    template=loader.get_template("ICE/category.html")
    context ={
        'all_categories':all_categories,
        'courseList': courseList,
        'categoryCurr': categoryCurr,
        'learnerDetails': learnerDetails,
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

def course_learner_view(request, learner_ID):
    all_courses=LearnerTakesCourse.objects.filter(staffID = learner_ID)
    courseDetails = Course.objects.none()
    currModules = LearnerTakesCourse.objects.none()
    learnerDetails= Learner.objects.get(userID=learner_ID)
    for c in all_courses:
        courseDetails = Course.objects.filter(courseID = str(c.courseID)).union(courseDetails)
        currModules=LearnerTakesCourse.objects.filter(courseID = str(c.courseID), staffID = learner_ID).union(currModules)

    template=loader.get_template("ICE/learnerCourseList.html")
    context ={
        'all_courses':all_courses,
        'courseDetails':courseDetails,
        'learnerDetails':learnerDetails,
		'currModules':currModules,
    }
    return HttpResponse(template.render(context,request))

def course_instructor_view(request, instructor_id):
    all_courses=Course.objects.filter(instructorID = instructor_id)
    currModules = Module.objects.none()
    learnerDetails= Instructor.objects.get(userID=instructor_id)
    for c in all_courses:
        currModule=Module.objects.filter(courseID = str(c.courseID))
        for c in currModule:
            currModules = Module.objects.filter(moduleID = c.moduleID).union(currModules)
            break

    template=loader.get_template("ICE/instructorCourseList.html")
    context ={
        'all_courses':all_courses,
        'learnerDetails':learnerDetails,
		'currModules':currModules,
    }
    return HttpResponse(template.render(context,request))

def intructor_view_quiz(request, id):
    all_questions = Question.objects.filter(moduleID=id)
    template = loader.get_template("ICE/question_list.html")
    context = {
        'all_questions': all_questions,
    }
    return HttpResponse(template.render(context, request))

def courseDescriptionView(request, course_id, learner_id):

    if request.method == 'POST':
        learnerC = LearnerTakesCourse.objects.all()
        for l in learnerC:
            if(str(l.courseID) == str(course_id) and str(l.staffID) == str(learner_id)):
                learnerCourse = LearnerTakesCourse.objects.get(staffID=learner_id, courseID=course_id)
                return redirect('../../learnerCourse/learnerID='+learner_id+'&courseID='+course_id+'&moduleID='+str(learnerCourse.currentModule)+'/')
        courseDet = Course.objects.get(courseID=course_id)
        courseDet.currentEnrolled = courseDet.currentEnrolled+1
        courseDet.totalEnrolled = courseDet.totalEnrolled+1
        courseDet.save()
        learnerCourseDet = LearnerTakesCourse()
        learnerCourseDet.staffID = Learner.objects.get(userID=learner_id)
        learnerCourseDet.courseID = Course.objects.get(courseID=course_id)
        learnerCourseDet.completeStatus = 'N'
        learnerCourseDet.currentModule = 1
        learnerCourseDet.save()
        return redirect('../../learnerCourse/learnerID='+learner_id+'&courseID='+course_id+'&moduleID=1/')
    courseDetails = Course.objects.get(courseID=course_id)
    instructorDetails = Instructor.objects.get(userID=str(courseDetails.instructorID))
    template = loader.get_template("ICE/courseDescription.html")
    learnerC = LearnerTakesCourse.objects.all()
    flag = True
    for l in learnerC:
        if(str(l.courseID) == str(course_id) and str(l.staffID) == str(learner_id)):
            flag = False
    if(flag == False):
        context = {
            'courseDetails': courseDetails,
            'instructorDetails': instructorDetails,
            'type': 'View Course',
        }
        return HttpResponse(template.render(context, request))
    else:
        context = {
            'courseDetails': courseDetails,
            'instructorDetails': instructorDetails,
            'type': 'Enroll Course',
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


'''
    Redundant Code
'''

# def monkeyPageView(request):
#     return render(request, 'ICE/monkey.html')



# def learnerCourseView(request, course_ID, learner_ID):
#     all_modules=Module.objects.filter(courseID = course_ID)
#     course=Course.objects.filter(courseID = course_ID)
#     instructor = ''
#     title = ''
#     components = ''
#     done_Modules=Module.objects.none()
#     left_Modules=Module.objects.none()
#     curr_Modules=Module.objects.none()
#     for c in course:
#         instructor=Instructor.objects.filter(pk = c.instructorID)
#     learnerDetails= Learner.objects.filter(userID=learner_ID)
#     currModule=LearnerTakesCourse.objects.filter(courseID = course_ID, staffID = learner_ID)

#     for m in currModule:
#         print(m.currentModule)
#         title=Module.objects.filter(moduleID = m.currentModule)
#         components=Component.objects.filter(moduleID = m.currentModule)
#         curr_Modules=Module.objects.filter(moduleID = m.currentModule)
#     for m in all_modules:
#         for t in curr_Modules:
#             if(m.pk < int(t.moduleID)):
#                 done_Modules = Module.objects.filter(moduleID = m.moduleID).union(done_Modules)
#     for m in all_modules:
#         for t in curr_Modules:
#             if(m.pk > int(t.moduleID)):
#                 left_Modules = Module.objects.filter(moduleID = m.moduleID).union(left_Modules)
      
#     template=loader.get_template("ICE/courseContent.html")
#     context ={
#         'all_modules':all_modules,
#         'title': title,
#         'instructor': instructor,
#         'course': course,
#         'components': components,
#         'learnerDetails': learnerDetails,
#         'left_Modules':left_Modules,
#         'done_Modules':done_Modules,
#         'currModule':curr_Modules,
#         # 'components1': components1,
#     }
#     return HttpResponse(template.render(context,request))



# def instructorCourseView(request, course_ID):
#     all_modules=Module.objects.filter(courseID = course_ID)
#     course=Course.objects.filter(courseID = course_ID)
#     instructor = ''
#     title = Module.objects.none()
#     components = ''
#     for c in course:
#         instructor=Instructor.objects.filter(pk = c.instructorID)
#     for m in all_modules:
#         title = Module.objects.filter(moduleID = m.moduleID).union(title)
#         break
#     for t in title:
#         components=Component.objects.filter(moduleID = t.moduleID)
#     template=loader.get_template("ICE/instructorCourse.html")
#     context ={
#         'all_modules':all_modules,
#         'title': title,
#         'instructor': instructor,
#         'course': course,
#         'components': components,
#     }
#     return HttpResponse(template.render(context,request))