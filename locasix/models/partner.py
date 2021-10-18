from odoo import fields, api, models

class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    compte = fields.Char(string="Compte")
    alpha_key = fields.Char(string="Clé alpha")

    has_insurance = fields.Boolean(string="Mettre une assurance dans les offres", default=lambda self: self._get_default_has_insurance())


    def _get_default_has_insurance(self):
        if self.parent_id:
            return self.parent_id.has_insurance
        else:
            return True
    