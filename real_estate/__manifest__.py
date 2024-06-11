{
    'name' : 'Real Estate',
    'version' : '17.0',
    'summary': 'Real Estate Management Module',
    'sequence': 10,
    'description': """
    Real Estate Management Module
    ====================
    This Odoo Module allows you to manage your real estate business.
    """,
    'category': 'Business',
    'website': 'https://www.odoo.com/documentation/17.0/developer/tutorials/server_framework_101.html',
    'depends': [
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_menus.xml',
        'views/res_users.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}
