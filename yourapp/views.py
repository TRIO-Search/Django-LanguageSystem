from django.shortcuts import render

def about_view(request):
    return render(request, 'pages/about.html')

def home_view(request):
    return render(request, 'pages/home.html')