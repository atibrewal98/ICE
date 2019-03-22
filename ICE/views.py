from django.shortcuts import render

# Create your views here.
def monkeyPageView(request):
    return render(request, 'ICE/monkey.html')

def courseView(request):
    return render(request, 'ICE/courseContent.html')