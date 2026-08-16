from django.urls import path
from userauths import views
from django.urls import include
app_name = 'userauths'

urlpatterns = [
    path ("sign-up/",views.register_view,name= "sign-up"),
    path ("login/",views.login_view,name= "login"),
    path ("logout/",views.logout_view,name= "logout"),
    path ("account/", include('allauth.urls')),
]