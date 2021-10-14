from odoo import fields, api, models

class AlreadyComputedWarning(models.Model):

    _name = "locasix.compute.warning"
    _description = "Warning pop-up lorsqu'il y a déjà eu un ajout automatique"

    order_id = fields.Many2one(comodel_name="sale.order", string="Offre")


    def action_compute(self):
        for wizard in self:
            wizard.order_id.action_remove_computed_lines
            wizard.order_id.line_computations()