from django.shortcuts import render

def index(request):
    return render(request, "home.html")

def privateView(request):
    return render(request, "private/private.html")

def privateView2(request):
    return render(request, "private/private2.html")