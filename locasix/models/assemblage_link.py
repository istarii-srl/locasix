from odoo import fields, api, models

class AssemblageLink(models.Model):
    _name = "locasix.assemblage.link"
    _description = "Lien d'assemblage"

    assemblage_product_id = fields.Many2One(string="Assemblage", comodel_name = "product.template")
    linked_product_id = fields.Many2one(string="Composant", comodel_name="product.template")

