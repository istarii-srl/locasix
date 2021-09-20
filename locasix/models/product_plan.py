from odoo import fields, api, models

class ProductPlan(models.Model):
    _name = "locasix.product.plan"
    _description = "Product Plan"
    _inherit = ['image.mixin']
    _order = 'sequence, id'

    name = fields.Char(string="Nom", store=True, compute="_get_name")

    sequence = fields.Integer(default=10, index=True)

    image_1920 = fields.Image(required=True)

    product_tmpl_id = fields.Many2one('product.template', "Product Template", index=True, ondelete='cascade')

    def fetch_number(self):
        for plan in self:
            seq = self.env["locasix.plan.counter"].search([("product_id", "=", plan.product_tmpl_id.id)], limit=1)
            if not seq:
                seq = self.env["locasix.plan.counter"].create({"product_id": plan.product_tmpl_id.id})
            number = seq.fetch_and_increase()
            return number

    def _get_name(self):
        for plan in self:
            if plan.product_tmpl_id:
                number = plan.fetch_number()
                plan.name = "Plan - "+f'{number:03d}'
            else:
                plan.name = "/"
