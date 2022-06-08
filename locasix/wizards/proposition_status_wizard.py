from odoo import fields, api, models

class PropositionStatusWizard(models.TransientModel):
    _name = "locasix.prop.status.wizard"
    _description = "Proposition status wizard"

    aller_id = fields.Many2one(string="Proposition", comodel_name="locasix.aller")

    def validate(self):
        pass