from odoo import fields, api, models

class AllerHistoryLines(models.Model):
    _name = "locasix.aller.history.line"
    _description = 'Historique des changements sur un aller'

    aller_id = fields.Many2one(string="Aller", comodel_name="locasix.aller", required=True)
    timestamp = fields.Datetime(string="Date")
    user_id = fields.Many2one(string="User", comodel_name="res.user")
    message = fields.Char(string="Message")