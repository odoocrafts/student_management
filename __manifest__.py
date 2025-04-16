{
    'name': 'Student Management',
    'version': '1.0',
    'category': 'Education',
    'summary': 'Manage students from CRM leads',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/student_views.xml',
        'views/crm_lead_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'student_management,static/description/icon.png',
        ],
    },
    'web_icon': "student_management,static/description/icon.png",
    'installable': True,
    'application': True,
}
