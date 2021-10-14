from odoo import fields , api, models

class Municipality(models.Model):
    _name = "locasix.municipality"
    _description = "Une localité"

    name = fields.Char(string="Nom", compute="_compute_name", store=True)
    postal_code = fields.Char(string="Code postal", required=True)
    city = fields.Char(string="Localité", required=True)
    is_sub_municipality = fields.Boolean(string="Est une sous-commune", default=False)
    municipality = fields.Char(string="Commune")

    @api.depends("postal_code", 'city')
    def _compute_name(self):
        for municipality in self:
            if municipality.postal_code and municipality.city:
                municipality.name = municipality.postal_code + "-"+municipality.city
            else:
                municipality.name = "En cours de création"