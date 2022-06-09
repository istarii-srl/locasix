from odoo import fields, api, models

class PropositionStatusWizard(models.TransientModel):
    _name = "locasix.prop.status.wizard"
    _description = "Proposition status wizard"

    aller_id = fields.Many2one(string="Proposition", comodel_name="locasix.aller")

    note = fields.Text(string="Remarque")
    is_asking_confirmation = fields.Boolean()

    def validate(self):
        for wizard in self:
            if wizard.is_asking_confirmation:
                wizard.aller_id.ask_confirmation(wizard.note)
            else:
                wizard.aller_id.ask_changes(wizard.note)