from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from ..views import staff_member_required
from ...userprofile.models import User, UserTrail
from ...decorators import permission_decorator, user_trail
from ...utils import render_to_pdf, image64
import csv
import random
from django.utils.encoding import smart_str
import logging
from datetime import date

debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')

@staff_member_required
@permission_decorator('userprofile.view_usertrail')
def user_trails(request):   
    try:
        users = UserTrail.objects.all().order_by('-now')
        paginator = Paginator(users, 10)
        page = request.GET.get('page', 1)
        user_trail(request.user.name, 'accessed user trail page', 'view')
        info_logger.info('User: '+str(request.user.name)+' accessed the user trail page')

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except InvalidPage:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        return TemplateResponse(request, 'dashboard/users/trail.html', {'users':users, 'pn':paginator.num_pages})
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing users')

@staff_member_required
@permission_decorator('userprofile.view_user')
def users(request):
    try:
        users = User.objects.all().order_by('-id')
        groups = Group.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(users, 10)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except InvalidPage:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed users list page','view')
        info_logger.info('User: '+str(request.user.name)+' accessed the view users page')
        return TemplateResponse(request, 'dashboard/users/users.html', {'groups':groups,'users':users, 'pn': paginator.num_pages})
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing users')

@staff_member_required
def usertrail_paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    date = request.GET.get('date')
    action = request.GET.get('action')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    gid = request.GET.get('gid')
    users = UserTrail.objects.all().order_by('-now')
    if request.GET.get('sth'):

        if date:
            try:
                users = UserTrail.objects.filter(date=date).order_by('-now')
                if p2_sz and gid:
                    paginator = Paginator(users, int(p2_sz))
                    users = paginator.page(page)
                    return TemplateResponse(request,'dashboard/users/trail/paginate.html',{'users':users, 'gid':date})

                paginator = Paginator(users, 10)
                users = paginator.page(page)
                return TemplateResponse(request,'dashboard/users/trail/p2.html',{'users':users, 'pn':paginator.num_pages,'sz':10,'gid':date})

            except ValueError as e:
                return HttpResponse(e)

        if action:
            try:
                users = UserTrail.objects.filter(crud=action).order_by('-now')
                if p2_sz and gid:
                    paginator = Paginator(users, int(p2_sz))
                    users = paginator.page(page)
                    return TemplateResponse(request,'dashboard/users/trail/paginate.html',{'users':users, 'gid':action})

                paginator = Paginator(users, 10)
                users = paginator.page(page)
                return TemplateResponse(request,'dashboard/users/trail/p2.html',{'users':users, 'pn':paginator.num_pages,'sz':10,'gid':action})

            except ValueError as e:
                return HttpResponse(e)
    else:

        if list_sz:
            paginator = Paginator(users, int(list_sz))
            users = paginator.page(page)
            return TemplateResponse(request,'dashboard/users/trail/p2.html',{'users':users, 'pn':paginator.num_pages,'sz':list_sz, 'gid':0})
        else:
            paginator = Paginator(users, 10)
        if p2_sz:
            paginator = Paginator(users, int(p2_sz))
            users = paginator.page(page)
            return TemplateResponse(request,'dashboard/users/trail/paginate.html',{'users':users})

        if date:
            try:
                users = UserTrail.objects.filter(date=date).order_by('-now')
                if p2_sz:
                    paginator = Paginator(users, int(p2_sz))
                    users = paginator.page(page)
                    return TemplateResponse(request,'dashboard/users/trail/paginate.html',{'users':users, 'gid':date})

                paginator = Paginator(users, 10)
                users = paginator.page(page)
                return TemplateResponse(request,'dashboard/users/trail/p2.html',{'users':users, 'pn':paginator.num_pages,'sz':10,'gid':date})

            except ValueError as e:
                return HttpResponse(e)

        if action:
            try:
                users = UserTrail.objects.filter(crud=action).order_by('-now')
                if p2_sz:
                    paginator = Paginator(users, int(p2_sz))
                    users = paginator.page(page)
                    return TemplateResponse(request,'dashboard/users/trail/paginate.html',{'users':users, 'gid':action})

                paginator = Paginator(users, 10)
                users = paginator.page(page)
                return TemplateResponse(request,'dashboard/users/trail/p2.html',{'users':users, 'pn':paginator.num_pages,'sz':10,'gid':action})

            except ValueError as e:
                return HttpResponse(e)


        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except InvalidPage:
            groups = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        return TemplateResponse(request,'dashboard/users/trail/paginate.html',{'users':users})

