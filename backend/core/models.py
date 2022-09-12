from unicodedata import category
from django.db import models
from django.db.models import F
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserAccountManager(BaseUserManager):
    def create_user(self, name, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, name, email, password=None):
        user = self.create_user(
            name,
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return self.email


class CardCategory(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING
    )


class CardColor(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING
    )


class CardStatus(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING
    )


class Card(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    creation_date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(
        'CardCategory',
        verbose_name='Card Categories',
        on_delete=models.CASCADE
    )
    status = models.ForeignKey(
        'CardStatus',
        verbose_name='Card Status',
        on_delete=models.CASCADE
    )
    color = models.ForeignKey(
        'CardColor',
        verbose_name='Card Colors',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title
