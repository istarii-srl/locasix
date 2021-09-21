from odoo import fields, api, models

class AggRetour(models.Model):
    _name = "locasix.agg.retour"
    _description = "Un agglomérat de retours"

    retour_ids = fields.One2many(comodel_name="locasix.retour", string="Retours", inverse_name="agg_id")