from django.http import HttpResponse

# Create your views here.
def MonkeyPageView(request):
    return HttpResponse('Kya Bakchodi hai ye Madarchod!')