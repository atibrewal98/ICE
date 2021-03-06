from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from django.views.generic.list import ListView
from django.views.generic import View
from django.template import loader

from ICE.models import Module, Category, Component, Course, Instructor, LearnerTakesCourse, Learner, Question, User, Staff, Quiz
from .forms import ModuleForm, ImportComponentForm, UserForm, InviteForm, SignupFormInstructor, LearnerGetTokenForm, SignupFormLearner
from .forms import CourseForm, ImportQuizForm, EditModuleForm, EditComponentForm
import operator
import requests

"""
FOR AUTHENTICATION
"""
from django.contrib.auth.decorators import login_required
from ICE.decorators import admin_required
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import redirect
from .tokens import account_activation_token

def learner_quiz(request,module_ID):
    """
    Only the learner who has access to the course can access this.
    """
    if request.user.role != 2:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    courseID=Module.objects.get(moduleID=module_ID).getCourse().courseID
    learner_ID = request.user.userID
    # print(courseID)
    # print(learner_ID)
    try:
        # print("HEY")
        lcs = LearnerTakesCourse.objects.filter(courseID=courseID)
        lc = LearnerTakesCourse.objects.get(courseID=courseID, staffID = learner_ID)        
    except Exception as e :
        # print(e)
        """
        The learner doesn't take this course
        """
        context= {
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
        
    course=Module.objects.get(moduleID=module_ID).getCourse()
    record=LearnerTakesCourse.objects.get(staffID=request.user.userID,courseID=courseID)
    if request.method=='POST':
        correct=0
        for key, value in request.POST.items():
            if key!='csrfmiddlewaretoken':
                if Question.objects.get(questionID=key).getAnswer()==value:
                    correct+=1
        if Module.objects.get(moduleID=module_ID).getQuiz().passingMark<=correct:
            record.updateCourse()
            record.save()
            if record.completeStatus=='Y':
                user=Learner.objects.get(userID=request.user.userID)
                user.updateCECU(Module.objects.get(moduleID=module_ID).getCourse().courseCECU)
                user.save()
                email = EmailMessage(
                'Course completion confirmation',
                render_to_string('ICE/quiz_email.html', {
                    'course': course,
                }),
                to=[Learner.objects.get(userID=request.user.userID).emailID])
                email.send()
            numOfQues=Module.objects.get(moduleID=module_ID).getQuiz().numOfQuestions
            return render(request, 'quiz_result.html', {'result': correct,'numOfQues':numOfQues,'courseID':courseID,'moduleID':record.currentModule})
        else:
            return render(request, 'quiz_result.html', {'result': -1,'courseID':courseID,'moduleID':record.currentModule})
    if record.currentModule==Module.objects.get(moduleID=module_ID).orderNumber and record.completeStatus!='Y':
        questions=Module.objects.get(moduleID=module_ID).getQuiz().getQuestions()
        return render(request, 'quiz_template.html', {'questions': questions})
    else:
        context={
            'message': "You don't have access to this quiz."
        }
        return render(request, 'ICE/message.html', context)

@login_required
def course_form(request):
    if request.user.role != 1:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_id = request.user.userID
    if request.method=='POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            instance =form.save(commit=False)
            instructor=Instructor.objects.get(userID=instructor_id)
            instance.instructorID = instructor
            instance.save()
            return redirect('../addModule/courseID='+str(instance.courseID)+'/')
    form = CourseForm()
    return render(request,'add_course.html',{'courseform': form})

@login_required
def module_form(request, course_id):
    """
    Only the instructor who is the creator of the course can access this.
    """
    course=Course.objects.get(courseID = course_id)
    if request.user.role != 1 or (course.instructorID.userID != request.user.userID):
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    if request.user.role != 1:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_id = request.user.userID
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
            return redirect('../../instructorCourse/courseID='+course_id+'&moduleID='+str(instance.orderNumber)+'/')
    form=ModuleForm()
    module=Course.objects.filter(courseID=course_id)
    return render(request,'add_module.html',{'moduleform': form, 'course': module})

def import_quiz(request,module_ID):
    """
    Only the instructor who is the creator of the course to which this module belongs can access this.
    """
    course = Module.objects.get(moduleID=module_ID).getCourse()
    if request.user.role != 1 or (course.instructorID.userID != request.user.userID):
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    if request.method=='POST':
        quiz=Quiz.objects.none()
        passingMark=0
        numOfQuestions=0
        for key, value in request.POST.items():
            if key=='quizzes':
                quiz=Quiz.objects.get(quizID=value)
            elif key=='numOfQuestions':
                numOfQuestions=value
            elif key=='passingMark':
                passingMark=value
        quiz.passingMark=passingMark
        quiz.numOfQuestions=numOfQuestions
        quiz.moduleID=Module.objects.get(moduleID=module_ID)
        quiz.save()
        course_ID=Module.objects.get(moduleID=module_ID).getCourse().courseID
        orderNumber=Module.objects.get(moduleID=module_ID).orderNumber
        return redirect('../../instructorCourse/courseID='+str(course_ID)+'&moduleID='+str(orderNumber)+'/')
    quizzes=Module.objects.get(moduleID=module_ID).getCourse().getQuiz()
    quiz=Quiz.objects.none()
    for q in quizzes:
        if q.moduleID is None:
            quiz=Quiz.objects.filter(quizID=q.quizID).union(quiz)
    form=ImportQuizForm(quiz)
    return render(request, 'import_quiz.html', {'form': form})

@login_required
def edit_module_form(request, module_id):
    """
    Only the instructor who is the creator of the course to which this module belongs can access this.
    """
    course = Module.objects.get(moduleID=module_id).getCourse()
    if request.user.role != 1 or (course.instructorID.userID != request.user.userID):
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_id = request.user.userID
    if request.method == 'POST':
        module=Module.objects.get(moduleID=module_id)
        ordNum = 0
        for key, value in request.POST.items():
            if key=='orderNumber':
                ordNum = value
        course = module.getCourse()
        modules = Module.objects.filter(courseID=course.courseID)
        maxOrd = 0
        sameOrd = 0
        for m in modules:
            if m.orderNumber > maxOrd:
                maxOrd = m.orderNumber
        if int(maxOrd) < int(ordNum):
            for m in modules:
                if m.orderNumber > module.orderNumber:
                    mod = Module.objects.get(moduleID = m.moduleID)
                    mod.orderNumber -= 1
                    mod.save()
            module.orderNumber=course.numOfModules
            module.save()
        elif int(ordNum) == 0:
            for m in modules:
                if m.orderNumber < module.orderNumber:
                    mod = Module.objects.get(moduleID = m.moduleID)
                    mod.orderNumber += 1
                    mod.save()
            module.orderNumber = 1
            module.save()
        else:    
            for m in modules:
                if int(m.orderNumber) == int(ordNum):
                    sameOrd = m.orderNumber
            if int(sameOrd) != 0 and int(sameOrd) > int(module.orderNumber):
                for m in modules:
                    if int(m.orderNumber) <= int(sameOrd) and int(m.orderNumber) > int(module.orderNumber):
                        mod = Module.objects.get(moduleID=m.moduleID)
                        mod.orderNumber = mod.orderNumber - 1
                        mod.save()
                module.orderNumber = ordNum
                module.save()
            elif int(sameOrd) != 0 and int(sameOrd) < int(module.orderNumber):
                for m in modules:
                    if int(m.orderNumber) >= int(sameOrd) and int(m.orderNumber) < int(module.orderNumber):
                        mod = Module.objects.get(moduleID=m.moduleID)
                        mod.orderNumber = mod.orderNumber + 1
                        mod.save()
                module.orderNumber = ordNum
                module.save()
        return redirect('../../instructorCourse/courseID='+str(course.courseID)+'&moduleID=1/')
    form = EditModuleForm()
    return render(request, 'edit_module.html', {'moduleform': form})

@login_required
def edit_component_form(request, component_id):
    """
    Only the instructor who is the creator of the course to which this module belongs can access this.
    """
    course = Component.objects.get(componentID=component_id).getModule().getCourse()
    if request.user.role != 1 or (course.instructorID.userID != request.user.userID):
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_id = request.user.userID
    if request.method == 'POST':
        component=Component.objects.get(componentID=component_id)
        ordNum = 0
        for key, value in request.POST.items():
            if key=='orderNumber':
                ordNum = value
        module = component.getModule()
        components = Component.objects.filter(moduleID=module.moduleID)
        maxOrd = 0
        sameOrd = 0
        for c in components:
            if c.orderNumber > maxOrd:
                maxOrd = c.orderNumber
        if int(maxOrd) < int(ordNum):
            for c in components:
                if c.orderNumber > component.orderNumber:
                    com = Component.objects.get(componentID = c.componentID)
                    com.orderNumber -= 1
                    com.save()
            component.orderNumber=module.numOfComponents
            component.save()
        elif int(ordNum) == 0:
            for c in components:
                if c.orderNumber < component.orderNumber:
                    com = Component.objects.get(componentID = c.componentID)
                    com.orderNumber += 1
                    com.save()
            component.orderNumber = 1
            component.save()
        else:    
            for m in components:
                if int(m.orderNumber) == int(ordNum):
                    sameOrd = m.orderNumber
            if int(sameOrd) != 0 and int(sameOrd) > int(component.orderNumber):
                for c in components:
                    if int(c.orderNumber) <= int(sameOrd) and int(c.orderNumber) > int(component.orderNumber):
                        com = Component.objects.get(componentID = c.componentID)
                        com.orderNumber = com.orderNumber - 1
                        com.save()
                component.orderNumber = ordNum
                component.save()
            elif int(sameOrd) != 0 and int(sameOrd) < int(component.orderNumber):
                for c in components:
                    if int(c.orderNumber) >= int(sameOrd) and int(c.orderNumber) < int(component.orderNumber):
                        com = Component.objects.get(componentID = c.componentID)
                        com.orderNumber = com.orderNumber + 1
                        com.save()
                component.orderNumber = ordNum
                component.save()
        return redirect('../../instructorCourse/courseID='+str(course.courseID)+'&moduleID=1/')
    form = EditComponentForm()
    return render(request, 'edit_component.html', {'form': form})

@login_required
def import_component_form(request, module_id):
    """
    Only the instructor who is the creator of the course to which this module belongs can access this.
    """
    course = Module.objects.get(moduleID=module_id).getCourse()
    if (request.user.role != 1) or (course.instructorID.userID != request.user.userID): 
        print(course.courseID)
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_id = request.user.userID
    if request.method == 'POST':
        course = Module.objects.get(moduleID=module_id).getCourse()
        print('CCC', course)
        componentID=0
        components = course.getComponent()
        component = Component.objects.none()
        for key, value in request.POST.items():
            if key=='components':
                componentID = value
        print(componentID)
        component = Component.objects.filter(componentID=componentID)
        form = ImportComponentForm(component, request.POST)
        if form.is_valid():
            print("111")
            instance=form.save(commit=False)
            module=Module.objects.get(moduleID=module_id)
            components = Component.objects.get(componentID=componentID)
            module.numOfComponents = module.numOfComponents+1
            module.save()
            instance.moduleID=module
            instance.componentID=components.componentID
            instance.courseID = components.courseID
            instance.componentTitle = components.componentTitle
            print("Here", form.instance.orderNumber)
            if(components.componentText is not None):
                instance.componentText = components.componentText
            if(components.componentImage is not None):
                instance.componentImage = components.componentImage
            instance.createdAt=components.createdAt
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
            print(instance)
            instance.save()
            mod=Module.objects.get(moduleID=module_id)
            courseDet=Course.objects.get(courseID=str(mod.courseID))
            print(courseDet.courseID)
            return redirect('../../instructorCourse/courseID='+str(courseDet.courseID)+'&moduleID='+str(mod.orderNumber)+'/')
    course = Module.objects.get(moduleID=module_id).getCourse()
    components = course.getComponent()
    component = Component.objects.none()
    for c in components:
        if c.moduleID is None:
            component = Component.objects.filter(componentID=c.componentID).union(component)

    form = ImportComponentForm(component)
    return render(request, 'import_component.html', {'componentform': form})

@login_required
def learnerModuleCourseView(request, course_ID, module_ID):
    """
    Only the learner who is the owner of the course can view this page
    """
    learner_ID = request.user.userID
    if request.user.role != 2:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    try:
        lc = LearnerTakesCourse.objects.get(courseID=course_ID, staffID = learner_ID)
    except:
        """
        The learner doesn't take this course
        """
        context= {
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
        

    course = Course.objects.get(courseID = course_ID)
    all_modules = course.getModule()
    all_modules = sorted(all_modules, key=operator.attrgetter('orderNumber'))
    learnerDetails = Learner.objects.get(userID = learner_ID)

    title = Module.objects.none()
    done_Modules=Module.objects.none()
    left_Modules=Module.objects.none()
    curr_Modules=Module.objects.none()

    instructor=Instructor.objects.get(userID = str(course.instructorID))
    currModule=LearnerTakesCourse.objects.get(courseID = course_ID, staffID = learner_ID)
    
    for m in all_modules:
        if(m.orderNumber == currModule.currentModule):
            curr_Modules=Module.objects.get(moduleID = m.moduleID)
    for m in all_modules:
        if(m.orderNumber < int(curr_Modules.orderNumber)):
            done_Modules = Module.objects.filter(moduleID = m.moduleID).union(done_Modules)
    for m in all_modules:
        if(m.orderNumber > int(curr_Modules.orderNumber)):
            left_Modules = Module.objects.filter(moduleID = m.moduleID).union(left_Modules)

    for m in all_modules:
        if(m.orderNumber == int(module_ID)):
            title=Module.objects.get(moduleID = m.moduleID)
    
    components = title.getComponent()
    components = sorted(components, key=operator.attrgetter('orderNumber'))
    done_Modules = sorted(done_Modules, key=operator.attrgetter('orderNumber'))
    left_Modules = sorted(left_Modules, key=operator.attrgetter('orderNumber'))

    template=loader.get_template("ICE/courseContent.html")
    context ={
        'learnerDetails': learnerDetails,
        'all_modules':all_modules,
        'title': title,
        'instructor': instructor,
        'course': course,
        'components': components,
        'left_Modules':left_Modules,
        'done_Modules':done_Modules,
        'currModule':curr_Modules,
        'CM': currModule,
    }
    return HttpResponse(template.render(context,request))


@login_required
def instructorCourseModuleView(request, course_ID, module_ID):
    """
    Only the instructor who is the owner of the course can view this page
    """
    course=Course.objects.get(courseID = course_ID)
    if (request.user.role != 1) or (request.user.userID != course.instructorID.userID):
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_ID = request.user.userID
    course=Course.objects.get(courseID = course_ID)

    all_modules = course.getModule()
    all_modules = sorted(all_modules, key=operator.attrgetter('orderNumber'))

    title = Module.objects.none()

    instructor=Instructor.objects.get(pk = course.instructorID)

    for m in all_modules:
        if(m.orderNumber == int(module_ID)):
            title=Module.objects.get(moduleID = m.moduleID)
    print(title)
    if not title:
        return redirect('../../addModule/courseID=' + course_ID)

    if title.numOfComponents != 0:
            components = title.getComponent()
    else:
        components = Component.objects.none()
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

@login_required
def liveCourseView(request, course_ID):
    if request.user.role != 1:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_ID = request.user.userID
    course=Course.objects.get(courseID = course_ID)

    course.courseStatus = 'L'
    course.save()

    return redirect('../../instructorDashboard/')

@login_required
def category_list_view(request, category_id):
    if request.user.role != 2:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    learner_id = request.user.userID
    all_categories=Category.objects.all()
    all_learnerCourses=LearnerTakesCourse.objects.filter(staffID=learner_id)
    courseList = Course.objects.none()
    if category_id == '0':
        courses=Course.objects.all().exclude(courseStatus = 'U')
        for c in courses:
            flag = True
            for lc in all_learnerCourses:
                if(str(lc.courseID) == str(c.courseID)):
                    flag = False
                    break
            if(flag):
                courseList = Course.objects.filter(courseID = str(c.courseID)).union(courseList)
        learnerDetails=Learner.objects.get(userID=learner_id)
        template=loader.get_template("ICE/category.html")
        context ={
            'all_categories':all_categories,
            'courseList': courseList,
            'categoryCurr': 'All Categories',
            'learnerDetails': learnerDetails,
        }
        return HttpResponse(template.render(context,request))
    courses=Course.objects.filter(categoryID = category_id).exclude(courseStatus = 'U')
    for c in courses:
        flag = True
        for lc in all_learnerCourses:
            if(str(lc.courseID) == str(c.courseID)):
                flag = False
                break
        if(flag):
            courseList = Course.objects.filter(courseID = str(c.courseID)).union(courseList)
    categoryCurr=Category.objects.get(categoryID=category_id)
    learnerDetails=Learner.objects.get(userID=learner_id)
    template=loader.get_template("ICE/category.html")
    context ={
        'all_categories':all_categories,
        'courseList': courseList,
        'categoryCurr': categoryCurr.categoryName,
        'learnerDetails': learnerDetails,
    }
    return HttpResponse(template.render(context,request))

@login_required
def course_learner_view(request):
    if request.user.role != 2:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    learner_ID = request.user.userID
    all_courses=LearnerTakesCourse.objects.filter(staffID = learner_ID).exclude(completeStatus = 'Y')
    courseDetails = Course.objects.none()
    currModules = LearnerTakesCourse.objects.none()
    learnerDetails= Learner.objects.get(userID=learner_ID)
    for c in all_courses:
        courseDetails = Course.objects.filter(courseID = str(c.courseID)).union(courseDetails)
        currModules=LearnerTakesCourse.objects.filter(courseID = str(c.courseID), staffID = learner_ID).union(currModules)

    template=loader.get_template("ICE/learner_dashboard.html")
    context ={
        'all_courses':all_courses,
        'courseDetails':courseDetails,
        'learnerDetails':learnerDetails,
		'currModules':currModules,
    }
    return HttpResponse(template.render(context,request))

def course_history_view(request):
    if request.user.role != 2:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    learner_ID = request.user.userID
    all_courses=LearnerTakesCourse.objects.filter(staffID = learner_ID).exclude(completeStatus = 'N').order_by('completionDate')
    courseDetails = Course.objects.none()
    currModules = LearnerTakesCourse.objects.none()
    learnerDetails= Learner.objects.get(userID=learner_ID)
    for c in all_courses:
        courseDetails = Course.objects.filter(courseID = str(c.courseID)).union(courseDetails)
        currModules=LearnerTakesCourse.objects.filter(courseID = str(c.courseID), staffID = learner_ID).union(currModules)

    template=loader.get_template("ICE/learner_dashboard.html")
    context ={
        'all_courses':all_courses,
        'courseDetails':courseDetails,
        'learnerDetails':learnerDetails,
		'currModules':currModules,
    }
    return HttpResponse(template.render(context,request))

@login_required
def course_instructor_view(request):
    if request.user.role != 1:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_id = request.user.userID
    all_courses=Course.objects.filter(instructorID = instructor_id).exclude(courseStatus = 'U')
    currModules = Module.objects.none()
    learnerDetails= Instructor.objects.get(userID=instructor_id)
    for c in all_courses:
        currModule=Module.objects.filter(courseID = str(c.courseID))
        for c in currModule:
            currModules = Module.objects.filter(moduleID = c.moduleID).union(currModules)
            break

    template=loader.get_template("ICE/instructor_dashboard.html")
    context ={
        'all_courses':all_courses,
        'learnerDetails':learnerDetails,
		'currModules':currModules,
    }
    return HttpResponse(template.render(context,request))

@login_required
def course_development_view(request):
    if request.user.role != 1:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_id = request.user.userID
    all_courses=Course.objects.filter(instructorID = instructor_id).exclude(courseStatus = 'L')
    currModules = Module.objects.none()
    learnerDetails= Instructor.objects.get(userID=instructor_id)
    for c in all_courses:
        currModule=Module.objects.filter(courseID = str(c.courseID))
        for c in currModule:
            currModules = Module.objects.filter(moduleID = c.moduleID).union(currModules)
            break

    template=loader.get_template("ICE/instructor_dashboard.html")
    context ={
        'all_courses':all_courses,
        'learnerDetails':learnerDetails,
		'currModules':currModules,
    }
    return HttpResponse(template.render(context,request))

@login_required
def instructorDetailView(request, course_id):
    if request.user.role != 2:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    learner_id = request.user.userID
    course = Course.objects.get(courseID= course_id)
    instructor = course.getInstructor()
    learnerDetails = Learner.objects.get(userID=learner_id)
    template = loader.get_template("ICE/instructorDetails.html")
    context = {
        'course': course,
        'instructor': instructor,
        'learnerDetails': learnerDetails,
    }
    return HttpResponse(template.render(context, request))

@login_required
def courseDescriptionView(request, course_id):
    if request.user.role != 2:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    learner_id = request.user.userID
    if request.method == 'POST':
        learnerC = LearnerTakesCourse.objects.all()
        for l in learnerC:
            if(str(l.courseID) == str(course_id) and str(l.staffID) == str(learner_id)):
                learnerCourse = LearnerTakesCourse.objects.get(staffID=learner_id, courseID=course_id)
                return redirect('../../learnerCourse/courseID='+course_id+'&moduleID='+str(learnerCourse.currentModule)+'/')
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
        return redirect('../../learnerCourse/courseID='+course_id+'&moduleID=1/')
    learnerDetails = Learner.objects.get(userID=learner_id)
    courseDetails = Course.objects.get(courseID=course_id)
    instructorDetails = Instructor.objects.get(userID=str(courseDetails.instructorID))
    categoryDetails = Category.objects.get(categoryID=str(courseDetails.categoryID))
    template = loader.get_template("ICE/learnerCourseDescription.html")
    learnerC = LearnerTakesCourse.objects.all()
    flag = True
    for l in learnerC:
        if(str(l.courseID) == str(course_id) and str(l.staffID) == str(learner_id)):
            flag = False
    if(flag == False):
        context = {
            'courseDetails': courseDetails,
            'categoryDetails': categoryDetails,
            'instructorDetails': instructorDetails,
            'learnerDetails': learnerDetails,
            'type': 'View Course',
        }
        return HttpResponse(template.render(context, request))
    else:
        context = {
            'courseDetails': courseDetails,
            'categoryDetails': categoryDetails,
            'instructorDetails': instructorDetails,
            'learnerDetails': learnerDetails,
            'type': 'Enroll Course',
        }
        return HttpResponse(template.render(context, request))


"""
FOR AUTHENTICATION
"""
def login_success(request):
    if request.user.role == 1:
        #instructor
        return redirect("course_instructor")
    elif request.user.role == 2:
        #learner
        return redirect("course_learner")
    else:
        return redirect("/")

@login_required
def invite(request):
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            user = Instructor(
                emailID = form.cleaned_data.get('emailID'),
                role = 1,
                is_active = False
            )
            user.save()
            domain = get_current_site(request).domain
            uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
            token = account_activation_token.make_token(user)
            print(domain + '/ICE/signup/' +  uid + '/' + token)

            email = EmailMessage(
                'Sign up for your ICE Account',
                render_to_string('ICE/send_email.html', {
                    'domain': domain,
                    'uid': uid,
                    'token': token,
                }),
                to=[form.cleaned_data.get('emailID')]
            )
            email.send()
            context={
                'message': "Registration invite has been sent to " + user.emailID + "."
            }
            return render(request, 'ICE/message.html', context)
    else:
        form = InviteForm()
    return render(request, 'ICE/signup.html', {'title':'Invite Instructors','form':form})



def signup(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        context = {
            'message': "Activation link is invalid!"
        }
        return render(request, 'ICE/message.html', context)
    
    if user.role == User.INSTRUCTOR:
        SignupForm = SignupFormInstructor
    else:
         SignupForm = SignupFormLearner

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            if account_activation_token.check_token(user, token):
                if user.role == User.INSTRUCTOR:
                    user.userName = form.cleaned_data.get('userName')
                    user.firstName = form.cleaned_data.get('firstName')
                    user.lastName = form.cleaned_data.get('lastName')
                    user.set_password(form.cleaned_data.get('password'))
                    user.biography = form.cleaned_data.get('biography')
                    user.is_staff = False
                    user.is_active = True
                    user.save()
                else:
                    user.userName = form.cleaned_data.get('userName')
                    user.set_password(form.cleaned_data.get('password'))
                    user.is_staff = False
                    user.is_active = True
                    user.save()
                if user.role == User.INSTRUCTOR:
                    instructor = Instructor.objects.get(userID = user.userID)
                    instructor.biography = form.cleaned_data.get('biography')
                    instructor.save()

                login(request, user)
                return redirect('login_success')
            else:
                context = {
                    'message': "Activation link is invalid!"
                }
                return render(request, 'ICE/message.html', context)
    else:
            form = SignupForm()    
    return render(request, 'ICE/signup.html', {'title': "Sign Up", 'form': form})

def learner_get_token(request):
    if request.method == 'POST':
        form = LearnerGetTokenForm(request.POST)
        if form.is_valid():
            staffID = form.cleaned_data.get('staffID')
            try:
                r = requests.get('https://gibice-hrserver.herokuapp.com/info/' + str(staffID), params=request.GET)
                x = r.json()
            except:
                context={
                    'message': "StaffID is invalid! There's no staff record with the staffID you input."
                }
                return render(request, 'ICE/message.html', context)
            staff_firstName = x['first_name']
            staff_lastName = x['last_name']
            staff_emailID = x['email']
            staff = Staff(
            staffID = x['id'],
            firstName = staff_firstName,
            lastName = staff_lastName,
            emailID = staff_emailID
            )
            staff.save()
            user = Learner(
                firstName = staff_firstName,
                lastName = staff_lastName,
                emailID = staff_emailID,
                role = 2,
                is_active = False,
                staff = staff
            )
            user.save()
            domain = get_current_site(request).domain
            uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
            token = account_activation_token.make_token(user)
            print(domain + '/ICE/signup/' +  uid + '/' + token)
            email = EmailMessage(
                'Sign up for your ICE Account',
                render_to_string('ICE/send_email.html', {
                    'domain': domain,
                    'uid': uid,
                    'token': token,
                }),
                to=[staff_emailID]
            )
            email.send()
            context={
                'message': "Registration invite has been sent to " + user.emailID + "."
            }
            return render(request, 'ICE/message.html', context)
    else:
        form = LearnerGetTokenForm()
    return render(request, 'ICE/signup.html', {'title':'Get Learner Token','form':form})