from odoo import fields, api, models

class AlreadyComputedWarning(models.Model):

    _name = "locasix.compute.warning"
    _description = "Warning pop-up lorsqu'il y a déjà eu un ajout automatique"

    order_id = fields.Many2one(comodel_name="sale.order", string="Offre")
    offer_type = fields.Selection(related="order_id.offer_type")
    has_assemblage = fields.Boolean(compute="_compute_has_assemblage")

    transport_aller = fields.Float(string="Prix transport aller / weekend", default=0.0)
    transport_retour = fields.Float(string="Prix transport retour", default=0.0)

    frais_assemblage_aller = fields.Float(string="Frais assemblage aller", default=0.0)
    frais_assemblage_retour = fields.Float(string="Frais assemblage retour", default=0.0)

    @api.depends("order_id")
    def _compute_has_assemblage(self):
        for wizard in self:
            has_assemblage = False
            for line in wizard.order_id.order_line:
                if line.product_id and line.product_id.is_assemblage_product:
                    has_assemblage = True
            wizard.has_assemblage = has_assemblage


    def action_compute(self):
        for wizard in self:
            wizard.order_id.action_remove_computed_lines()
            wizard.order_id.line_computations(wizard.transport_aller, wizard.transport_retour, wizard.frais_assemblage_aller, wizard.frais_assemblage_retour)