# -*- coding: utf-8 -*-
{
    'name': "locasix",

    'summary': """
        Locasix""",

    'description': """
        Locasix
    """,

    'author': "istarii",
    'website': "https://istarii.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'ERP',
    'version': '0.18.74',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/locasix_settings.xml',
        'data/quote_paperformat.xml',
        'data/cron_jobs.xml',
        'reports/locasix_quote_template.xml',
        'reports/locasix_quote_report.xml',
        'views/day.xml',
        'views/order_line.xml',
        'views/product_link.xml',
        'views/product_template.xml',
        'views/category.xml',
        'views/order.xml',
        'views/assets.xml',
        'views/client.xml',
        'views/aller.xml',
        'views/remarque.xml',
        'views/retour.xml',
        'views/agg_aller.xml',
        'views/agg_retour.xml',
        'views/assemblage_link.xml',
        'views/product_plan.xml',
        'views/product_technical.xml',
        'wizards/export_products.xml',
        'wizards/no_transport_price_warning.xml',
        'wizards/import_products.xml',
        'wizards/import_clients.xml',
        'wizards/already_computed_warning.xml',
        'views/menus.xml',
    ],
    'qweb': [
        'static/src/xml/client_tree_buttons.xml',
        'static/src/xml/product_tree_buttons.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
