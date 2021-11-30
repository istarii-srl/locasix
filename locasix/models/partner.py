from odoo import fields, api, models

class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    compte = fields.Char(string="Compte")
    alpha_key = fields.Char(string="Clé alpha")

    has_insurance = fields.Boolean(string="Mettre une assurance dans les offres", default=lambda self: self._get_default_has_insurance())

    @api.depends('is_company', 'name', 'parent_id.display_name', 'type', 'company_name', 'compte')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None, html_format=None, show_vat=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            
            display_name = names.get(partner.id)
            if partner.compte:
                partner.display_name = "["+partner.compte+"] "+display_name
            else:
                partner.display_name = display_name

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