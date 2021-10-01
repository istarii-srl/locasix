from odoo import fields, api, models

class AggAller(models.Model):
    _name = "locasix.agg.aller"
    _description = "Un agglomérat d'allers"

    day_id = fields.Many2one(string="Journée", comodel_name="locasix.day")
    date = fields.Date(string="Date", related="day_id.day")

    address_id = fields.Many2one(comodel_name="res.partner", string="Contact")
    city = fields.Char(string="Ville", related="address_id.city")
    contract = fields.Char(string="Contrat")
    remarque_ids = fields.Many2many(string="Remarques", comodel_name="locasix.remarque")
    note = fields.Text(string="Remarque libre")

    aller_ids = fields.One2many(comodel_name="locasix.aller", string="Allers", inverse_name="agg_id")

    def action_validate(self):
        return