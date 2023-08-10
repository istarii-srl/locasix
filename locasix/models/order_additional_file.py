from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)

class OrderAdditionalFile(models.Model):
    _name = "locasix.order.file"
    _description = "Locasix order file"
    _inherit = ['image.mixin']
    _order = 'sequence, id'


    name = fields.Char(string="Nom", store=True, compute="_get_name")

    sequence = fields.Integer(default=10, index=True)
    image_1920 = fields.Image(required=True)

    order_id = fields.Many2one('sale.order', "Commande", index=True, ondelete='cascade', readonly=True)



    def _get_name(self):
        for technical in self:
            if technical.order_id:
                technical.name = "Fiche - " + technical.order_id.name
            else:
                technical.name = "/"