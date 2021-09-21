from odoo import fields, api, models

class Aller(models.Model):
    _name = "locasix.aller"
    _description = "Un aller"

    day_id = fields.Many2one(comodel_name="locasix.day", string="Journée")
    agg_id = fields.Many2one(comodel_name="locasix.agg.aller")


    def open_agg(self):
        for aller in self:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': "locasix.agg.aller",
                'res_id': aller.agg_id.id,
                'target': 'current',
            }          