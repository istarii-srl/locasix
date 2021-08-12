from odoo import fields, api, models

class Order(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    front_page_body = fields.Html(string="Page de garde")
    added_terms = fields.Html(string="Conditions additionnelles")