{
    'name': 'Students',
    'version': '17.0.1.0.0',
    'category': 'Education',
    'summary': 'Manage students from CRM leads',
    'description': """
        Student Management System
        - Create students from CRM leads
        - Manage student information
        - Track academic records
        - Store contact details
    """,
    'depends': ['crm', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'security/student_security.xml',
        'views/student_views.xml',
        'views/crm_lead_views.xml',
        'views/student_web_form.xml',
        'views/student_form_link.xml',
        'views/welcome_mail.xml',
        'views/product.xml',
        'views/discount.xml',
        'data/activity.xml',
        'views/branch.xml',
        'views/batch_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'web_icon': "student_management,static/description/icon.png",
}
