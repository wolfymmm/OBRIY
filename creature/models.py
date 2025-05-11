from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

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

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'creatures'
        verbose_name = "Міфічна істота"
        verbose_name_plural = "Міфічні істоти"
        ordering = ['name']


class CreatureHistory(models.Model):
    creature = models.ForeignKey('Creature', on_delete=models.CASCADE,
                                 related_name='history')  # зв'язок з моделлю Creature
    name = models.CharField(max_length=100, verbose_name='Назва')  # Назва істоти
    type = models.CharField(
        choices=[('spirit', 'Дух'), ('demon', 'Демон'), ('deity', 'Божество'), ('creature', 'Міфічна істота'),
                 ('other', 'Інше')],
        max_length=100,
        verbose_name='Тип'
    )  # Тип істоти
    region = models.CharField(max_length=100, verbose_name='Регіон')  # Регіон
    appearance = models.TextField(verbose_name='Зовнішність')  # Зовнішність
    behavior = models.TextField(verbose_name='Поведінка')  # Поведінка
    role_in_mythology = models.TextField(verbose_name='Роль у міфології')  # Роль у міфології
    symbols = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        null=True,
        verbose_name='Символи'
    )  # Символи
    description = models.TextField(verbose_name='Взаємодія')  # Взаємодія
    sources = models.TextField(verbose_name='Джерела')  # Джерела
    image_url = models.URLField(blank=True, null=True, verbose_name='Зображення')  # URL зображення
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено')  # Дата створення
    edited_at = models.DateTimeField(default=timezone.now, verbose_name='Змінено')  # Дата редагування

    def __str__(self):
        return f"{self.creature.name} ({self.edited_at.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        db_table = 'creature_creaturehistory'  # Назва таблиці в базі даних
        verbose_name = 'Історія істоти'
        verbose_name_plural = 'Історії істот'
        ordering = ['-edited_at']  # Сортування за датою редагування (спочатку останні зміни)

class CreatureDraft(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
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

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
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
        self.object_id = None
        self.object_type = None

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

    # Цей метод вже є у всіх моделях Django за замовчуванням для полів з choices
    # def get_action_display(self):
    #     return dict(self.ACTION_CHOICES).get(self.action, self.action)