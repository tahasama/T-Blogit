from django import template 
register = template.Library() 

from django.contrib.auth.models import Group


@register.filter(name='is_writer') 
def is_writer(user, group_name):
    group = Group.objects.filter(name='writer')
    if group:
        group = group.first()
        return group in user.groups.all()
    else:
        return False

@register.filter(name='is_reader') 
def is_reader(user, group_name):
    group = Group.objects.filter(name='reader')
    if group:
        group = group.first()
        return group in user.groups.all()
    else:
        return False