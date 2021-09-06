from odoo import fields, api, models

class Day(models.Model):
    _name = "locasix.day"
    _description = "Gestion des allers et retours pour une journée"

    name = fields.Char(string="Jour", computed="_compute_name")
    day = fields.Date(string="Date", required=True)


    @api.depends('day')
    def _compute_name(self):
        for day in self:
            day.name = day.to_date().strftime('%m/%d/%Y')