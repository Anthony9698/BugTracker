from django.shortcuts import render

# Create your views here.


def dashboard(request):
    context = {}
    template = 'dashboard.html'
    return render(request, template, context)


def tickets(request):
    context = {}
    template = 'tickets.html'
    return render(request, template, context)


def projects(request):
    context = {}
    template = 'projects.html'
    return render(request, template, context)