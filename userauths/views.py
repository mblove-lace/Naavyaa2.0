# ====================================
# IMPORT STATEMENTS
# ====================================

# Importing Django's shortcut functions for rendering templates and redirecting users
# render: Combines HTML template with data to create a webpage
# redirect: Sends user to a different URL/page
from django.shortcuts import render, redirect

# Importing Django's messaging framework for showing notifications to users
# messages: Allows displaying success/error/warning messages that appear once
# Example: messages.success(request, "Welcome!") or messages.error(request, "Invalid login")
from django.contrib import messages

# Importing Django's authentication functions for user login and verification
# login: Logs a user into the system (creates a session)
# authenticate: Verifies user credentials (checks if email/password are correct)
from django.contrib.auth import login, authenticate

# Importing form classes from the userauths app with an alias to avoid naming conflicts
# userauth_forms: Contains form classes like UserRegisterForm, LoginForm, etc.
# These forms handle validation and cleaning of user input data
from userauths import forms as userauth_forms

# Importing model classes from the vendor app
# vendor_models: Contains database models related to vendors (Vendor, VendorProduct, etc.)
# Used to create vendor accounts and manage vendor-related data
from vendor import models as vendor_models

# Importing model classes from the userauths app
# userauth_models: Contains user authentication related models (Profile, User extensions, etc.)
# Used to create user profiles and manage user-related data
from userauths import models as userauth_models


# ====================================
# REGISTER VIEW FUNCTION
# ====================================
# This view handles user registration (sign-up process)
# It creates a new user account and associated profile/vendor account

# WHY NOT USE CLASS BASED VIEWS (CBV)?
# - Function-based views (FBV) are simpler and more explicit for beginners
# - Easier to understand the flow of logic step-by-step
# - CBVs are more abstract and hide logic behind inheritance
# - For complex custom logic (like this registration), FBVs are often clearer
# - You CAN use CBVs, but FBVs are perfectly fine and often preferred for custom workflows

