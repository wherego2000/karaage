# Copyright 2007-2010 VPAC
#
# This file is part of Karaage.
#
# Karaage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Karaage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Karaage  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

import datetime
from andsome.middleware.threadlocals import get_current_user

from karaage.util.helpers import create_password_hash 
from karaage.people.models import Person
from karaage.machines.models import UserAccount
from karaage.util import log_object as log

class PersonalDataStore(object):


    def create_new_user(self, data, hashed_password=None):
        """Creates a new user (not active)

        Keyword arguments:
        data -- a dictonary of user data
        hashed_password -- 
    
        """
        # Make sure username isn't taken in Datastore
        random_passwd = User.objects.make_random_password()
        user = User.objects.create_user(data['username'], data['email'], random_passwd)
        
        if hashed_password:
            user.password = hashed_password
        else:
            user.password = create_password_hash(data['password1'])
            
        user.is_active = False
        user.save()
    
        #Create Person
        person = Person.objects.create(
            user=user, 
            first_name=data['first_name'],
            last_name=data['last_name'],
            institute=data['institute'],
            position=data.get('position', ''),
            department=data.get('department', ''),
            title=data.get('title', ''), 
            address=data.get('address', ''),
            country=data.get('country', ''),
            website=data.get('website', ''), 
            fax=data.get('fax', ''),
            comment=data.get('comment', ''), 
            telephone=data.get('telephone', ''),
            mobile=data.get('mobile', ''),
            supervisor=data.get('supervisor', ''),
            )
        
        try:
            current_user = get_current_user()
            if current_user.is_anonymous():
                current_user = person.user
        except:
            current_user = person.user

        log(current_user, person, 1, 'Created')
        
        return person


    def activate_user(self, person):
        """ Activates a user """
        try:
            approver = get_current_user().get_profile()
            if current_user.is_anonymous():
                current_user = person
        except:
            approver = person

        person.date_approved = datetime.datetime.today()

        person.approved_by = approver
        person.deleted_by = None
        person.date_deleted = None
        person.user.is_active = True
        person.user.save()

        log(person.user, person, 1, 'Activated')

        return person
        

    def delete_user(self, person):
        """ Sets Person not active and deletes all UserAccounts"""
        person.user.is_active = False
        person.expires = None
        person.user.save()
    
        deletor = get_current_user()
    
        person.date_deleted = datetime.datetime.today()
        person.deleted_by = deletor.get_profile()
        person.save(update_datastore=False)

        from karaage.datastores import delete_account

        for ua in person.useraccount_set.filter(date_deleted__isnull=True):
            delete_account(ua)

        log(get_current_user(), person, 3, 'Deleted')    


    def update_user(self, person):
        from karaage.datastores import update_account

        for ua in person.useraccount_set.filter(date_deleted__isnull=True):
            update_account(ua)
        
    def is_locked(self, person):
        pass

    def lock_user(self, person):
        from karaage.datastores import lock_account

        for ua in person.useraccount_set.filter(date_deleted__isnull=True):
            lock_account(ua)


    def unlock_user(self, person):
        from karaage.datastores import unlock_account

        for ua in person.useraccount_set.filter(date_deleted__isnull=True):
            unlock_account(ua)


    def set_password(self, person, raw_password):
        person.user.set_password(raw_password)
        person.user.save()


class AccountDataStore(object):

    def __init__(self, machine_category):
        self.machine_category = machine_category
    
    def create_account(self, person, default_project):
        """Creates a UserAccount (if needed) and activates user.

        Keyword arguments:
        person_id -- Person id
        project_id -- Project id
        
        """
    
        ua = UserAccount.objects.create(
            user=person, username=person.username,
            machine_category=self.machine_category,
            default_project=default_project,
            date_created=datetime.datetime.today())
    
        if default_project is not None:
            default_project.users.add(person)
    
        log(get_current_user(), ua.user, 1, 'Created account on %s' % self.machine_category)


        return ua



    def delete_account(self, ua):
        
        if not ua.date_deleted:
            ua.date_deleted = datetime.datetime.now()
            ua.save()

        for project in ua.project_list():
            project.users.remove(ua.user)
        
        
        log(get_current_user(), ua.user, 3, 'Deleted account on %s' % ua.machine_category)
        

    def update_account(self, ua):
        pass

    def lock_account(self, ua):
        ua.previous_shell = ua.loginShell()
        ua.save()
        from karaage.datastores import change_shell
        change_shell(ua, settings.LOCKED_SHELL)

    def unlock_account(self, ua):
        shell = getattr(ua, 'previous_shell', '/bin/bash')
        from karaage.datastores import change_shell
        change_shell(ua, shell)

    def get_shell(self, ua):
        pass

    def change_shell(self, ua, shell):
        from karaage.datastores import get_shell
        ua.previous_shell = get_shell(ua)
        ua.save()

