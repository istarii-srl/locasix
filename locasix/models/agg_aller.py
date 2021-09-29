from odoo import fields, api, models

class AggAller(models.Model):
    _name = "locasix.agg.aller"
    _description = "Un agglomérat d'allers"

    date = fields.Date(string="Date")

    aller_ids = fields.One2many(comodel_name="locasix.aller", string="Allers", inverse_name="agg_id")
