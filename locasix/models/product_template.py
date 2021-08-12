from odoo import fields, api, models

class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    product_description = fields.Char(string="Description du produit")

    weekend_price = fields.Float(string="Prix weekend")
    has_24_price = fields.Boolean(string="A un tarif 24/24", default=False)
    has_multi_price = fields.Boolean(string="A plusieurs tarifs", default=False)
    has_ref_to_condi = fields.Boolean(string="Référence vers les conditions additionnelles", default=False)
    more_details_link = fields.Char(string="Lien vers plus de détail") 