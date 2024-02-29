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
    'version': '16.0.0.153',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'product', 'contacts'],

    # always loaded
    'data': [
        'data/locasix_settings.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/quote_paperformat.xml',
        'data/cron_jobs.xml',
        'reports/locasix_quote_template.xml',
        'reports/locasix_deposit_template.xml',
        'reports/locasix_quote_report.xml',
        "views/settings.xml",
        'views/day.xml',
        'views/order_line.xml',
        'views/product_link.xml',
        'views/product_template.xml',
        'views/aller_history_lines.xml',
        'views/lost_reason.xml',
        'views/category.xml',
        'views/order.xml',
        'views/html_template.xml',
        'views/client.xml',
        'views/municipality.xml',
        'views/order_additional_file.xml',
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
        'wizards/proposition_status_wizard.xml',
        'wizards/proposition_multi_update.xml',
        'wizards/mark_lost_popup.xml',
        'wizards/modify_contract.xml',
        'views/user.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'locasix/static/src/js/no_discount_pop_up.js',
            'locasix/static/src/js/no_discount.js',
            'locasix/static/src/js/product_tree_buttons.js',
            'locasix/static/src/js/client_tree_buttons.js',
            'locasix/static/locasix.css',
            'locasix/static/src/xml/client_tree_buttons.xml',
            'locasix/static/src/xml/product_tree_buttons.xml'
        ]
    }
}
