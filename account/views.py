from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views import View
from .forms import LoginForm, ForgotPasswordForm, ConfirmCodeForm, NewPasswordForm, RegisterForm, UserPanelForm
from .models import UserAccount
from .send_email import generate_verification_code, send_verification_email, generate_token, send_registration_email
from django.utils import timezone
from datetime import timedelta



class LoginPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('Home:Home')
        else:
            form = LoginForm()
            return render(request, 'account/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'😊 خیلی خوش آمدید')
                return redirect('Home:Home')
            else:
                messages.error(request, 'ایمیل یا کلمه عبور اشتباه است')
                return render(request, 'account/login.html', {'form': form})
        else:
            return render(request, 'account/login.html', {'form': form})




class LogoutPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, '👋 به امیددیدار خیلی خوش آمدید')
            return redirect('Home:Home')



class ForgotPasswordPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('Home:Home')
        else:
            form = ForgotPasswordForm()
            return render(request, 'account/forgot_password.html', {'form': form})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = UserAccount.objects.filter(email=email).first()
            if user:
                if not user.is_code_valid():
                    verification_code = generate_verification_code()
                    token = generate_token()
                    user.code = verification_code
                    user.token = token
                    user.code_created_at = timezone.now()
                    user.token_created_at = timezone.now()
                    user.save()
                    send_verification_email(email, verification_code, token)
                    messages.success(request, 'ایمیل ارسال شد. ایمیل خود را چک کنید')
                else:
                    messages.info(request, 'یک کد قبلاً برای شما ارسال شده است. لطفاً در مدت زمان ۲ دقیقه صبر کنید')
            else:
                messages.error(request, 'ایمیلی که وارد کرده‌اید اشتباه است')
        else:
            messages.error(request, 'لطفاً ایمیل معتبر وارد کنید')

        form = ForgotPasswordForm()
        return render(request, 'account/forgot_password.html', {'form': form})





class VerifyEmailPageView(View):
    def get(self, request, token):
        if request.user.is_authenticated:
            return redirect('Home:Home')
        else:
            user = UserAccount.objects.filter(token=token).first()
            if user and user.is_token_valid():
                form = ConfirmCodeForm()
                return render(request, 'account/confirm_code.html', {'form': form})
            else:
                messages.info(request, 'این لینک منقضی شده است یا نامعتبر است. لطفاً دوباره تلاش کنید')
                return redirect('Home:Home')

    def post(self, request, token):
        form = ConfirmCodeForm(request.POST)
        user = UserAccount.objects.filter(token=token).first()
        if form.is_valid() and user and user.is_token_valid():
            code = form.cleaned_data['code']
            if user.code == code:
                messages.info(request, 'پسورد جدید را وارد کنید و ذخیره را بزنید')
                return redirect('Account:NewPassword', token=token)
            else:
                form = ConfirmCodeForm()
                messages.error(request, 'کد اشتباه است')
                return render(request, 'account/confirm_code.html', {'form': form})
        else:
            form = ConfirmCodeForm()
            return render(request, 'account/confirm_code.html', {'form': form})

class NewPasswordPageView(View):
    def get(self, request, token):
        if request.user.is_authenticated:
            return redirect('Home:Home')
        else:
            user = UserAccount.objects.filter(token=token).first()
            if user and user.is_token_valid():
                form = NewPasswordForm()
                return render(request, 'account/new_password.html', {'form': form, 'token': token})
            else:
                return redirect('Home:Home')

    def post(self, request, token):
        form = NewPasswordForm(request.POST)
        user = UserAccount.objects.filter(token=token).first()
        if form.is_valid() and user and user.is_token_valid():
            password = form.cleaned_data['password']
            user.set_password(password)
            user.code = ''
            user.token = ''
            user.save()
            messages.success(request, 'رمزعبور شما تغییر کرد')
            return redirect('Account:Login')
        else:
            return render(request, 'account/new_password.html', {'form': form, 'token': token})


class RegisterPageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('Home:Home')
        else:
            form = RegisterForm()
            return render(request, 'account/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user, created = UserAccount.objects.get_or_create(email=email, defaults={'name': name})

            if not created:
                if not user.is_active:
                    user.token = generate_token()
                    user.token_created_at = timezone.now()
                    user.code = generate_verification_code()
                    user.code_created_at = timezone.now()
                    user.save()
                    send_registration_email(email, user.code, user.token)
                    messages.success(request, 'کد تایید جدید به ایمیل شما ارسال شد')
                else:
                    messages.error(request, 'کاربری با این ایمیل قبلاً ثبت ‌نام کرده است و حساب فعال است')
            else:
                user.set_password(password)
                user.token = generate_token()
                user.token_created_at = timezone.now()
                user.code = generate_verification_code()
                user.code_created_at = timezone.now()
                user.save()
                send_registration_email(email, user.code, user.token)
                messages.success(request, 'کد تایید به ایمیل شما ارسال شد')

            form = RegisterForm()
            return render(request, 'account/register.html', {'form': form})
        else:
            return render(request, 'account/register.html', {'form': form})



class ConfirmRegistrationCodeView(View):
    def get(self, request, token):
        user = UserAccount.objects.filter(token=token).first()
        if user and user.is_token_valid():
            form = ConfirmCodeForm()
            return render(request, 'account/confirm_code.html', {'form': form, 'token': token})
        else:
            messages.info(request, 'این لینک منقضی شده است یا نامعتبر است. لطفاً دوباره تلاش کنید')
            return redirect('Home:Home')

    def post(self, request, token):
        user = UserAccount.objects.filter(token=token).first()
        code_input = request.POST.get('code')

        if user and user.is_code_valid():
            if user.code == code_input:
                user.is_active = True
                user.save()
                login(request, user)
                messages.success(request, '😊 ثبت نام شما با موفقیت انجام شد. خوش آمدید')
                return redirect('Home:Home')
            else:
                messages.error(request, 'کد تأیید نادرست است. لطفاً دوباره تلاش کنید')
                return redirect('Account:ConfirmRegistrationCode', token=token)
        else:
            messages.error(request, 'کد تأیید منقضی شده است یا نامعتبر است. لطفاً دوباره تلاش کنید')
            return redirect('Home:Home')


class UserPanelView(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            user = get_object_or_404(UserAccount, id=id)
            form = UserPanelForm(initial={'name': user.name, 'image': user.image}, email=user.email)
            return render(request, 'account/user_panel.html', {'form': form, 'user': user})
        else:
            messages.error(request, 'برای ورود به این صفحه ثبت نام کنید')
            return redirect('Home:Home')

    def post(self, request, id):
        if request.user.is_authenticated:
            user = get_object_or_404(UserAccount, id=id)
            form = UserPanelForm(request.POST, request.FILES, instance=user, email=user.email)
            if form.is_valid():
                form.save()
                messages.success(request, 'پروفایل شما با موفقیت به‌روزرسانی شد')
                return redirect('Account:UserPanel', id=user.id)
            else:
                messages.error(request, 'برخی از فیلدها صحیح نیستند')
        else:
            messages.error(request, 'برای ورود به این صفحه ثبت نام کنید')
            return redirect('Home:Home')

        return render(request, 'account/user_panel.html', {'form': form, 'user': user})




