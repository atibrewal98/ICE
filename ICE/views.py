from django.shortcuts import render

# Create your views here.
def monkeyPageView(request):
    return render(request, 'monkey.html')