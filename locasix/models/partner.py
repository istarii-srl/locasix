from odoo import fields, api, models

class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    compte = fields.Char(string="Compte")
    alpha_key = fields.Char(string="Clé alpha")

    has_insurance = fields.Boolean(string="Mettre une assurance dans les offres", default=lambda self: self._get_default_has_insurance())

    def _get_name(self):
        name = super(Partner, self)._get_name()
        if self.compte:
            name = "["+self.compte+"] "+ name
        return name

    def _get_default_has_insurance(self):
        if self.parent_id:
            return self.parent_id.has_insurance
        else:
            return True
    
    @api.model
    def create(self, vals):
        obj = super(Partner, self).create(vals)
        if obj.parent_id:
            obj.has_insurance = obj.parent_id.has_insurance
        return obj