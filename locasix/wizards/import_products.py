from odoo import fields, api, models


class ImportProducts(models.TransientModel):
    _name = "locasix.product.import"
    _description = "Assistant pour l'importation de nouveaux produits"

    file = fields.Binary(string="File", required=True, attachment=False)


    def import_products(self):
        for wizard in self:
            return