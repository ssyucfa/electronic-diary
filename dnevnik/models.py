from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.auth.models import Group

from transliterate import get_translit_function

# Create your models here.


translit_ru = get_translit_function('ru')


def gen_slug(text):
    """Генерирует слаг, с русского на англ"""
    return slugify(translit_ru(text, reversed=True))


def gen_slug_for_teacher(first_name, patronymic):
    """Генерирует слаг для учителя"""
    slug = ''
    slug += translit_ru(first_name, reversed=True)
    slug += '-'
    slug += translit_ru(patronymic, reversed=True)

    return slugify(slug)


class Subject(models.Model):
    title = models.CharField('Предмет', max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.title

    # def save(self, *args, **kwargs):
    #     self.slug = gen_slug(self.title)
    #     return super().save(*args, **kwargs)


class ScoreQuerySet(models.QuerySet):

    def avg_score(self):
        return self.aggregate(models.Avg('score'))


class Score(models.Model):
    score = models.PositiveSmallIntegerField('Оценка')
    comment = models.TextField('Комментарий к оценке', blank=True)
    date = models.DateTimeField('Дата оценки')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='scores')
    student = models.ForeignKey('User', on_delete=models.CASCADE, related_name='scores')
    objects = ScoreQuerySet().as_manager()

    def __str__(self) -> str:
        return f"{self.score}-{self.student.first_name}-{self.date.date()}"


class UserQuerySet(models.QuerySet):

    def teachers(self):
        return self.filter(is_teacher=True)

    def students(self):
        return self.filter(is_teacher=False)


class UserManager(UserManager):

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def teachers(self):
        return self.get_queryset().teachers()

    def students(self):
        return self.get_queryset().students()


class User(AbstractUser):
    username = models.CharField(
        blank=True, error_messages={'unique': 'A user with that username already exists.'},
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        max_length=150, unique=True, validators=[UnicodeUsernameValidator()],
        verbose_name='username'
    )
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE, blank=True, null=True)
    last_visit = models.DateTimeField('Последний визит', null=True, blank=True)
    slug = models.SlugField(blank=True)
    objects = UserManager()

    def __str__(self) -> str:
        if self.profile.is_teacher:
            return f"{self.first_name} {self.last_name} {self.profile.patronymic}"
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.password:
            if len(self.password) == 88:
                pass
            else:
                self.password = make_password(self.password)

        if self.profile.is_teacher:
            self.slug = gen_slug_for_teacher(
                self.first_name, self.profile.patronymic
            )

        if not self.username:
            self.username = gen_slug(
                self.last_name
            ) + gen_slug(self.first_name[0]) + gen_slug(
                self.profile.patronymic[0]
            )
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['first_name', 'last_name']


@receiver(post_save, sender=User)
def add_admin_permission(sender, instance, created, **kwargs):
    if created:
        if instance.profile.is_teacher:
            instance.slug = gen_slug_for_teacher(
                instance.first_name, instance.profile.patronymic
            )
        if not instance.username:
            instance.username = gen_slug(
                instance.last_name
            ) + gen_slug(instance.first_name[0]) + gen_slug(
                instance.profile.patronymic[0]
            )
        if instance.password:
            instance.password = make_password(instance.password)


class Profile(models.Model):

    age = models.PositiveSmallIntegerField('Сколько лет', null=True)
    patronymic = models.CharField('Отчество', max_length=100, blank=True)
    is_teacher = models.BooleanField('Учитель?', default=False)


class StudyClass(models.Model):
    name = models.CharField('Название класса', unique=True, max_length=10)
    slug = models.SlugField(unique=True)
    teacher = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, verbose_name='Учитель',
                                   related_name='class_for_teacher')
    students = models.ManyToManyField(User, verbose_name='Ученики', related_name='class_for_student')

    def __str__(self) -> str:
        return self.name

    def count_students(self):
        return self.students.count()

    # def save(self, *args, **kwargs):
    #     self.slug = gen_slug(self.name)
    #     return super().save(*args, **kwargs)
