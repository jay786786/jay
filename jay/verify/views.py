from django.shortcuts import redirect,render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages 
from django.contrib.auth import authenticate,login,logout
from jay import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import *
from .tokens import generate_token
from django.core.mail import EmailMessage,send_mail

print(settings.EMAIL_HOST_USER)
# from .views import 


# Create your views here.

def home(request):
    return render(request,'authentication/index.html')  

def signup(request):
    
    if request.method=='POST':
    
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        
        
        if User.objects.filter(username=username):
            messages.error(request,"Username already exist ! Please try some other username")
            return redirect('home')
        
        if User.objects.filter(email=username):
            messages.error(request,"E-mail already registered")
            return redirect('home')
            
        if len(username)>10:
            messages.error(request,"Username must be under 10 characters")
            
        if pass1 != pass2 :  
            messages.error(request,"Passwords didn't match !")
            
        if not username.isalnum():  
            messages.error(request,"Username must be Alpha-Numric !")
            return redirect('home') 
        
       
            
        my1=User.objects.create_user(username,email,pass1)
        
        my1.first_name=fname
        my1.last_name=lname
        my1.is_active=False
        my1.save()
        messages.success(request,"Your Account successfully created. We sent you aconfirmation email,please confirm your email in order to activate your account")
        
         #Welcome email
        
        subject="Welcome To Jay Login !!"
        message="Hello" +  my1.first_name  +" !! \n" + "Welcome to My page! \nThank you for visited our Website \nWe have also sent you comfirmation email Address in order to activate your account. \n\nThank you \nJay Prajapati" 
        from_email=settings.EMAIL_HOST_USER
        to_list=[my1.email]
        send_mail(subject,message,from_email,to_list,fail_silently=False)
        
        
        # Email Address comfirmation Email
        
        current_site=get_current_site(request)
        email_subject="Confirm your email @ Jay Django Login !!"
        message2=render_to_string('authentication/email_confirmation.html',{
                                    'name':my1.first_name,
                                    'domain':current_site.domain,
                                    'uid':urlsafe_base64_encode(force_bytes(my1.pk)),
                                    'token':generate_token.make_token(my1)
                                   })
        
        email=EmailMessage(
            email_subject,message2,settings.EMAIL_HOST_USER,[my1.email],
        )
        
        email.fail_silently=False
        email.send()
        
        return redirect('signin')
        
    
    return render(request,'authentication/signup.html')
    
    

def signin(request):
    
    if request.method == 'POST':
        
        username=request.POST['username']
        pass1=request.POST['pass1']
        
        user=authenticate(username=username,password=pass1)

        if user is not None:
            login(request,user)
            fname=user.first_name
            return render(request,"authentication/index.html",{'fname':fname})
            
        else:
            messages.error(request,"Bad Credentials !")
            return redirect('home')
    
    
    
    return render(request,'authentication/signin.html')


def signout(request):
    
    logout(request)
    messages.success(request,"Logged out Successfully !")
    
    return redirect('home')

def activate(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        my1=User.objects.get(pk=uid)
    
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        my1=None

    if my1 is not None and generate_token.check_token(my1,token):
        my1.is_active=True
        my1.save()
        login(request,my1)
        return redirect('home')
    
    else:
        
        return render(request,'activation_failed.html')