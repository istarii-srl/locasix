from odoo import models, api, fields

class LocasixSettings(models.TransientModel):
    _name = "res.config.settings"
    _inherit = "res.config.settings"

    has_extra_cost_transport = fields.Boolean(string="Ajout du surcoût", default=False)
    email_shipping_handler = fields.Char(string="Email gestionnaire", default="o.libbrecht@locasix.be")
    extra_cost_transport_rate = fields.Float(string="Pourcentage de surcoût", default=0.06)
    
    def set_values(self):
        super(LocasixSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('locasix.has_extra_cost_transport', self.has_extra_cost_transport)
        self.env['ir.config_parameter'].sudo().set_param('locasix.extra_cost_transport_rate', self.extra_cost_transport_rate)
        self.env['ir.config_parameter'].sudo().set_param('locasix.email_shipping_handler', self.email_shipping_handler)

    def get_values(self):
        res = super(LocasixSettings, self).get_values()
        has_extra_cost_transport = self.env['ir.config_parameter'].sudo().get_param('locasix.has_extra_cost_transport')
        extra_cost_transport_rate = self.env['ir.config_parameter'].sudo().get_param('locasix.extra_cost_transport_rate')
        email_shipping_handler = self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler')
 
        res.update({
            'has_extra_cost_transport': has_extra_cost_transport,
            'extra_cost_transport_rate': extra_cost_transport_rate,
            'email_shipping_handler': email_shipping_handler,
        });
        return res