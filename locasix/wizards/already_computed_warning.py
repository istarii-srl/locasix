from odoo import fields, api, models
from odoo.exceptions import UserError

class AlreadyComputedWarning(models.Model):

    _name = "locasix.compute.warning"
    _description = "Warning pop-up lorsqu'il y a déjà eu un ajout automatique"

    order_id = fields.Many2one(comodel_name="sale.order", string="Offre")
    offer_type = fields.Selection(related="order_id.offer_type")
    has_assemblage = fields.Boolean(compute="_compute_has_assemblage")

    already_transport = fields.Boolean(string="Transport déjà encodé", default=False)

    transport_aller = fields.Float(string="Prix transport aller / weekend")
    transport_retour = fields.Float(string="Prix transport retour")

    frais_assemblage_aller = fields.Float(string="Frais assemblage aller")
    frais_assemblage_retour = fields.Float(string="Frais assemblage retour")

    @api.depends("order_id")
    def _compute_has_assemblage(self):
        for wizard in self:
            has_assemblage = False
            for line in wizard.order_id.order_line:
                if line.product_id and line.product_id.is_assemblage_product and not line.from_compute:
                    has_assemblage = True
            wizard.has_assemblage = has_assemblage


    def action_compute(self):
        for wizard in self:
            if wizard.transport_aller == 0.0 and not wizard.already_transport:
                raise UserError("Montant(s) de zéro !")
            if wizard.transport_retour == 0.0 and wizard.offer_type == "classic" and not wizard.already_transport:
                raise UserError("Montant(s) de zéro !")
            if (wizard.frais_assemblage_retour == 0.0 or wizard.frais_assemblage_aller == 0.0) and wizard.has_assemblage:
                raise UserError("Montant(s) de zéro !")
            wizard.order_id.action_remove_computed_lines()
            wizard.order_id.line_computations(wizard.transport_aller, wizard.transport_retour, wizard.frais_assemblage_aller, wizard.frais_assemblage_retour, wizard.already_transport)