from odoo import fields, api, models

class PropositionStatusWizard(models.TransientModel):
    _name = "locasix.prop.status.wizard"
    _description = "Proposition status wizard"

    aller_id = fields.Many2one(string="Proposition", comodel_name="locasix.aller")
    address_id = fields.Many2one(comodel_name="res.partner", string="Client")
    is_depl = fields.Boolean(string="Est un déplacement", default=False)
    date = fields.Date(string="Date", required=True)
    product_id = fields.Many2one(string="Produit", comodel_name="product.product", required=True)
    product_unique_ref = fields.Many2one(string="N°", comodel_name="locasix.product.ref")
    contract_id = fields.Many2one(string="Contrat", comodel_name="locasix.contract", domain="[('id', '=', -1)]")
    localite_id = fields.Many2one(comodel_name="locasix.municipality", string="Localité")
    localite_id_depl = fields.Many2one(comodel_name="locasix.municipality", string="Localité arrivé déplacement")

    note = fields.Text(string="Remarque")
    is_asking_confirmation = fields.Boolean()

    def validate(self):
        for wizard in self:
            if wizard.address_id != wizard.aller_id.address_id:
                wizard.aller_id.address_id = wizard.address_id
            if wizard.date != wizard.aller_id.date:
                wizard.aller_id.date = wizard.date
            if wizard.product_id != wizard.aller_id.product_id:
                wizard.aller_id.product_id = wizard.product_id
            if wizard.product_unique_ref != wizard.aller_id.product_unique_ref:
                wizard.aller_id.product_unique_ref = wizard.product_unique_ref
            if wizard.contract_id != wizard.aller_id.contract_id:
                wizard.aller_id.contract_id = wizard.contract_id
            if wizard.localite_id != wizard.aller_id.localite_id:
                wizard.aller_id.localite_id = wizard.localite_id
            if wizard.localite_id_depl != wizard.aller_id.localite_id_depl:
                wizard.aller_id.localite_id_depl = wizard.localite_id_depl

            if wizard.is_asking_confirmation:
                wizard.aller_id.ask_confirmation(wizard.note)
            else:
                wizard.aller_id.ask_changes(wizard.note)