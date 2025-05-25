from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Creature(models.Model):
    MYTH_TYPE_CHOICES = [
        ('spirit', 'Дух'),
        ('demon', 'Демон'),
        ('deity', 'Божество'),
        ('creature', 'Міфічна істота'),
        ('other', 'Інше'),
    ]

    name = models.CharField(max_length=100, verbose_name="Назва")
    type = models.CharField(max_length=100, choices=MYTH_TYPE_CHOICES, verbose_name="Тип")
    region = models.CharField(max_length=100, verbose_name="Регіон")
    appearance = models.TextField(verbose_name="Зовнішність")
    behavior = models.TextField(verbose_name="Поведінка")
    role_in_mythology = models.TextField(verbose_name="Роль у міфології")
    symbols = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        null=True,
        verbose_name="Символи"
    )
    description = models.TextField(verbose_name="Взаємодія")
    sources = models.TextField(verbose_name="Джерела")
    image_url = models.URLField(blank=True, null=True, verbose_name="Зображення")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    edited_at = models.DateTimeField(auto_now=True, verbose_name="Змінено")
    image = models.ImageField(upload_to='creature_images/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'creatures'
        verbose_name = "Міфічна істота"
        verbose_name_plural = "Міфічні істоти"
        ordering = ['name']

class CreatureDraft(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор")
    name = models.CharField(max_length=100, verbose_name="Назва")
    type = models.CharField(max_length=100, choices=Creature.MYTH_TYPE_CHOICES, verbose_name="Тип")
    region = models.CharField(max_length=100, verbose_name="Регіон")
    appearance = models.TextField(verbose_name="Зовнішність")
    behavior = models.TextField(verbose_name="Поведінка")
    role_in_mythology = models.TextField(verbose_name="Роль у міфології")
    symbols = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        null=True,
        verbose_name="Символи"
    )
    description = models.TextField(verbose_name="Взаємодія")
    sources = models.TextField(verbose_name="Джерела")
    image_url = models.URLField(blank=True, null=True, verbose_name="Зображення")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подання")
    is_approved = models.BooleanField(default=False, verbose_name="Затверджено")
    admin_comment = models.TextField(blank=True, null=True, verbose_name="Коментар адміна")
    is_rejected = models.BooleanField(default=False, verbose_name="Відхилено")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.creature = None

    def __str__(self):
        return f"{self.name} (чернетка)"

    class Meta:
        verbose_name = "Чернетка істоти"
        verbose_name_plural = "Чернетки істот"


class AdminActionLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Створення'),
        ('edit', 'Редагування'),
        ('approve', 'Затвердження'),
        ('reject', 'Відхилення'),
        ('delete', 'Видалення'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    object_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Лог дій'
        verbose_name_plural = 'Логи дій'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.get_action_display()} {self.object_type} #{self.object_id}"

    def get_action_class(self):
        return {
            'create': 'success',
            'edit': 'primary',
            'approve': 'info',
            'reject': 'warning',
            'delete': 'danger',
        }.get(self.action, 'secondary')

    @classmethod
    def log_admin_action(user, action, obj, details=''):
        AdminActionLog.objects.create(
            user=user,
            action=action,
            object_type=obj.__class__.__name__,
            object_id=obj.id,
            object_name=str(obj),
            details=details
        )


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'creature_role'  # Явно вказуємо ім'я таблиці
        verbose_name = 'Роль'
        verbose_name_plural = 'Ролі'

    def __str__(self):
        return self.name

class User(AbstractUser):
            name = models.CharField(max_length=100)
            surname = models.CharField(max_length=100)
            email = models.EmailField(unique=True)
            profile_picture_url = models.TextField(blank=True, null=True)
            activity = models.IntegerField(default=0)
            role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

            REQUIRED_FIELDS = ['email', 'name', 'surname']

            class Meta:
                db_table = 'creature_user'  # Підтверджуємо існуюче ім'я таблиці
                verbose_name = 'User'
                verbose_name_plural = 'Users'