@staff_member_required
def user_paginate(request):
    page = int(request.GET.get('page', 1))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')

    if request.GET.get('gid'):
        users = User.objects.filter(groups__id=request.GET.get('gid'))
        if p2_sz:
            paginator = Paginator(users, int(p2_sz))
            users = paginator.page(page)
            return TemplateResponse(request,'dashboard/users/paginate.html',{'users':users})

        if list_sz:
            paginator = Paginator(users, int(list_sz))
            users = paginator.page(page)
            return TemplateResponse(request,'dashboard/users/p2.html',{'users':users, 'pn':paginator.num_pages,'sz':list_sz, 'gid':request.GET.get('gid')})

        paginator = Paginator(users, 10)
        users = paginator.page(page)
        return TemplateResponse(request,'dashboard/users/p2.html',{'users':users, 'pn':paginator.num_pages,'sz':10,'gid':request.GET.get('gid')})

    else:
        users = User.objects.all().order_by('-id')
        if list_sz:
            paginator = Paginator(users, int(list_sz))
            users = paginator.page(page)
            return TemplateResponse(request,'dashboard/users/p2.html',{'users':users, 'pn':paginator.num_pages,'sz':list_sz, 'gid':0})
        else:
            paginator = Paginator(users, 10)
        if p2_sz:
            paginator = Paginator(users, int(p2_sz))
            users = paginator.page(page)
            return TemplateResponse(request,'dashboard/users/paginate.html',{'users':users})

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except InvalidPage:
            groups = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        return TemplateResponse(request,'dashboard/users/paginate.html',{'users':users})

@staff_member_required
@permission_decorator('userprofile.add_user')
def user_add(request):
    try:
        permissions = Permission.objects.all()
        groups = Group.objects.all()
        user_trail(request.user.name, 'accessed add users page', 'view')
        info_logger.info('User: '+str(request.user.name)+' accessed user create page')
        return TemplateResponse(request, 'dashboard/users/add_user.html',{'permissions':permissions, 'groups':groups})
    except TypeError as e:
        error_logger.error(e)
        return HttpResponse('error accessing add users page')

@staff_member_required
@csrf_protect
def user_process(request):
    user = User.objects.all()
    if request.method == 'POST':
        name = (request.POST.get('name')).lower()
        email = request.POST.get('email')
        password = request.POST.get('password')
        encr_password = make_password(password)
        nid = request.POST.get('nid')
        mobile = request.POST.get('mobile').replace(' ','').replace('(','').replace(')','').replace('-','')
        image= request.FILES.get('image')
        groups = request.POST.getlist('groups[]')
        job_title = request.POST.get('job_title')
        new_user = User(
            name=name,
            email=email,
            password=encr_password,
            nid=nid,
            mobile=mobile,
            image=image,
            job_title=job_title,
        )
        try:
            new_user.save()
        except IntegrityError:
            error_logger.info('Error when saving ')
            return HttpResponse('user exists with those details')
        except Exception, e:
            error_logger.error(e)
            
        last_id = User.objects.latest('id')
        if groups:
            permissions = Permission.objects.filter(group__name__in=groups)
            last_id.user_permissions.add(*permissions)
            gps = Group.objects.filter(name__in=groups)
            last_id.groups.add(*gps)
            last_id.save()
        user_trail(request.user.name, 'added user: '+str(name), 'add')
        info_logger.info('User: '+str(request.user.name)+' created user:'+str(name))
        return HttpResponse(last_id.id)

@staff_member_required
@permission_decorator('userprofile.change_user')
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_permissions = Permission.objects.filter(user=user)
    groups = user.groups.all()
    permissions = Permission.objects.filter(group__in=[group for group in groups]).distinct()
    all_permissions = list(set(user_permissions).union(set(permissions)))
    if request.user == user:
        user_trail(request.user.name, 'viewed self profile ','view')
        info_logger.info('User: '+str(request.user)+' viewed self profile')
    else:
        user_trail(request.user.name, 'viewed '+str(user.name)+ '`s profile','view')
        info_logger.info('User: '+str(request.user.name)+' viewed '+str(user.name)+'`s profile')
    return TemplateResponse(request, 'dashboard/users/detail.html', {'user':user,'all_permissions':all_permissions,'groups':groups})

