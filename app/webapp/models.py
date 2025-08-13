from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Create your models here.


User = get_user_model()

STATUS_CHOICES = [
    ('available', 'Доступна'),
    ('rented', 'В аренде'),
    ('sold', 'Продана'),
]


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')


class Book(models.Model):
    avatar = models.ImageField(
        upload_to='books/images/',
        null=True,
        blank=True,
        verbose_name='Обложка книги'
    )
    title = models.CharField(max_length=100, verbose_name='Название книги')
    author_name = models.CharField(max_length=100, verbose_name='Автор книги')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Добавил')
    category = models.CharField(max_length=50, verbose_name='Категория')
    year = models.PositiveIntegerField(verbose_name='Год написания')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    STATUS_CHOICES = [
        ('available', 'Доступна'),
        ('rented', 'В аренде'),
        ('sold', 'Продана'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    users_favorites = models.ManyToManyField(
        User,
        through='webapp.Favorite',
        related_name='favorite_books',
        blank=True,
    )

    @property
    def is_available(self):
        return not self.rental_set.filter(end_date__gt=timezone.now()).exists()

    def __str__(self):
        return f"{self.title} ({self.author_name})"


class Rental(models.Model):
    RENTAL_CHOICES = [
        ('2weeks', '2 недели'),
        ('1month', '1 месяц'),
        ('3months', '3 месяца'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rental_period = models.CharField(choices=RENTAL_CHOICES, max_length=10)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)  # чтобы start_date был

        if not self.end_date:
            if self.rental_period == '2weeks':
                self.end_date = self.start_date + timedelta(weeks=2)
            elif self.rental_period == '1month':
                self.end_date = self.start_date + timedelta(days=30)
            elif self.rental_period == '3months':
                self.end_date = self.start_date + timedelta(days=90)

        now = timezone.now()
        self.is_active = self.end_date > now

        super().save(*args, **kwargs)

        # Обновляем статус книги
        book = self.book
        if self.is_active:
            book.status = 'rented'
        else:
            # Если нет других активных аренд, возвращаем статус доступна
            active_rentals = book.rental_set.filter(is_active=True).exclude(pk=self.pk).exists()
            if not active_rentals and book.status != 'sold':
                book.status = 'available'
        book.save()

    def __str__(self):
        return f"{self.user} арендует '{self.book.title}' на {self.get_rental_period_display()}"
