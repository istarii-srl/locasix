from odoo import fields, api, models

class Day(models.Model):
    _name = "locasix.day"
    _description = "Gestion des allers et retours pour une journée"

    name = fields.Char()