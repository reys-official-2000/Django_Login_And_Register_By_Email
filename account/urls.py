from django.urls import path
from . import views


app_name = 'Account'

urlpatterns = [
    path('login/', views.LoginPageView.as_view(), name='Login'),
    path('register/', views.RegisterPageView.as_view(), name='Register'),
    path('logout/', views.LogoutPageView.as_view(), name='LogoUt'),
    path('forgot_password/', views.ForgotPasswordPageView.as_view(), name='ForgotPassword'),
    path('confirm_code/<str:token>', views.VerifyEmailPageView.as_view(), name='VerifyEmail'),
    path('new_password/<str:token>', views.NewPasswordPageView.as_view(), name='NewPassword'),
    path('confirm_registration_code/<str:token>', views.ConfirmRegistrationCodeView.as_view(), name='ConfirmRegistrationCode'),
    path('user_panel/<int:id>', views.UserPanelView.as_view(), name='UserPanel'),
]
