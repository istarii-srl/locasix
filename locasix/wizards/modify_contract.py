from odoo import fields, api, models

class ModifyContract(models.TransientModel):
    _name = "locasix.modify.contract"
    _description = "Modifier toutes les lignes d'un contrat"

    contract_id = fields.Many2one(string="Contract", comodel_name="locasix.contract")

    day_id = fields.Many2one(string="Journée", comodel_name="locasix.day")

    include_aller = fields.Boolean("Allers", default=True)
    include_retours = fields.Boolean("Retours", default=True)

    status = fields.Selection(string="Statut", selection=[("progress", "En cours"), ("cancel", "Annulé"), ("move", "Déplacé"), ("zdone", "fini")], default="zdone")

    @api.onchange('day_id')
    def _on_mission_changed(self):
        for wizard in self:
            allers = self.env["locasix.aller"].search([("day_id", "=", wizard.day_id.id)])
            names = []
            for aller in allers:
                if aller.contract_id:
                    names.append(aller.contract_id.name)      
            return {'domain': {'contract_id': [('name', 'in', names)]}}

    def modify(self):
        for wizard in self:
            allers = self.env["locasix.aller"].search([("day_id", "=", wizard.day_id.id)])
            for aller in allers:
                if aller.contract_id and aller.contract_id.name == wizard.contract_id.name:
                    if (aller.aller_type == "out" or aller.aller_type == "depl") and wizard.include_aller:
                        aller.state = wizard.status
                    elif aller.aller_type == "in" and wizard.include_retours:
                        aller.state = wizard.status
