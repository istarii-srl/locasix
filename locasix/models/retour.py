from odoo import fields, api, models


class Retour(models.Model):
    _name = "locasix.retour"
    _description = "Un retour"

    day_id = fields.Many2one(comodel_name="locasix.day", string="Journée")