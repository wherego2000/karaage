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

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.contrib import messages

from karaage.projects.utils import add_user_to_project
from karaage.requests.models import ProjectJoinRequest
from karaage.util import log_object as log
from karaage.util.email_messages import send_account_approved_email, send_account_rejected_email


@permission_required('machines.add_useraccount')
def account_request_list(request):
    request_list = ProjectJoinRequest.objects.filter(leader_approved=True) 
    return render_to_response('requests/user_request_list.html', locals(), context_instance=RequestContext(request)) 


@permission_required('machines.add_useraccount')
def account_request_detail(request, ar_id):
    ar = get_object_or_404(ProjectJoinRequest, pk=ar_id)
    person = ar.person
    project = ar.project
    return render_to_response('requests/user_request_detail.html', locals(), context_instance=RequestContext(request))


@permission_required('machines.add_useraccount')
def account_request_approve(request, ar_id):
    join_request = get_object_or_404(ProjectJoinRequest, pk=ar_id)

    person = join_request.person
    project = join_request.project

    person.activate()

    log(request.user, person, 2, 'Added to project %s' % project)
    log(request.user, project, 2, '%s added to project' % person)

    add_user_to_project(person, project)

    send_account_approved_email(join_request)
    join_request.delete()

    messages.info(request, "User '%s' approved succesfully and an email has been sent" % person)
    return HttpResponseRedirect(person.get_absolute_url())


@permission_required('machines.add_useraccount')
def account_request_reject(request, ar_id):
    ar = get_object_or_404(ProjectJoinRequest, pk=ar_id)

    person = ar.person
    user = person.user
    project = ar.project
    send_account_rejected_email(ar)   
    ar.delete()
    log(request.user, person, 2, "Account rejected")

    if not person.is_active:
        person.delete()
        user.delete()

    messages.info(request, "User '%s' rejected succesfully and an email has been sent" % person)
        
    return HttpResponseRedirect(reverse('kg_account_request_list'))
