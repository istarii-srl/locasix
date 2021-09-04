# -*- coding: utf-8 -*-
{
    'name': "locasix",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "istarii",
    'website': "https://istarii.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'ERP',
    'version': '0.15.44',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/locasix_settings.xml',
        'data/quote_paperformat.xml',
        'reports/locasix_quote_template.xml',
        'reports/locasix_quote_report.xml',
        'views/day.xml',
        'views/order_line.xml',
        'views/product_link.xml',
        'views/product_template.xml',
        'views/category.xml',
        'views/order.xml',
        'wizards/already_computed_warning.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
