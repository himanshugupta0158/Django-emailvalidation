from django.shortcuts import render , redirect
from django.contrib.auth.models import User
from django.contrib import messages
from accounts.models import Profile
import uuid
from django.conf import settings
from django.core.mail import send_mail
#authenticate :  check that whether username and password is correct.
#login : for making user loggin in by providing request and user object as parameter.
from django.contrib.auth import authenticate , login
from django.contrib.auth.decorators import login_required
import random
# Create your views here.

# Home page which cannot be accessed by unauthorized user.
def home(request):
    if request.user.is_authenticated:
        return render(request , 'home.html')
    else:
        return render(request , 'error.html', {'msg':'Your not logged in'})

# for logging in by registered user
def login_attempt(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = username).first()
        if user_obj is None:
            messages.success(request, "User not found !")
            return redirect('/login')
        
        profile_obj = Profile.objects.filter(user=user_obj).first()
        
        if not profile_obj.is_verified :
            messages.success(request, "User is not verified check your mail.")
            return redirect('/login')
        user = authenticate(username=username , password=password)
        if user is None :
            messages.success(request, "Wrong password.")
            return redirect('/login')
        
        login(request , user)
        return redirect('/')
    return render(request , 'login.html')

# for registering(storing) of user data in db
def register_attempt(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(password)
        
        try:
            if User.objects.filter(username=username).first() :
                messages.success(request, "Username is already taken!")
                return redirect('/register')
            if User.objects.filter(email=email).first() :
                messages.success(request, "Email is already taken!")
                return redirect('/register')
            user_obj = User(username=username,email=email)
            user_obj.set_password(password)
            user_obj.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user=user_obj ,auth_token=auth_token)
            profile_obj.save()
            send_mail_after_registration(email , auth_token)
            return redirect('/token')
        except Exception as e:
            print(e)
        
    return render(request , 'register.html')

# success page
def success(request):
    return render(request , 'success.html')

# token page
def token_send(request):
    return render(request , 'token_send.html')

# verifying token
def verify(request , auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()
        if profile_obj :
            if profile_obj.is_verified :
                messages.success(request, "Your account have already verified.")
                return redirect('/login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, "Your account have been verified.")
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e :
        print(e)
            
# Error page
def error_page(request):
    return render(request , "error.html")

# sending mail to user mail for verifying token after this user will be able to login
def send_mail_after_registration(email , token):
    subject = "Your account is need to be verified"
    message = f"Hi , \n paster the link to verify your account http://127.0.0.1:8000/verify/{token}" 
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject , message , email_from , recipient_list )

# resetting forgotten password via OTP valid till user does not user it.
def forgotten_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        request.session['email'] = email
        if user :
            send_OTP(request , email)
            messages.success(request, "OTP has been sent to your mail.")
            return render(request , "forgotten_password.html" , {"verify" : True})
        else:
            messages.success(request, "User with this email does not exist.")
            return render(request , 'forgotten_password.html')
    return render(request , 'forgotten_password.html')

# sending OTP to user's mail 
def send_OTP(request , email):
    otp = int(random.randint(10000,99999))
    request.session['OTP'] = otp
    subject = "Your password reset OTP"
    message = f"Hi , \n Your OTP for password reset :\n{otp} " 
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject , message , email_from , recipient_list )

# to verify token is correct or received by authentic user.
def verify_OTP(request):
    print("Inside verify OTP")
    if request.method == "POST":
        password = request.POST.get("password")
        otp = request.POST.get("OTP")
        if int(otp) == int(request.session['OTP']) :
            user = User.objects.filter(email = request.session['email']).first()
            user.set_password(password)
            request.session.flush()
            messages.success(request, "Password changed successfully.")
            return redirect('/login_attempt')
        else:
            messages.success(request, "OTP does not match.")
            return render(request , "verify_otp.html")
    return render(request , 'verify_otp.html')
        
    

    

