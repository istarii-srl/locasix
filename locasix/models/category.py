from odoo import fields, api, models

class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = "product.category"

    show_section_order = fields.Boolean(string="Crée une section dans l'offre", default=False)