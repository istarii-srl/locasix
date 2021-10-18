from odoo import fields, api, models, tools

class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"

    @api.onchange('is_assemblage_product')
    def is_assemblage_changed(self):
        if self.is_assemblage_product:
            categ_id = self.env["product.category"].search([("name", "=", "Location de modules habitables - containers maritimes")], limit=1)
        else:
            categ_id = self.env["product.category"].search([("name", "=", "All")], limit=1)
        if categ_id:
            self.categ_id = categ_id

    @tools.ormcache()
    def _get_default_category_id(self):
        # Deletion forbidden (at least through unlink)
        categ_id = self.env["product.category"].search([("name", "=", "Location de modules habitables - containers maritimes")], limit=1)
        if not categ_id:
            return self.env.ref('product.product_category_all')
        else:
            return categ_id

    def get_plans(self):
        for product in self:
            if product.is_assemblage_product:
                plans = product.plan_ids[:]
                for assemblage in product.assemblage_ids:
                    plans += assemblage.linked_product_id.get_plans()
                return plans
            else:
                return product.plan_ids
    
    def get_technicals(self):
        for product in self:
            if product.is_assemblage_product:
                plans = product.technical_ids[:]
                for assemblage in product.assemblage_ids:
                    plans += assemblage.linked_product_id.get_technicals()
                return plans
            else:
                return product.technical_ids