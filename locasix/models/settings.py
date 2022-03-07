from odoo import models, api, fields

class LocasixSettings(models.TransientModel):
    _name = "res.config.settings"
    _inherit = "res.config.settings"

    has_extra_cost_transport = fields.Boolean(string="Ajout du surcoût", default=False)
    extra_cost_transport_rate = fields.Float(string="Pourcentage de surcoût", default=0.06)
    
    def set_values(self):
        super(LocasixSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('locasix.has_extra_cost_transport', self.has_extra_cost_transport)
        self.env['ir.config_parameter'].sudo().set_param('locasix.extra_cost_transport_rate', self.extra_cost_transport_rate)

    def get_values(self):
        res = super(LocasixSettings, self).get_values()
        has_extra_cost_transport = self.env['ir.config_parameter'].sudo().get_param('locasix.has_extra_cost_transport')
        extra_cost_transport_rate = self.env['ir.config_parameter'].sudo().get_param('locasix.extra_cost_transport_rate')
 
        res.update({
            'has_extra_cost_transport': has_extra_cost_transport,
            'extra_cost_transport_rate': extra_cost_transport_rate,
        });
        return res