from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from django.views.generic.list import ListView
from django.views.generic import View
from django.template import loader
from ICE.models import Module, Category, Component, Course, Instructor, LearnerTakesCourse, Learner, Question, User, Staff
from .forms import ModuleForm,QuizForm, ComponentForm, UserForm, InviteForm, SignupFormInstructor, LearnerGetTokenForm, SignupFormLearner  #SomeForm
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

def module_form(request,instructor_id,course_id):
	if request.method=='POST':
		form = ModuleForm(request.POST)
		if form.is_valid():
			instance=form.save(commit=False)
			course=Course.objects.get(courseID=course_id)
			instance.courseID=course
			instance.save()
			return redirect('../../instructorCourse/instructorID='+instructor_id+'&courseID='+course_id+'&moduleID=1/')
	form=ModuleForm()
	module=Course.objects.filter(courseID=course_id)
	return render(request,'form.html',{'form': form, 'course': module})

def component_form(request,instructor_id,module_id):

    if request.method == 'POST':
        form = ComponentForm(request.POST,request.FILES)
        if form.is_valid():
            instance=form.save(commit=False)
            module=Module.objects.get(moduleID=module_id)
            instance.moduleID=module
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

def instructorCourseModuleView(request, instructor_ID,course_ID, module_ID):
    all_modules=Module.objects.filter(courseID = course_ID)
    course=Course.objects.get(courseID = course_ID)
    instructor = ''
    title = ''
    components = ''
    instructor=Instructor.objects.get(pk = course.instructorID)
    title=Module.objects.get(moduleID = module_ID)
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

def course_learner_view(request, learner_ID):
    all_courses=LearnerTakesCourse.objects.filter(staffID = learner_ID)
    courseDetails = Course.objects.none()
    currModules = LearnerTakesCourse.objects.none()
    #learnerDetails= Learner.objects.filter(userID=learner_ID)
    learnerDetails= Learner.objects.get(userID=learner_ID)
    for c in all_courses:
        # print(c.courseID)
        courseDetails = Course.objects.filter(courseID = str(c.courseID)).union(courseDetails)
        currModules=LearnerTakesCourse.objects.filter(courseID = str(c.courseID), staffID = learner_ID).union(currModules)
        # print(currModules)

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
    #learnerDetails= Learner.objects.filter(userID=learner_ID)
    learnerDetails= Instructor.objects.get(userID=instructor_id)
    for c in all_courses:
        # print(c.courseID)
        currModule=Module.objects.filter(courseID = str(c.courseID))
        for c in currModule:
            currModules = Module.objects.filter(moduleID = c.moduleID).union(currModules)
            break
        # print(currModules)

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

"""
FOR AUTHENTICATION
"""
def login_success(request):
    if request.user.role == 1:
        #instructor
        return redirect("course_instructor", instructor_id = request.user.userID)
    elif request.user.role == 2:
        #learner
        return redirect("course_learner", learner_ID = request.user.userID)
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