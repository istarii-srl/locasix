from odoo import fields, api, models
import datetime

class DuplicateToAller(models.TransientModel):
    _name = "locasix.duplicate.aller"
    _description = "Assistant pour la duplication d'un aller"

    new_date = fields.Date(string="Nouvelle date", default=lambda self: self._get_default_date() , required=True)
    agg_id = fields.Many2one(string="Allers", comodel_name="locasix.agg.aller", required=True)

    def _get_default_date(self):
        return datetime.date.today()

    def validate(self):
        for wizard in self:
            wizard.agg_id.duplicate_to(wizard.new_date)