@staff_member_required
@permission_decorator('userprofile.delete_user')
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        user_trail(request.user.name, 'deleted user: '+ str(user.name),'delete')
        return HttpResponse('success')

@staff_member_required
@permission_decorator('userprofile.change_user')
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    permissions = Permission.objects.all()
    groups = Group.objects.all()
    user_groups = user.groups.all()
    user_permissions = Permission.objects.filter(user=user)
    ctx = {'user': user,'permissions':permissions, 'user_permissions':user_permissions, 'groups':groups, 'user_groups':user_groups}
    user_trail(request.user.name, 'accessed edit page for user '+ str(user.name),'view')
    info_logger.info('User: '+str(request.user.name)+' accessed edit page for user: '+str(user.name))
    return TemplateResponse(request, 'dashboard/users/edit_user.html', ctx)

@staff_member_required
@csrf_protect
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_permissions = Permission.objects.filter(user=user)
    user_groups = user.groups.all()
    permissions_in_user_groups = Permission.objects.filter(group__in=[group for group in user_groups])

    if request.method == 'POST':
        name = (request.POST.get('user_name')).lower()
        email = request.POST.get('user_email')
        password = request.POST.get('user_password')
        nid = request.POST.get('user_nid')
        mobile = request.POST.get('user_mobile').replace(' ','').replace('(','').replace(')','').replace('-','')
        image= request.FILES.get('image')
        job_title = request.POST.get('job_title')
        groups = request.POST.getlist('groups[]')

        if password == user.password:
            encr_password = user.password
        else:
            encr_password = make_password(password)
        if image :
            user.name = name
            user.email = email
            user.password = encr_password
            user.nid = nid
            user.mobile = mobile
            user.job_title = job_title
            user.image = image
            user.save()
            user_trail(request.user.name, 'updated user: '+ str(user.name),'update')
            info_logger.info('User: '+str(request.user.name)+' updated user: '+str(user.name))

            if groups:
                th_groups2 = Group.objects.filter(name__in=[group for group in groups])
                if set(user_groups).difference(set(th_groups2)) or set(th_groups2).difference(set(user_groups)):
                    group_permissions = Permission.objects.filter(group__name__in=[group for group in th_groups2])
                    user.groups.remove(*user_groups)
                    user.groups.add(*th_groups2)
                    user.user_permissions.remove(*permissions_in_user_groups)
                    user.user_permissions.add(*group_permissions)
            else:
                '''remove all groups'''
                if user_groups:
                    user.groups.remove(*user_groups)
                    return HttpResponse("groups removed")
            return HttpResponse("success with image")
        else:
            user.name = name
            user.email = email
            user.password = encr_password
            user.nid = nid
            user.mobile = mobile
            user.job_title = job_title
            user.save()
            user_trail(request.user.name, 'updated user: '+ str(user.name), 'update')
            info_logger.info('User: '+str(request.user.name)+' updated user: '+str(user.name),'update')


            if groups:
                th_groups2 = Group.objects.filter(name__in=[group for group in groups])
                if set(user_groups).difference(set(th_groups2)) or set(th_groups2).difference(set(user_groups)):
                    group_permissions = Permission.objects.filter(group__name__in=[group for group in th_groups2])
                    user.groups.remove(*user_groups)
                    user.groups.add(*th_groups2)
                    user.user_permissions.remove(*permissions_in_user_groups)
                    user.user_permissions.add(*group_permissions)
            else:
                '''remove all groups'''
                if user_groups:
                    user.groups.remove(*user_groups)
                    return HttpResponse("groups removed")
            return HttpResponse("success without image")




