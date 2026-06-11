"""
URL configuration for Naavyaa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 


# urlpatters is a Python list that Django expects to exist in every urls.py file. So that, When a user visits a specific URL, send them to this handler.

urlpatterns = [
    # “When the user goes to https://naavyaa.com/admin/, show them the Django admin site.” Here, path() is a function that takes at least two arguments: a route (string) (here,admin/) and a view (callable).
    # Inside Django, admin.site is actually an instance of the class AdminSite.
    # The site instance has a urls property that returns the URL patterns for the admin site.
    path('admin/', admin.site.urls),
    # This tells Django:  “If the URL doesn’t start with /admin/ or /ckeditor5/, check inside the file store/urls_store.py for more URL patterns.”
    path('', include('store.urls_store')),
# This line tells Django: “If the URL starts with /user/, check inside the file userauths/urls_userauth.py for more URL patterns related to user authentication (like login, registration, etc.).”
    path('user/', include('userauths.urls_userauth')),
# This line tells Django: “If the URL starts with /customer/, check inside the file customer/urls_customer.py for more URL patterns related to customer-specific views (like the dashboard).”
    path('customer/', include('customer.urls_customer', namespace='customer')),

    path('blog/', include('blog.urls')),
    # This line connects your project with a third-party app called django-ckeditor-5
    # It provides URLs that handle uploading, browsing, and managing images/files for your text editor in the admin panel.
    path("ckeditor5/", include("django_ckeditor_5.urls")),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
