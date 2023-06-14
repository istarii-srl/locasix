from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)

class LostReason(models.Model):
    _name = "locasix.lost.reason"
    _description = "Locasix lost reason"

    name = fields.Char(string="Raison")