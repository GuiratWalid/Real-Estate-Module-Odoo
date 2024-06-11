{
    'name' : 'Estate Account',
    'version' : '17.0',
    'summary': 'Real Estate Management Module',
    'sequence': 11,
    'description': """
    Estate Account Management Module
    ================================
    This Odoo Module allows you to create invoices for the real estate module.
    """,
    'category': 'Accounting/Accounting',
    'website': 'https://www.odoo.com/documentation/17.0/developer/tutorials/server_framework_101/13_other_module.html',
    'depends': [
        'account',
        'real_estate'
    ],
    'data': [
        "views/estate_property_views.xml",
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'assets': {},
    'license': 'LGPL-3',
}
