from odoo import fields, api, models

class OrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = "sale.order.line"

    has_ref_to_condi = fields.Boolean(string="Référence aux conditons additionnelles", default=False)