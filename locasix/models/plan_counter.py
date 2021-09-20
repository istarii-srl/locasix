from odoo import fields, api, models

class PlanCounter(models.Model):
    _name = "locasix.plan.counter"
    _description = "Gère le numéro de séquence des lots par vendeur"

    product_id = fields.Many2one(comodel_name="product.template", string="Produit")
    next_number = fields.Integer(string="Prochain numéro de séquence", default=1)


    def fetch_and_increase(self):
        for seq in self:
            number = seq.next_number
            seq.next_number = number + 1
            return number
