from odoo import fields , api, models

class Municipality(models.Model):
    _name = "locasix.municipality"
    _description = "Une localité"

    name = fields.Char(string="Nom", compute="_compute_name", store=True)
    postal_code = fields.Char(string="Code postal", required=True)
    city = fields.Char(string="Localité", required=True)
    is_sub_municipality = fields.Boolean(string="Est une sous-commune", default=False)
    municipality = fields.Char(string="Commune")

    province = fields.Selection(string="Province", selection=[("brabant_wallon", "Brabant Wallon"), ("hainaut", "Hainaut"), ("liege", "Liège"), ("luxembourg", "Luxembourg"), ("namur", "Namur"), ("brabant_flamand", "Brabant Flamand"), ("flandre_occidentale", "Flandre Occidentale"), ("flandre_orientale", "Flandre Orientale"), ("anvers", "Anvers"), ("limbourg", "Limbourg"), ('bruxelles', 'Bruxelles'), ('autre', 'Autres')], compute="_compute_province", store=True)

    @api.depends("postal_code")
    def _compute_province(self):
        for municipality in self:
            if municipality.postal_code:
                postal_code = int(municipality.postal_code)
                if postal_code >= 1300 and postal_code <= 1499:
                    municipality.province = "brabant_wallon"
                elif postal_code >= 4000 and postal_code <= 4999:
                    municipality.province = "liege"
                elif (postal_code >= 6000 and postal_code <= 6599) or (postal_code >= 7000 and postal_code <= 7999):
                    municipality.province = "hainaut"
                elif postal_code >= 5000 and postal_code <= 5680:
                    municipality.province = "namur"
                elif postal_code >= 6600 and postal_code <= 6999:
                    municipality.province = "luxembourg"
                elif (postal_code >= 1500 and postal_code <= 1999) or (postal_code >= 3000 and postal_code <= 3499):
                    municipality.province = "brabant_flamand"
                elif postal_code >= 8000 and postal_code <= 8999:
                    municipality.province = "flandre_occidentale"
                elif postal_code >= 9000 and postal_code <= 9999:
                    municipality.province = "flandre_orientale"
                elif postal_code >= 2000 and postal_code <= 2999:
                    municipality.province = "anvers"
                elif postal_code >= 3500 and postal_code <= 3999:
                    municipality.province = "limbourg"
                elif postal_code >= 1000 and postal_code <= 1299:
                    municipality.province = "bruxelles"
                else:
                    municipality.province = "brabant_wallon"
            else:
                municipality.province = "autre"

    @api.depends("postal_code", 'city')
    def _compute_name(self):
        for municipality in self:
            if municipality.postal_code and municipality.city:
                municipality.name = municipality.postal_code + "-"+municipality.city
            else:
                municipality.name = "En cours de création"