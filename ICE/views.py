from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from django.views.generic.list import ListView
from django.views.generic import View
from django.template import loader

from ICE.models import Module, Category, Component, Course, Instructor, LearnerTakesCourse, Learner, Question, User, Staff
from .forms import ModuleForm,QuizForm, ComponentForm, UserForm, InviteForm, SignupFormInstructor, LearnerGetTokenForm, SignupFormLearner, CourseForm, QuestionForm
import operator

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

@login_required
def learner_quiz(request, q_ID):
    if request.user.role != 2:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    learner_ID = request.user.userID
    if request.method=="POST":
        form=QuestionForm(Question.objects.get(questionID=q_ID),request.POST)
        if form.is_valid():
            choices = form.cleaned_data.get('answers')
            print(choices)
    form=QuestionForm(Question.objects.get(questionID=q_ID))
    return render(request,'quiz_template.html',{'form':form})

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
            return redirect('../../instructorCourse/courseID='+course_id+'&moduleID='+str(instance.moduleID)+'/')
    form=ModuleForm()
    module=Course.objects.filter(courseID=course_id)
    return render(request,'add_module.html',{'moduleform': form, 'course': module})

@login_required
def component_form(request, module_id):
    if request.user.role != 1:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_id = request.user.userID
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
            mod=Module.objects.get(moduleID=module_id)
            courseDet=Course.objects.get(courseID=str(mod.courseID))
            print(courseDet.courseID)
            return redirect('../../instructorCourse/courseID='+str(courseDet.courseID)+'&moduleID='+module_id+'/')
    form = ComponentForm()
    return render(request, 'add_component.html', {'componentform': form})

@login_required
def learnerModuleCourseView(request, course_ID, module_ID):
    if request.user.role != 2:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    learner_ID = request.user.userID
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

@login_required
def instructorCourseModuleView(request, course_ID, module_ID):
    if request.user.role != 1:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_ID = request.user.userID
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
        courses=Course.objects.all()
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
    courses=Course.objects.filter(categoryID = category_id)
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

@login_required
def course_instructor_view(request):
    if request.user.role != 1:
        context={
            'message': "You do not have access to this page."
        }
        return render(request, 'ICE/message.html', context)
    instructor_id = request.user.userID
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

# @admin_required
@login_required
def invite(request):
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            user = Instructor(
                emailID = form.cleaned_data.get('emailID'),
                # username = 'n',
                role = 1,
                is_active = False
            )
            user.save()

            email = EmailMessage(
                'Sign up for your ICE Account',
                render_to_string('ICE/send_email.html', {
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }),
                to=[form.cleaned_data.get('emailID')]
            )

            # subject = "ICE Instructor Registration Token"
            # message = "".format()


            email.send()
            context={
                #'sidebar': access[request.user.role],
                'message': "Registration invite has been sent to " + user.emailID + "."
            }
            return render(request, 'ICE/message.html', context)
    else:
        form = InviteForm()
    return render(request, 'ICE/signup.html', {'title':'Invite Users','form':form})



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
                user.userName = form.cleaned_data.get('userName')
                user.firstName = form.cleaned_data.get('firstName')
                user.lastName = form.cleaned_data.get('lastName')
                user.set_password(form.cleaned_data.get('password'))
                user.biography = form.cleaned_data.get('biography')
                user.is_staff = False
                user.is_active = True
                user.save()

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
                staff = Staff.objects.get(staffID = staffID)
            except:
                context={
                    'message': "StaffID is invalid! There's no staff record with the staffID you input."
                }
                return render(request, 'ICE/message.html', context)
            staff_firstName = staff.firstName
            staff_lastName = staff.lastName
            staff_emailID = staff.emailID
            # staff = Group
            user = Learner(
                emailID = staff_emailID,
                staff = staff,
                firstName = staff_firstName,
                lastName = staff_lastName,
                role = 2,
                is_active = False
            )
            user.save()
            email = EmailMessage(
                'Sign up for your ICE Account',
                render_to_string('ICE/send_email.html', {
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }),
                to=[staff_emailID]
            )
            # subject = "ICE Instructor Registration Token"
            # message = "".format()
            email.send()
            context={
                #'sidebar': access[request.user.role],
                'message': "Registration invite has been sent to " + user.emailID + "."
            }
            return render(request, 'ICE/message.html', context)
    else:
        form = LearnerGetTokenForm()
    return render(request, 'ICE/signup.html', {'title':'Get Learner Token','form':form})