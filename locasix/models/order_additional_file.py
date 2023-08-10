from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)

class OrderAdditionalFile(models.Model):
    _name = "locasix.order.file"
    _description = "Locasix order file"


    sequence = fields.Integer(default=10, index=True)

    image_1920 = fields.Image(required=True)

    order_id = fields.Many2one('sale.order', "Commande", index=True, ondelete='cascade')