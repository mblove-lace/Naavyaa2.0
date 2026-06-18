from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
    

    path('', views.blog, name='blog'),
    # path('care-instructions/', views.care_instructions, name='care_instructions'),
    path('faqs/', views.faq, name='faqs'),
    path('contact-us/', views.contact_us, name='contact_us'),
]