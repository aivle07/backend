from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)


class UserManager(BaseUserManager):
    def create_user(self, email, name,username, agree_terms, agree_marketing, created_at, modified_at,last_password_modified, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username = username,
            email=self.normalize_email(email),
            name = name,
            agree_terms=agree_terms,
            agree_marketing=agree_marketing,
            created_at = created_at,
            modified_at = modified_at,
            last_password_modified = last_password_modified,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name,username,email, agree_terms, agree_marketing,created_at, modified_at,last_password_modified,password):
        user = self.create_user(
            username,
            email,
            name,
            password=password,
            agree_terms=agree_terms,
            agree_marketing=agree_marketing,
            created_at = created_at,
            modified_at = modified_at,
            last_password_modified = last_password_modified,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=20)
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    agree_terms = models.BooleanField(default=False)
    agree_marketing = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    name = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    last_password_modified = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','agree_terms', 'agree_marketing']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin