from django.db import models
from django.contrib.postgres.fields import ArrayField

class Creature(models.Model):
    MYTH_TYPE_CHOICES = [
        ('spirit', 'Дух'),
        ('demon', 'Демон'),
        ('deity', 'Божество'),
        ('creature', 'Міфічна істота'),
        ('other', 'Інше'),
    ]

    name = models.CharField(max_length=100, verbose_name="Назва")
    type = models.CharField(
        max_length=100,
        choices=MYTH_TYPE_CHOICES,
        verbose_name="Тип"
    )
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

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'creatures'  # Вказуємо існуючу назву таблиці
        verbose_name = "Міфічна істота"
        verbose_name_plural = "Міфічні істоти"
        ordering = ['name']