from odoo import fields, api, models

class ProductLinks(models.Model):
    _name = "locasix.product.link"
    _description = "Lien entre deux produits"

    product_master_id = fields.Many2one(comodel_name="product.template", string="Produit maître")
    product_linked_id = fields.Many2one(comodel_name="product.template", string="Produit lié")