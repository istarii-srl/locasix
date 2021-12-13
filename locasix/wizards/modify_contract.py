from odoo import fields, api, models

class ModifyContract(models.TransientModel):
    _name = "locasix.modify.contract"
    _description = "Modifier toutes les lignes d'un contrat"

    contract_id = fields.Many2one(string="Contract", comodel_name="locasix.contract")

    day_id = fields.Many2one(string="Journée", comodel_name="locasix.day")

    include_aller = fields.Boolean("Allers", default=True)
    include_retours = fields.Boolean("Retours", default=True)

    status = fields.Selection(string="Statut", selection=[("progress", "En cours"), ("cancel", "Annulé"), ("move", "Déplacé"), ("done", "fini")], default="done")


    def modify(self):
        for wizard in self:
            allers = self.env["locasix.aller"].search([("day_id", "=", wizard.day_id.id)])
            for aller in allers:
                if aller.contract_id and aller.contract_id.id == wizard.contract_id.id:
                    if (aller.aller_type == "out" or aller.aller_type == "depl") and wizard.include_aller:
                        aller.state = wizard.status
                    elif aller.aller_type == "in" and wizard.include_retours:
                        aller.state = wizard.status
