from django.utils.text import slugify

from .models import Group

from transliterate import get_translit_function


translit_ru = get_translit_function('ru')


def delete_another_group_for_user_if_has(obj, name_of_group):
    """Удаляем ненужную группу,
     если она была случайно добавлена"""
    if obj.groups.count() > 1:
        group = Group.objects.get(name=name_of_group)
        group.user_set.remove(obj)


def gen_slug(text):
    """Генерирует слаг, с русского на англ"""
    return slugify(translit_ru(text, reversed=True))


def gen_slug_in_two_words(first_name, some_word):
    """Генерирует слаг из двух слов, с русского на англ"""
    slug = ''
    slug += translit_ru(first_name, reversed=True)
    slug += '-'
    slug += translit_ru(some_word, reversed=True)

    return slugify(slug)