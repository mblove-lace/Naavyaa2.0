from django.shortcuts import render

# from blog.models import Blog

# Create your views here.
def blog(request):
    return render (request,'blog/blog.html')

def care_instructions(request):
    return render(request, 'blog/care_instructions.html')

def faq(request):
    return render(request, 'blog/faq.html')

def contact_us(request):
    return render(request, 'blog/contact_us.html')