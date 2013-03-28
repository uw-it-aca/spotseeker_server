#   $URL: https://svn-sdg.cites.illinois.edu:4430/Develop/Product/SDGPython/trunk/module/sdg/django/admin.py $
#   $Revision: 29352 $ $Date: 2012-04-23 15:45:00 -0500 (Mon, 23 Apr 2012) $

#   Copyright (c) 2010 by Jon R. Roma and the Board of Trustees of the
#   University of Illinois. All rights reserved.

'''Package of SDG functions used for the Django admin interface.'''

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

import sdg

from sdg import logging

class ExternalUserCreationForm(UserCreationForm):
    '''Class used for user creation form with CITES SDG customizations.'''

    def clean(self):
        '''Override superclass clean() method.'''

        #   Call superclass clean method
        cleaned_data = super(ExternalUserCreationForm, self).clean()

        #   We're not using passwords, so these errors are irrelevant
        if self.errors.has_key('password1'):
            del self.errors['password1']
        if self.errors.has_key('password2'):
            del self.errors['password2']

        return cleaned_data

    def save(self, commit=True):
        '''Override superclass save() method.'''

        #   Get user object from form's superclass
        user = super(UserCreationForm, self).save(commit=False)

        #   Set unusable password
        user.set_unusable_password()

        #   If commit is set, save User model
        if commit:
            user.save()
        return user

class ExternalUserAdmin(UserAdmin):
    '''Class for administration of overridden user creation form.'''

    add_form = ExternalUserCreationForm
    fieldsets = \
        (
            (None, {'fields': ('username', )}),
            (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
            (_('Groups'), {'fields': ('groups',)}),
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )
    list_display = ('username', 'is_superuser', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

#   Unregister base User administrative class and register our custom class
if sdg.VERBOSE:
    logging.debug('registering external user admin interface')

admin.site.unregister(User)
admin.site.register(User, ExternalUserAdmin)
