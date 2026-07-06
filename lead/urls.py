from django.urls import path
from .views import dashboard, lead_page, change_status, add_lead, student_list_view, student_create_view, \
    student_update_view, student_delete_view, billing_view, accept_payment

urlpatterns = [

    path(
        "",
        dashboard,
        name="dashboard"
    ),
    path(
        "lead_list/",
        lead_page,
        name="lead"
    ),
    path(
        "change-status/",
        change_status,
        name="change_status"
    ),
    path('lead/add/', add_lead, name='add_lead'),
    # path('student_list/', student_list_view, name='student_list'),
    path('students/', student_list_view, name='student_list'),
    path('students/add/', student_create_view, name='student_add'),
    path('students/<int:pk>/edit/', student_update_view, name='student_edit'),
    path('students/<int:pk>/delete/', student_delete_view, name='student_delete'),
    path('billing/', billing_view, name='billing_page'),
    path('billing/accept/<int:pk>/', accept_payment, name='accept_payment'),

]
