from odoo import fields, api, models

class Order(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    