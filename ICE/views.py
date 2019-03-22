from django.shortcuts import render, HttpResponse
from django.views.generic.list import ListView
from django.template import loader
from ICE.models import Module, Category, Component

# Create your views here.
def monkeyPageView(request):
    return render(request, 'ICE/monkey.html')

def courseView(request):
    return render(request, 'ICE/courseContent.html')

def category_list_view(request):
    all_categories=Category.objects.all()
    template=loader.get_template("ICE/category.html")
    context ={
        'all_categories':all_categories,
    }
    return HttpResponse(template.render(context,request))

def module_list_view(request):
    all_modules=Module.objects.all()
    template=loader.get_template("ICE/module_List1.html")
    context ={
        'all_modules':all_modules,
    }
    return HttpResponse(template.render(context,request))

def component_list_view(request, module_ID):
    all_components=Component.objects.filter(moduleID = module_ID)
    template=loader.get_template("ICE/component_List1.html")
    context ={
        'all_components':all_components,
    }
    return HttpResponse(template.render(context,request))

class ModuleViewAll(ListView):
    model = Module

class ModuleViewComponents(ListView):
    def get_queryset(self):
        self.module = self.kwargs['module']
        return Component.objects.filter(module__pk = self.module).all()

    def get_context_data(self, **kwargs):
        self.module = self.kwargs['module']
        context = super().get_context_data(**kwargs)
        context['module'] = Component.objects.get(pk = self.module)
        return context