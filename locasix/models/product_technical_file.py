from odoo import fields, api, models

class ProductTechnicalFile(models.Model):
    _name = "locasix.product.technical"
    _description = "Product technical file"
    _inherit = ['image.mixin']
    _order = 'sequence, id'

    name = fields.Char(string="Nom", store=True, compute="_get_name")

    sequence = fields.Integer(default=10, index=True)

    image_1920 = fields.Image(required=True)

    product_tmpl_id = fields.Many2one('product.template', "Product Template", index=True, ondelete='cascade')

    def fetch_number(self):
        for technical in self:
            seq = self.env["locasix.technical.counter"].search([("product_id", "=", technical.product_tmpl_id.id)], limit=1)
            if not seq:
                seq = self.env["locasix.technical.counter"].create({"product_id": technical.product_tmpl_id.id})
            number = seq.fetch_and_increase()
            return number

    def _get_name(self):
        for technical in self:
            if technical.product_tmpl_id:
                number = technical.fetch_number()
                technical.name = "Fiche - "+f'{number:03d}'
            else:
                technical.name = "/"
