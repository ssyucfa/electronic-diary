from .models import Group


def delete_another_group_for_user_if_has(obj, name_of_group):
    if obj.groups.count() > 1:
        group = Group.objects.get(name=name_of_group)
        group.user_set.remove(obj)
