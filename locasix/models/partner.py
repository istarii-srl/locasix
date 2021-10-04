from odoo import fields, api, models

class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    compte = fields.Char(string="Compte")
    alpha_key = fields.Char(string="Clé alpha")
    