from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _name = "res.company"
    _inherit = "res.company"


    company_type = fields.Selection(string="Type de société", selection=[("locasix", "Locasix"), ("six", "Six Units")], default="locasix", required=True)
    pub_six_units_attachment_id = fields.Many2one('ir.attachment', string="Pub Six Units", help="La publicité Six Units à ajouter à la fin des devis")