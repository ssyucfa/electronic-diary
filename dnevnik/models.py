from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth.models import Group

from . import service


class Subject(models.Model):
    """Модель предмета"""
    title = models.CharField('Предмет', max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.title

    # def save(self, *args, **kwargs):
    #     self.slug = gen_slug(self.title)
    #     return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('subject', kwargs={'subject_slug': self.slug})


class Score(models.Model):
    """Модель оценки"""
    score = models.PositiveSmallIntegerField('Оценка')
    comment = models.TextField('Комментарий к оценке', blank=True)
    date = models.DateTimeField('Дата оценки', auto_now_add=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='scores')
    student = models.ForeignKey('User', on_delete=models.CASCADE, related_name='scores')

    def __str__(self) -> str:
        return f"{self.score}-{self.student.first_name}-{self.date.date()}"


class UserQuerySet(models.QuerySet):
    """QuerySet пользователя"""

    def teachers(self):
        return self.filter(profile__is_teacher=True)

    def students(self):
        return self.filter(profile__is_teacher=False)


class UserManager(UserManager):
    """Менеджер пользователя"""

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def teachers(self):
        return self.get_queryset().teachers()

    def students(self):
        return self.get_queryset().students()


class User(AbstractUser):
    """Модель пользователя"""
    username = models.CharField(
        blank=True,
        error_messages={
            'unique': 'A user with that username already exists.'
        },
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name='username'
    )
    profile = models.OneToOneField('Profile',
                                   on_delete=models.CASCADE,
                                   blank=True,
                                   null=True
                                   )
    last_visit = models.DateTimeField('Последний визит',
                                      null=True,
                                      blank=True
                                      )
    slug = models.SlugField(unique=True)
    is_in_class = models.BooleanField(default=False)
    objects = UserManager()

    def __str__(self) -> str:
        """Устанавливаем отображение User,
         если учитель, то ФИО,
          а если ученик, фамилия и имя"""
        if self.profile.is_teacher:
            return f"{self.first_name} {self.last_name} {self.profile.patronymic}"
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        self.__make_password()
        self.__gen_slug()
        self.__make_username()

        return super().save(*args, **kwargs)

    def __gen_slug(self):
        """Делаем слаг для пользователя,
         если учитель, то отчество и имя,
        если ученик, то имя и фамилия"""
        if self.profile.is_teacher:
            self.slug = service.gen_slug_in_two_words(
                self.first_name, self.profile.patronymic
            )
        else:
            self.slug = service.gen_slug_in_two_words(
                self.first_name,
                self.last_name
            )

    def __make_password(self):
        """Хешируем пароль, хеш пароля всегда 88 символов,
         и мы будем устанавливать хеш,
          всегда когда у пользователя пароль меньше или больше"""
        if self.password:
            if len(self.password) == 88:
                pass
            else:
                self.password = make_password(self.password)

    def __make_username(self):
        """Если у пользователя нет username, то устанавливаем его"""
        if not self.username:
            self.username = service.gen_slug(
                self.last_name
            ) + service.gen_slug(
                self.first_name[0]
            ) + service.gen_slug(
                self.profile.patronymic[0]
            )

    @staticmethod
    def _create_data(count=20, locale='ru'):
        """Создаем фиктивные данные,
         чтобы самому ничего не создавать"""
        from mimesis import Person
        from random import choice

        person = Person(locale)

        for _ in range(count):
            profile = Profile.objects.create(age=person.age(),
                                             patronymic=person.surname(),
                                             is_teacher=choice([
                                                 True, False
                                             ]))
            user = User(email=person.email(),
                        username=person.username(),
                        first_name=person.first_name(),
                        last_name=person.last_name(),
                        password=person.password(),
                        profile=profile,
                        )
            user.save()
            user.groups.add(
                Group.objects.get(name='Teacher')
                if user.profile.is_teacher else
                Group.objects.get(name='Student')
            )

    def get_absolute_url(self):
        return reverse('student', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['first_name', 'last_name']


# @receiver(post_save, sender=User)
# def add_admin_permission(sender, instance, created, **kwargs):
#     if created:
#         if instance.profile.is_teacher:
#             instance.slug = gen_slug_in_two_words(
#                 instance.first_name, instance.profile.patronymic
#             )
#         if not instance.username:
#             instance.username = gen_slug(
#                 instance.last_name
#             ) + gen_slug(instance.first_name[0]) + gen_slug(
#                 instance.profile.patronymic[0]
#             )
#         if instance.password:
#             instance.password = make_password(instance.password)


class Profile(models.Model):
    """Модель профиля для пользователя"""
    age = models.PositiveSmallIntegerField(
        'Сколько лет',
        null=True
    )
    patronymic = models.CharField(
        'Отчество',
        max_length=100,
        blank=True
    )
    is_teacher = models.BooleanField('Учитель?', default=False)


class StudyClass(models.Model):
    name = models.CharField(
        'Название класса',
        unique=True,
        max_length=10)
    slug = models.SlugField(unique=True)
    teacher = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Учитель',
        related_name='class_for_teacher'
    )
    students = models.ManyToManyField(
        User,
        verbose_name='Ученики',
        related_name='class_for_student'
    )

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse('class', kwargs={'pk': self.pk})

    # def save(self, *args, **kwargs):
    #     self.students.is_in_class = True
    #     self.teacher.is_in_class = True
    #     return super().save(*args, **kwargs)


@receiver(post_save, sender=StudyClass)
def update_in_class_for_persons(sender, instance, **kwargs):
    """Сигнал для учебного класса,
     когда пользователь будет ставится в класс,
      то его полю is_in_class будет ставится True"""
    class_ = StudyClass.objects.prefetch_related('students').get(name=instance)
    for student in class_.students.all():
        student.is_in_class = True
        student.save()
    class_.teacher.is_in_class = True
    class_.teacher.save()