def register_view(request):
    # request: Django's HTTP request object containing information about the user's request
    # - request.method: GET or POST
    # - request.user: The current user (logged in or anonymous)
    # - request.POST: Form data submitted by the user
    # - request.GET: URL parameters
    
    # ====================================
    # STEP 1: CHECK IF USER IS ALREADY LOGGED IN
    # ====================================
    # request.user: The currently authenticated user object
    # .is_authenticated: Boolean property that returns True if user is logged in, False if anonymous
    # Why check? Prevent logged-in users from creating another account
    if request.user.is_authenticated:
        
        
        # messages.warning(): Displays a warning message to the user
        # request: Needed to attach the message to this specific request/session
        # "You are already logged in.": The message text that will be displayed
        # This message will appear on the next page the user visits
        messages.warning(request, "You are already logged in.")
        
        # redirect("/"): Sends the user to the homepage
        # "/": The root URL of the website
        # return: Exits the function early and sends this redirect response
        # User sees the warning message on the homepage
        return redirect("/")

    # ====================================
    # STEP 2: CREATE THE REGISTRATION FORM
    # ====================================
    # userauth_forms.UserRegisterForm: A Django form class for user registration
    # It contains fields like email, password, full_name, mobile, user_type, etc.
    
    # (request.POST or None): Python's "or" logic for form data
    # - If request.method == "POST": request.POST contains form data → form is bound with data
    # - If request.method == "GET": request.POST is empty → None is used → form is unbound (empty)
    # Why? On GET request (initial page load), show empty form
    #      On POST request (form submission), bind form with submitted data for validation
    
    # form: The form object that will either be empty (GET) or filled with user data (POST)
    form = userauth_forms.UserRegisterForm(request.POST or None)

    # ====================================
    # STEP 3: VALIDATE FORM SUBMISSION
    # ====================================
    # form.is_valid(): Checks if all form data is correct and complete
    # Returns True if:
    # - All required fields are filled
    # - Email format is correct
    # - Password meets requirements
    # - No validation errors occurred
    # Returns False if any validation fails
    # Only runs when request.method == "POST" (form was submitted)
    if form.is_valid():
        
        # ====================================
        # STEP 4: SAVE THE USER TO DATABASE
        # ====================================
        # form.save(): Creates a new User object and saves it to the database
        # This method is provided by Django's ModelForm
        # It takes all the validated form data and creates a database record
        # user: The newly created User object (with id, email, password hash, etc.)
        user = form.save()

        # ====================================
        # STEP 5: EXTRACT CLEANED FORM DATA
        # ====================================
        # form.cleaned_data: A dictionary containing validated and cleaned form data
        # After is_valid() runs, Django processes the raw input and stores it here
        # Example: {"full_name": "John Doe", "email": "john@example.com", ...}
        
        # .get("full_name"): Safely retrieves the full_name value from the dictionary
        # Why .get()? Returns None if key doesn't exist instead of raising an error
        # full_name: Variable storing the user's full name (e.g., "Jane Smith")
        full_name = form.cleaned_data.get("full_name")
        
        # email: Variable storing the user's email address (e.g., "jane@example.com")
        email = form.cleaned_data.get("email")
        
        # mobile: Variable storing the user's phone number (e.g., "1234567890")
        mobile = form.cleaned_data.get("mobile")
        
        # password: Variable storing the user's chosen password (plain text at this point)
        # Note: This is used for immediate authentication; the User object already has the hashed version
        password = form.cleaned_data.get("password")
        
        # user_type: Variable storing whether user wants to be a "vendor" or "customer"
        # This determines what kind of account and permissions the user gets
        user_type = form.cleaned_data.get("user_type")

        # ====================================
        # STEP 6: AUTHENTICATE THE NEW USER
        # ====================================
        # authenticate(): Verifies the user's credentials against the database
        # email=email: The email address to check
        # password=password: The password to verify (Django compares against hashed password)
        # Returns: The User object if credentials are valid, None if invalid
        # Why authenticate immediately after saving? To verify the save was successful
        # user: Variable now contains the authenticated User object (reassigned from form.save())
        user = authenticate(email=email, password=password)
        
        # login(): Logs the user into the system (creates a session)
        # request: Needed to create the session and attach it to this request
        # user: The authenticated User object to log in
        # This sets request.user to the logged-in user and creates session cookies
        # After this line, the user is officially logged in
        login(request, user)

        # ====================================
        # STEP 7: SHOW SUCCESS MESSAGE
        # ====================================
        # messages.success(): Displays a success notification to the user
        # request: Attaches message to this request's session
        # f-string: Allows embedding the {full_name} variable in the message
        # Example: "Account created successfully! Welcome, Jane Smith."
        # This message will appear on the next page the user sees
        messages.success(request, f"Account created successfully! Welcome, {full_name}.")
        
        # ====================================
        # STEP 8: CREATE USER PROFILE
        # ====================================
        # userauth_models.Profile: The Profile model from your userauths app
        # .objects.create(): Creates and saves a new Profile record in one step
        # This is a shortcut for Profile() + .save()
        
        # profile: Variable storing the newly created Profile object
        profile = userauth_models.Profile.objects.create(
            # full_name=full_name: Sets the profile's full_name field
            full_name=full_name,
            
            # user=user: Links this profile to the User account (ForeignKey relationship)
            # This creates a one-to-one connection between User and Profile
            user=user,
            
            # mobile=mobile: Sets the profile's mobile phone number
            mobile=mobile,
        )
        # After this line, the Profile record exists in the database
        
        # ====================================
        # STEP 9: CREATE VENDOR ACCOUNT IF NEEDED
        # ====================================
        # Checking if the user chose to register as a vendor
        # user_type == "vendor": String comparison (case-sensitive)
        if user_type == "vendor":
            # User wants to be a vendor, so create a Vendor account
            
            # vendor_models.Vendor: The Vendor model from your vendor app
            # .objects.create(): Creates and saves a new Vendor record
            vendor_models.Vendor.objects.create(
                # user=user: Links the Vendor account to the User account (OneToOne relationship)
                # Each User can have at most one Vendor account
                user=user,
                
                # store_name=full_name + "'s Store": Creates a default store name
                # Example: If full_name is "Jane Smith", store_name becomes "Jane Smith's Store"
                # + "'s Store": String concatenation to add the suffix
                store_name=full_name + "'s Store"
            )
            # Now this user has both a User account AND a Vendor account
            
            # profile.user_Type: Setting the user type on the profile
            # "Vendor": Marks this profile as belonging to a vendor
            # Note: This field can be used for permissions, display logic, etc.
            profile.user_Type = "Vendor"
        else:
            # User did NOT choose vendor, so they're a regular customer
            
            # profile.user_Type: Setting the user type on the profile
            # "Customer": Marks this profile as belonging to a customer
            profile.user_Type = "Customer"

        # ====================================
        # STEP 10: SAVE THE UPDATED PROFILE
        # ====================================
        # profile.save(): Saves the changes we made to the profile (user_Type field)
        # We modified profile.user_Type above, but those changes are only in memory
        # This line commits the changes to the database
        profile.save()

        # ====================================
        # STEP 11: REDIRECT TO NEXT PAGE
        # ====================================
        # request.GET.get("next", "store:index"): Gets the "next" URL parameter
        # - request.GET: Dictionary of URL parameters (everything after ? in URL)
        # - .get("next", ...): Gets the "next" parameter if it exists
        # - "store:index": Default value if "next" doesn't exist
        # 
        # Why "next"? If user tried to access a page requiring login, they were redirected to signup
        # Example URL: /signup/?next=/cart/
        # After signup, send them to the page they originally wanted (/cart/)
        # If no "next" parameter, send them to the homepage (store:index)
        #
        # next_url: Variable storing where to send the user after successful registration
        next_url = request.GET.get("next", "store:index")
        
        # redirect(next_url): Sends the user to the URL stored in next_url
        # return: Exits the function and sends this redirect response
        # User is now logged in and redirected to their intended destination
        return redirect(next_url)
    
    # ====================================
    # STEP 12: RENDER THE FORM (GET REQUEST OR INVALID FORM)
    # ====================================
    # If we reach this line, either:
    # 1. request.method == "GET" (user just opened the page) → form is empty
    # 2. form.is_valid() returned False (user submitted invalid data) → form has errors
    
    # context: Dictionary containing data to pass to the template
    # This makes the 'form' object available in the HTML template
    context = {
        # "form": The key used in the template (e.g., {{ form.as_p }})
        # form: The UserRegisterForm object (either empty or with errors)
        "form": form,   
    }
    
    # render(): Combines the template with the context data
    # request: The HTTP request object (always required)
    # "userauths/sign-up.html": Path to the HTML template file
    # context: The data dictionary containing the form
    # 
    # Returns: An HttpResponse with the rendered HTML page
    # User sees the registration form (empty or with validation errors highlighted)
    return render(request, "userauths/sign-up.html", context)


