from odoo import fields, api, models

class Aller(models.Model):
    _name = "locasix.aller"
    _description = "Un aller"

    day_id = fields.Many2one(comodel_name="locasix.day", string="Journée", required=True)
    date = fields.Date(string="Date", related="day_id.day")
    agg_id = fields.Many2one(comodel_name="locasix.agg.aller", required=True)
    state = fields.Selection(string="Statut", selection=[("progress", "En cours")], default="progress")

    address_id = fields.Many2one(comodel_name="res.partner", string="Contact")
    city = fields.Char(string="Ville", related="address_id.city")
    contract = fields.Char(string="Contrat")

    product_id = fields.Many2one(string="Produit", comodel_name="product.product")
    product_unique_ref = fields.Many2one(string="N°", comodel_name="locasix.product.ref")

    remarque_ids = fields.Many2many(string="Remarques", comodel_name="locasix.remarque")
    note = fields.Text(string="Remarque libre")


    def create_copy_to_new_agg(self, new_agg):
        for aller in self:
            self.env["locasix.aller"].create({
                "day_id": new_agg.day_id.id,
                "agg_id": new_agg.id,
                "address_id": aller.address_id.id,
                "contract": aller.contract,
                "product_id": aller.product_id,
                "remarque_ids": aller.remarque_ids,
                "note": aller.note,
            })

    @api.onchange('product_id')
    def _on_product_changed(self):
        for aller in self:
            return {'domain': {'product_unique_ref': [('product_id', '=', aller.product_id.product_tmpl_id.id)]}}

    def open_agg(self):
        view = self.env.ref('locasix.locasix_agg_aller_form')
        return {
        'name': 'Allers',
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'locasix.agg.aller',
        'views': [(view.id, 'form')],
        'view_id': view.id,
        'res_id': self.agg_id.id,
        'target': 'new',
        }      