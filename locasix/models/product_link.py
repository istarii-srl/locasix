from odoo import fields, api, models

class ProductLinks(models.Model):
    _name = "locasix.product.link"
    _description = "Lien entre deux produits"

    product_master_id = fields.Many2one(comodel_name="product.template", string="Produit actif", required=True)
    product_linked_id = fields.Many2one(comodel_name="product.template", string="Produit passif", required=True)

    is_on_sale = fields.Boolean(string="Vente", default=True)
    is_on_weekend = fields.Boolean(string="Weekend", default=True)
    is_on_classic = fields.Boolean(string="Location", default=True)    