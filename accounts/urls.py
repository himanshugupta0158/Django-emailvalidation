from django.urls import path , include
from .views import *


urlpatterns = [
    path('',home , name="home"),
    path('login_attempt/', login_attempt , name="login_attempt"),
    path('register/', register_attempt , name="register"),
    path('token/' , token_send , name="token"),
    path('success/' , success , name="success"),
    path('verify/<auth_token>' , verify , name="verify"),
    path('error/' , error_page , name="error"),
    
]