# ====================================
# FLOW SUMMARY
# ====================================
# 1. User visits /register/ → GET request → Empty form displayed
# 2. User fills form and clicks submit → POST request
# 3. Check if already logged in → redirect if yes
# 4. Validate form data → if invalid, show errors
# 5. If valid:
#    a. Create User account in database
#    b. Authenticate and log in the user
#    c. Show success message
#    d. Create Profile for user
#    e. Create Vendor account if user_type == "vendor"
#    f. Set user_Type on profile
#    g. Save profile
#    h. Redirect to intended page or homepage



def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("/")
    
    if request.method == "POST":
        form = userauth_forms.LoginForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            captcha_verified = form.cleaned_data.get("captcha", False)

            if captcha_verified:
                try:
                    user_instance = userauth_models.User.objects.get(email=email,is_active=True)
                    user_authenticate = authenticate(request, email=email, password=password)

                    if user_instance is not None:
                        login(request, user_authenticate)
                        messages.success(request, f"Welcome back, {user_instance.profile.full_name}!")
                        next_url = request.GET.get("next", "store:index")
                        return redirect(next_url)
                    else:
                        messages.error(request, "Invalid email or password.")


                except:
                    messages.error(request, "No active account found with this email.")
            else:
                messages.error(request, "Captcha verification failed. Please try again.")
    else:
        form = userauth_forms.LoginForm()
    
    context = {
        "form": form,
    }
    return render(request, "userauths/login.html", context)