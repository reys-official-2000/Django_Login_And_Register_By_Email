from django import forms
from .models import UserAccount
import re
import random
import string



class RegisterForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Name'}))
    email = forms.EmailField(max_length=100, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Email'}))
    password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'}))
    repeat_password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Repeat Password'}))
    code_generation = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'Code_generation', 'readonly': 'readonly'}))
    confirm_code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Confirm Code'}))

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['code_generation'].initial = self.generate_code()

    def generate_code(self):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(6))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repeat_password = cleaned_data.get('repeat_password')
        confirm_code = cleaned_data.get('confirm_code')
        generated_code = cleaned_data.get('code_generation')

        if password and repeat_password and password != repeat_password:
            self.add_error(None, 'پسوردها باید مشابه باشند')

        if confirm_code != generated_code:
            self.add_error(None, 'کد کپچا نادرست است. لطفاً دوباره تلاش کنید')

        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get('password')
        super().clean()

        if len(password) < 8:
            raise forms.ValidationError("پسورد باید حداقل 8 کاراکتر باشد")

        if not re.search(r"\d", password):
            raise forms.ValidationError("پسورد باید حداقل یک عدد داشته باشد")

        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("پسورد باید حداقل یک حرف بزرگ داشته باشد")

        if not re.search(r"[a-z]", password):
            raise forms.ValidationError("پسورد باید حداقل یک حرف کوچک داشته باشد")

        if not re.search(r"[!@#$%^&*()_+=-{};:'<>,./?]", password):
            raise forms.ValidationError("پسورد باید حداقل یک کاراکتر خاص داشته باشد")

        return password



class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'}))





class ForgotPasswordForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Email'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            try:
                user = UserAccount.objects.get(email=email)
                if not user.is_active:
                    raise forms.ValidationError('ایمیل وارد شده به حسابی که فعال نیست تعلق دارد ثبت نام خود را تکمیل کنید')
            except UserAccount.DoesNotExist:
                raise forms.ValidationError('هیچ حساب کاربری با این ایمیل وجود ندارد')
        return email


class ConfirmCodeForm(forms.Form):
    code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Code'}))

    def clean_code(self):
        code = self.cleaned_data.get('code')

        if not code.isdigit():
            raise forms.ValidationError('کد باید فقط شامل اعداد باشد')

        if len(code) != 6:
            raise forms.ValidationError('کد باید دقیقاً 6 رقمی باشد')

        return code


class NewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'}))
    repeat_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'}))

    def clean(self):
        cleaned_data = super(NewPasswordForm, self).clean()
        password = cleaned_data.get("password")
        repeat_password = cleaned_data.get("repeat_password")
        if password != repeat_password:
            raise forms.ValidationError('رمز عبور مشابه هم نیستند')
        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get('password')
        super().clean()

        if len(password) < 8:
            raise forms.ValidationError("پسورد باید حداقل 8 کاراکتر باشد")

        if not re.search(r"\d", password):
            raise forms.ValidationError("پسورد باید حداقل یک عدد داشته باشد")

        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("پسورد باید حداقل یک حرف بزرگ داشته باشد")

        if not re.search(r"[a-z]", password):
            raise forms.ValidationError("پسورد باید حداقل یک حرف کوچک داشته باشد")

        if not re.search(r"[!@#$%^&*()_+=-{};:'<>,./?]", password):
            raise forms.ValidationError("پسورد باید حداقل یک کاراکتر خاص داشته باشد")

        return password


class UserPanelForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ['name', 'image']


    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Name'}),
        required=True
    )
    image = forms.ImageField(
        widget=forms.FileInput(attrs={'placeholder': 'Image'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        email = kwargs.pop('email', None)
        super().__init__(*args, **kwargs)
        if email:
            self.fields['email'] = forms.CharField(
                max_length=250,
                initial=email,
                widget=forms.TextInput(attrs={'placeholder': 'Email'}),
                disabled=True
            )
