from django.contrib import admin

# Register your models here.
# userauths is the name of a Django app in your project.
# models is a module inside that app — specifically, userauths/models.py.

# The line from userauths import models imports the entire models module, meaning you’d have to access models like this:
# models.User
# models.Profile
from userauths import models

admin.site.register(models.User)
admin.site.register(models.Profile)
# Why Register Models with admin.site.register()?
# You can add/edit/delete records for those models via the Django admin panel.

# Useful during development and debugging.

# Saves time—you don’t need to build custom forms or write raw queries.
# no extra