from odoo import fields, api, models

class ProductPlan(models.Model):
    _name = "locasix.product.plan"
    _description = "Product Plan"
    _inherit = ['image.mixin']
    _order = 'sequence, id'

    sequence = fields.Integer(default=10, index=True)

    image_1920 = fields.Image(required=True)

    product_tmpl_id = fields.Many2one('product.template', "Product Template", index=True, ondelete='cascade')