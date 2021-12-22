from django.shortcuts import render , redirect
from django.contrib.auth.models import User
from django.contrib import messages
from accounts.models import Profile
from .models import *
import uuid
from django.conf import settings
from django.core.mail import send_mail
#authenticate :  check that whether username and password is correct.
#login : for making user loggin in by providing request and user object as parameter.
from django.contrib.auth import authenticate , login
from django.contrib.auth.decorators import login_required
# Create your views here.

def home(request):
    if request.user.is_authenticated:
        return render(request , 'home.html')
    else:
        return render(request , 'error.html', {'msg':'Your not logged in'})


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

def success(request):
    return render(request , 'success.html')

def token_send(request):
    return render(request , 'token_send.html')

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
            

def error_page(request):
    return render(request , "error.html")

def send_mail_after_registration(email , token):
    subject = "Your account is need to be verified"
    message = f"Hi , \n paster the link to verify your account http://127.0.0.1:8000/verify/{token}" 
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject , message , email_from , recipient_list )
    


