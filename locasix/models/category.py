from odoo import fields, api, models

class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = "product.category"

    show_section_order = fields.Boolean(string="Crée une section dans l'offre", default=False)
    show_electro_annexe = fields.Boolean(string="Ajoute l'annexe groupe électrogène dans l'offre", default=False)
    has_months_discounts = fields.Boolean(string="Appliquer les réductions sur location longues durées", default=True)