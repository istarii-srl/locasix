from odoo import fields, api, models

class ProductUniqueReference(models.Model):
    _name = "locasix.product.ref"
    _description = "Référence unique d'un produit"

    name = fields.Char(string="N°")
    product_id = fields.Many2one(string="Produit", comodel_name="product.template")