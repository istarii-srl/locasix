from odoo import fields, api, models
from random import randint

class Remarque(models.Model):
    _name = "locasix.remarque"
    _description = "Remarque"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Remarque', required=True)
    send_mail_to_assembler = fields.Boolean(string="Mail resp. assemblage")
    color = fields.Integer('Couleur', default=_get_default_color)
