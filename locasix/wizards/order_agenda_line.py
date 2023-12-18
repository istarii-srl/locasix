from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)

class OrderAgendaLine(models.TransientModel):
    _name = "locasix.order.agenda.line"
    _description = "Locasix order agenda line"

    wizard_id = fields.Many2one(string="Wizard", comodel_name="locasix.order.agenda")

    product_id = fields.Many2one(string="Product", comodel_name="product.product")

    