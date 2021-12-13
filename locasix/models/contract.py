from odoo import fields, api, models

class Contract(models.Model):
    _name = "locasix.contract"
    _description = "Contract"

    name = fields.Char(string="Contrat")