from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta

class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email=email, name=name, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class UserAccount(AbstractBaseUser):
    image = models.ImageField(upload_to='images/users', blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=200, unique=True, blank=True, null=True)
    code = models.CharField(max_length=6, blank=True, null=True)
    token_created_at = models.DateTimeField(blank=True, null=True)
    code_created_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", ]

    def is_token_valid(self):
        if self.token_created_at:
            return timezone.now() < self.token_created_at + timedelta(minutes=2)
        return False

    def is_code_valid(self):
        if self.code_created_at:
            return timezone.now() < self.code_created_at + timedelta(minutes=2)
        return False

    def generate_token(self):
        pass

    def generate_verification_code(self):
        pass

    def send_verification_email(self):
        pass


    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return f'Email: {self.email} <==========> Name: {self.name}'


