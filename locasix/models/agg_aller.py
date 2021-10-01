from odoo import fields, api, models

class AggAller(models.Model):
    _name = "locasix.agg.aller"
    _description = "Un agglomérat d'allers"

    day_id = fields.Many2one(string="Journée", comodel_name="locasix.day")
    date = fields.Date(string="Date", related="day_id.day")

    address_id = fields.Many2one(comodel_name="res.partner", string="Contact")
    city = fields.Char(string="Ville", related="address_id.city")
    contract = fields.Char(string="Contrat")
    remarque_ids = fields.Many2many(string="Remarques", comodel_name="locasix.remarque")
    note = fields.Text(string="Remarque libre")
    state = fields.Selection(string='Statut', selection=[("progress", "En cours")], default="progress")
    aller_ids = fields.One2many(comodel_name="locasix.aller", string="Allers", inverse_name="agg_id")


    def duplicate_to(self, new_date):
        for aggAller in self:
            newday_id = self.env["locasix.day"].search([("day", "=", new_date)], limit=1)
            if not newday_id:
                newday_id = self.env["locasix.day"].create({"day": new_date})
            
            new_agg = self.env["locasix.agg.aller"].create({
                "day_id": newday_id.id,
                "address_id": aggAller.address_id,
                "contract": aggAller.contract,
                "remarque_ids": aggAller.remarque_ids,
                "note": aggAller.note,
            })
            #for remarque in aggAller.remarque_ids:
            #    new_agg.remarque_ids = [(4, remarque.id, 0)]
            
            for aller in aggAller.aller_ids:
                aller.create_copy_to_new_agg(new_agg)



    def action_validate(self):
        return

