from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = 'res.users'

    signature_image = fields.Image(string="Signature")
    work_location = fields.Selection([('ghislain', 'Saint-Ghislain'), ('thimister', 'Thimister')], string="Lieu de travail", default='ghislain')
    