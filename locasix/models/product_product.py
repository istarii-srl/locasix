from odoo import fields, api, models

class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"


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