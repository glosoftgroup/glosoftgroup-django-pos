from django.template.response import TemplateResponse
from django.http import HttpResponse
import logging

from ...userprofile.models import Staff, Attendance
from ...decorators import user_trail
from ...site.models import UserRole, Department, BankBranch, Bank

from structlog import get_logger

logger = get_logger(__name__)


def attendance(request):
    staff = Staff.objects.all()
    data = {
        "users": staff
    }
    user_trail(request.user.name, 'accessed attendance', 'view')
    logger.info('User: ' + str(request.user.name) + ' acccess attenndance')
    return TemplateResponse(request, 'dashboard/hr/attendance/list.html', data)


def detail(request):
    status = 'read'
    return TemplateResponse(request, 'dashboard/hr/attendance/employee.html', {})


def add(request):
    departments = Department.objects.all()
    roles = UserRole.objects.all()
    banks = Bank.objects.all()
    branches = BankBranch.objects.all()
    data = {
        "roles": roles,
        "departments": departments,
        "banks": banks,
        "branches": branches
    }
    user_trail(request.user.name, 'accessed attendance filling page', 'view')
    logger.info('User: ' + str(request.user.name) + 'accessed attendance filling page')
    return TemplateResponse(request, 'dashboard/hr/attendance/fill_attendance.html', data)


def add_process(request):
    name = request.POST.get('name')
    time_in = request.POST.get('time_in')
    time_out = request.POST.get('time_out')
    department = request.POST.get('department')
    date = request.POST.get('date')
    new_attendance = Attendance(name=name, time_in=time_in,
                                time_out=time_out, date=date, department=department)
    try:
        new_attendance.save()
        user_trail(request.user.name, 'filled in attendance', 'add')
        logger.info('User: ' + str(request.user.name) + 'filled in attendance')
        return HttpResponse('success')
    except Exception as e:
        logger.info('Error when saving ')
        logger.error('Error when saving ')
        return HttpResponse(e)
