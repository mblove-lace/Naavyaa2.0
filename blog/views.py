from django.shortcuts import render

# from blog.models import Blog

# Create your views here.
def blog(request):
    return render (request,'blog/blog.html')
