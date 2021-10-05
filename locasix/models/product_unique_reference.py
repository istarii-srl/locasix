from odoo import fields, api, models

class ProductUniqueReference(models.Model):
    _name = "locasix.product.ref"
    _description = "Référence unique d'un produit"

    name = fields.Char(string="N°")