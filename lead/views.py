import calendar
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.aggregates import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import User
from accounts.views import role_required # Sizda bor bo'lgan dekorator
from .forms import StudentForm
from .models import Client, Student

# --- 1. DASHBOARD (Hamma kirganlar uchun) ---
@login_required
def dashboard(request):
    today = date.today()
    total_clients = Client.objects.count()
    leads_count = Client.objects.filter(status="new").count()
    students_count = Student.objects.filter(is_active=True).count()

    # Bugungi tushum
    daily_revenue = Student.objects.filter(
        next_payment_date=today,
        is_active=True
    ).aggregate(Sum('monthly_amount'))['monthly_amount__sum'] or 0

    recent_leads = Client.objects.all().order_by('-id')[:8]

    # 3 kunlik eslatmalar
    three_days_later = today + timedelta(days=3)
    upcoming_payments = Student.objects.filter(
        next_payment_date__range=[today, three_days_later],
        is_active=True
    ).order_by('next_payment_date')

    reminders = []
    for s in upcoming_payments:
        reminders.append({
            'name': s.full_name,
            'direction': s.direction,
            'amount': s.monthly_amount,
            'days_left': (s.next_payment_date - today).days,
            'date': s.next_payment_date
        })

    context = {
        "total": total_clients, "leads": leads_count, "students": students_count,
        "revenue": daily_revenue, "recent_leads": recent_leads, "reminders": reminders,
    }
    return render(request, "main.html", context)


# --- 2. LEADLAR BILAN ISHLASH (Boss va Manager) ---

@login_required
@role_required(allowed_roles=['boss', 'manager'])
def lead_page(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    leads_queryset = Client.objects.all().order_by('-id')

    if query:
        leads_queryset = leads_queryset.filter(Q(name__icontains=query) | Q(phone__icontains=query))
    if status_filter:
        leads_queryset = leads_queryset.filter(status=status_filter)

    context = {
        'leads': leads_queryset,
        'total_count': Client.objects.count(),
        'new_count': Client.objects.filter(status='new').count(),
        'cancel_count': Client.objects.filter(status='cancel').count(),
        'student_count': Client.objects.filter(status='student').count(),
        'query': query, 'status_filter': status_filter,
    }
    return render(request, 'lead_home.html', context)

@login_required
@role_required(allowed_roles=['boss', 'manager'])
@require_POST
def change_status(request):
    client_id = request.POST.get("id")
    status = request.POST.get("status")
    amount = request.POST.get("amount", 0)

    try:
        with transaction.atomic():
            client = Client.objects.get(pk=client_id)
            client.status = status
            client.save(update_fields=["status"])

            if status == "student":
                next_pay_date = date.today() + relativedelta(months=1)
                student, created = Student.objects.get_or_create(
                    client=client,
                    defaults={
                        'full_name': client.name, 'phone': client.phone,
                        'direction': client.course, 'monthly_amount': amount,
                        'next_payment_date': next_pay_date,
                    }
                )
                msg = f"O'quvchi yaratildi. Keyingi to'lov: {next_pay_date.strftime('%d.%m.%Y')}"
            else:
                msg = "Status o'zgartirildi."

        return JsonResponse({"success": True, "status": client.status, "message": msg})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@login_required
@role_required(allowed_roles=['boss', 'manager'])
def add_lead(request):
    if request.method == "POST":
        Client.objects.create(
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            course=request.POST.get('course'),
            source=request.POST.get('source'),
            status=request.POST.get('status', 'new'),
            comment=request.POST.get('comment'),
            manager=request.user
        )
        return redirect('lead_home') # O'zingizni URL nomingizga qarang


# --- 3. STUDENTLAR BILAN ISHLASH (Boss, Manager, Accountant) ---

@login_required
@role_required(allowed_roles=['boss', 'manager', 'accountant'])
def student_list_view(request):
    query = request.GET.get('q', '')
    students = Student.objects.filter(is_active=True).order_by('-enrollment_date')
    if query:
        students = students.filter(Q(full_name__icontains=query) | Q(phone__icontains=query))

    total_expected = students.aggregate(Sum('monthly_amount'))['monthly_amount__sum'] or 0
    today = date.today()
    total_paid = students.filter(next_payment_date__gt=date(today.year, today.month, 28)).aggregate(Sum('monthly_amount'))['monthly_amount__sum'] or 0

    context = {
        'students': students, 'total_expected': total_expected, 'total_paid': total_paid,
        'total_debt': max(0, total_expected - total_paid), 'total_students': students.count(), 'query': query,
    }
    return render(request, 'students.html', context)

@login_required
@role_required(allowed_roles=['boss', 'manager'])
def student_create_view(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.is_active = True
            student.save()
            messages.success(request, "O'quvchi qo'shildi.")
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'student_form.html', {'form': form, 'is_edit': False})

@login_required
@role_required(allowed_roles=['boss', 'manager'])
def student_update_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Yangilandi.")
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'student_form.html', {'form': form, 'is_edit': True, 'student': student})

@login_required
@role_required(allowed_roles=['boss'])
def student_delete_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.is_active = False
        student.save()
        return redirect('student_list')
    return render(request, 'student_confirm_delete.html', {'student': student})


# --- 4. BILLING / MOLIYA (Faqat Boss va Accountant) ---

@login_required
@role_required(allowed_roles=['boss', 'accountant'])
def billing_view(request):
    today = date.today()
    three_days_later = today + timedelta(days=3)

    debtors = Student.objects.filter(next_payment_date__lt=today, is_active=True).order_by('next_payment_date')
    reminders_list = Student.objects.filter(next_payment_date__range=[today, three_days_later], is_active=True).order_by('next_payment_date')

    total_expected = Student.objects.filter(is_active=True).aggregate(Sum('monthly_amount'))['monthly_amount__sum'] or 0
    total_paid = Student.objects.filter(is_active=True, next_payment_date__gt=date(today.year, today.month, 28)).aggregate(Sum('monthly_amount'))['monthly_amount__sum'] or 0

    context = {
        'debtors': debtors, 'reminders': reminders_list,
        'total_expected': total_expected, 'total_paid': total_paid,
        'total_debt': max(0, total_expected - total_paid), 'today': today,
    }
    return render(request, 'billing.html', context)

@login_required
@role_required(allowed_roles=['boss', 'accountant'])
@require_POST
def accept_payment(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # Sanani 1 oyga surish
    if student.next_payment_date:
        student.next_payment_date += relativedelta(months=1)
    else:
        student.next_payment_date = date.today() + relativedelta(months=1)
    student.save()
    return redirect('billing_view')