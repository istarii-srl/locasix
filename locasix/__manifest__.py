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
    'version': '0.18.417',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'product', 'contacts'],

    # always loaded
    'data': [
        'data/locasix_settings.xml',
        'security/ir.model.access.csv',
        'data/quote_paperformat.xml',
        'data/cron_jobs.xml',
        'reports/locasix_quote_template.xml',
        'reports/locasix_quote_report.xml',
        'views/day.xml',
        'views/order_line.xml',
        'views/product_link.xml',
        'views/product_template.xml',
        'views/aller_history_lines.xml',
        'views/category.xml',
        'views/order.xml',
        'views/assets.xml',
        'views/html_template.xml',
        'views/client.xml',
        'views/municipality.xml',
        'views/aller.xml',
        'views/remarque.xml',
        'views/agg_aller.xml',
        "views/product_unique_ref.xml",
        'views/assemblage_link.xml',
        'views/product_plan.xml',
        'views/product_technical.xml',
        'wizards/export_products.xml',
        'wizards/order_to_agenda.xml',
        'wizards/no_transport_price_warning.xml',
        'wizards/import_products.xml',
        'wizards/duplicate_to_aller.xml',
        'wizards/import_clients.xml',
        'wizards/already_computed_warning.xml',
        'wizards/modify_contract.xml',
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
