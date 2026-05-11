# Taking and copying the whole URL  from the store/urls_store.py file and modifying it for the customer app.
# Import the path function from Django's URL routing system
# Import the path function from Django's URL routing system
# This is used to define URL patterns
from django.urls import path

# Import the views module from your 'customer' app
# This gives access to all view functions defined in customer/views.py
from customer import views

# Set the application namespace to 'customer'
# This allows you to reference URLs as 'customer:index' or 'customer:dashboard'
# when using reverse() or {% url %} template tags
app_name = "customer"


# Define the list of URL patterns for this app
urlpatterns = [
      # Route: "" (empty string = root URL or base /starting point of a URL path of this app)
      
    # View: calls views.index function when this URL is accessed
    # Name: 'index' - used for reverse URL lookups
    # Full URL reference: 'customer:index'
    # Even though it says we go to customer dashboardf, but  we have to go through the base .html file and click on the dashboard link to access this URL.
    path("dashboard/", views.dashboard, name='dashboard'),

    path ("order/<str:order_id>/", views.order_detail, name='order_detail'),

]