@staff_member_required
@csrf_protect
def user_assign_permission(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        user_has_permissions = Permission.objects.filter(user=user)
        login_status = request.POST.get('check_login')
        permission_list = request.POST.getlist('checklist[]')
        if login_status == 'inactive':
            user.is_staff = False
            user.is_active = False
            user.user_permissions.remove(*user_has_permissions)
            user.save()
            user_trail(request.user.name, 'deactivated and removed all permissions for user: '+ str(user.name), 'delete')
            info_logger.info('User: '+str(request.user.name)+' deactivated and removed all permissions for user: '+str(user.name))
            return HttpResponse('deactivated')
        else:
            if user_has_permissions in permission_list:
                not_in_user_permissions = list(set(permission_list) - set(user_has_permissions))
                user.is_staff = True
                user.is_active = True
                user.user_permissions.add(*not_in_user_permissions)
                user.save()
                user_trail(request.user.name, 'assigned permissions for user: '+ str(user.name),'add')
                info_logger.info('User: '+str(request.user)+' assigned permissions for user: '+str(user.name))
                return HttpResponse('permissions added')
            else:
                not_in_user_permissions = list(set(permission_list) - set(user_has_permissions))
                user.is_staff = True
                user.is_active = True
                user.user_permissions.remove(*user_has_permissions)
                user.user_permissions.add(*not_in_user_permissions)
                user.save()
                user_trail(request.user.name, 'assigned permissions for user: '+ str(user.name),'add')
                info_logger.info('User: '+str(request.user.name)+' assigned permissions for user: '+str(user.name))
                return HttpResponse('permissions updated')

@staff_member_required
def user_search( request ):

    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size')
        p2_sz = request.GET.get('psize')
        q = request.GET.get( 'q' )
        if list_sz == 0 or list_sz is None:
            sz = 10
        else:
            sz = list_sz


        if q is not None:
            users = User.objects.filter(
                Q( name__icontains = q ) |
                Q( email__icontains = q ) | Q( mobile__icontains = q ) ).order_by('-id' )

            if request.GET.get('gid'):
                users = users.filter(groups__id=request.GET.get('gid'))
                if p2_sz:
                    paginator = Paginator(users, int(p2_sz))
                    users = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/users/paginate.html', {'users': users})

                if list_sz:
                    paginator = Paginator(users, int(list_sz))
                    users = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/users/search.html',
                                            {'users': users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid':request.GET.get('gid'),'q':q})

                paginator = Paginator(users, 10)
                users = paginator.page(page)
                return TemplateResponse(request, 'dashboard/users/search.html',
                                        {'users': users, 'pn': paginator.num_pages, 'sz': sz,
                                         'gid': request.GET.get('gid')})

            else:
                if list_sz:
                    paginator = Paginator(users, int(list_sz))
                    users = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/users/search.html',
                                            {'users': users, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,'q':q})

                if p2_sz:
                    paginator = Paginator(users, int(p2_sz))
                    users = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/users/paginate.html', {'users': users})

                paginator = Paginator(users, 10)
                try:
                    users = paginator.page(page)
                except PageNotAnInteger:
                    users = paginator.page(1)
                except InvalidPage:
                    users = paginator.page(1)
                except EmptyPage:
                    users = paginator.page(paginator.num_pages)
                return TemplateResponse(request, 'dashboard/users/search.html', {'users':users, 'pn':paginator.num_pages,'sz':sz,'q':q})

@staff_member_required
def usertrail_search( request ):

    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size',10)
        p2_sz = request.GET.get('psize')
        q = request.GET.get( 'q' )
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            users = UserTrail.objects.filter(
                Q( name__icontains = q ) |
                Q( action__icontains = q ) | Q( date__icontains = q ) ).order_by( '-now' )
            paginator = Paginator(users, 10)
            try:
                users = paginator.page(page)
            except PageNotAnInteger:
                users = paginator.page(1)
            except InvalidPage:
                users = paginator.page(1)
            except EmptyPage:
                users = paginator.page(paginator.num_pages)
            if p2_sz:
                users = paginator.page(page)
                return TemplateResponse(request,'dashboard/users/trail/paginate.html',{'users':users})

            return TemplateResponse(request, 'dashboard/users/trail/search.html', {'users':users, 'pn':paginator.num_pages,'sz':sz,'q':q})

@staff_member_required
def users_pdf(request):
    name = request.GET.get('name')
    users = User.objects.all()
    img = image64()
    data = {
        'today': date.today(),
        'users': users,
        'puller': request.user,
        'name':name,
        'image':img,
        }
    pdf = render_to_pdf('dashboard/users/pdf/users.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

@staff_member_required
def users_export_csv(request):
    pdfname = 'users'+str(random.random())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="'+pdfname+'.csv"'
    qs = User.objects.all()
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"ID"),
        smart_str(u"Name"),
        smart_str(u"Email"),
        smart_str(u"Job Title"),
    ])
    for obj in qs:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.name),
            smart_str(obj.email),
            smart_str(obj.job_title),
        ])
    return response








