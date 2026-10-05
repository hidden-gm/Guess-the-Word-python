from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The username is required.')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        PLAYER = 'PLAYER', 'PLAYER'

    # Spring's original app uses usernames as the primary login identity.
    email = None
    first_name = None
    last_name = None
    username = models.CharField(max_length=40, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PLAYER)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class Word(models.Model):
    value = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.value


class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='games')
    word = models.ForeignKey(Word, on_delete=models.PROTECT, related_name='games')
    game_date = models.DateField(db_index=True)
    guesses_used = models.PositiveIntegerField(default=0)
    won = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'game_date'], name='idx_games_user_date')]
        ordering = ['-game_date', '-id']


class Guess(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='guesses')
    value = models.CharField(max_length=5)
    result = models.CharField(max_length=40)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
