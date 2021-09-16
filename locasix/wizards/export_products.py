from odoo import fields, api, models

class ExportProducts(models.TransientModel):
    _name = "locasix.product.export"
    _description = "Assistance pour l'exportation de produits"

    product_ids = fields.Many2many(comodel_name="product.template", default=lambda self : self._get_default_products())

    def _get_default_products(self):
        return self.env["product.template"].search([("active", "=", True)])

    def export_products(self):
        for wizard in self:
            return