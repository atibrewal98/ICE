from django.shortcuts import render

# Create your views here.
def MonkeyPageView(request):
    return render(request, 'monkey.html')