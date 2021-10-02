from odoo import fields, api, models
import datetime

class DuplicateToRetour(models.TransientModel):
    _name = "locasix.duplicate.retour"
    _description = "Assistant pour la duplication d'un retour"

    new_date = fields.Date(string="Nouvelle date", default=lambda self: self._get_default_date() , required=True)
    agg_id = fields.Many2one(string="Retours", comodel_name="locasix.agg.retour", required=True)

    def _get_default_date(self):
        return datetime.date.today()

    def validate(self):
        for wizard in self:
            return wizard.agg_id.duplicate_to(wizard.new_date)