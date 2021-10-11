from odoo import fields, api, models
import datetime

class OrderToAgenda(models.TransientModel):
    _name = "locasix.order.agenda"
    _description = "Assistant permettant de créer des allers et retours depuis une offre"

    order_id = fields.Many2one(string="Offre", comodel_name="sale.order", required=True)
    line_ids = fields.Many2many(string="Lignes", comodel_name="sale.order.line")

    aller_date = fields.Date(string="Date de l'aller", default=lambda self: self._get_default_date(), required=True)

    should_create_retour = fields.Boolean(string="Date de retour déjà connue ?", default=False)
    retour_date = fields.Date(string="Date du retour", default=lambda self: self._get_default_date(), required=True)

    def _get_default_date(self):
        return datetime.date.today()

    
    def action_create(self):
        for wizard in self:
            wizard.order_id.exported_to_agenda = True
            for line in wizard.line_ids:
                if line.product_id:
                    newday_id = self.env["locasix.day"].search([("day", "=", wizard.aller_date)], limit=1)
                    if not newday_id:
                        newday_id = self.env["locasix.day"].create({"day": wizard.aller_date})
                
                    new_agg_id = self.env["locasix.agg.aller"].search([("date", "=", wizard.aller_date), ("address_id", "=", wizard.order_id.partner_id.id), ("day_id", "=", newday_id.id), ("aller_type", "=", "out")], limit=1)
                    if not new_agg_id:
                        new_agg_id = self.env["locasix.agg.aller"].create({
                            "day_id": newday_id.id,
                            "aller_type": "out",
                            "date": wizard.aller_date,
                            "address_id": wizard.order_id.partner_id.id,
                        })

                    self.env["locasix.aller"].create({
                        "day_id": newday_id.id,
                        "date": new_agg_id.date,
                        "agg_id": new_agg_id.id,
                        "aller_type": "out",
                        "order_id": wizard.order_id.id,
                        "address_id": new_agg_id.address_id.id,
                        "product_id": line.product_id.id,
                    })
                    if wizard.should_create_retour:
                        newday_id = self.env["locasix.day"].search([("day", "=", wizard.retour_date)], limit=1)
                        if not newday_id:
                            newday_id = self.env["locasix.day"].create({"day": wizard.retour_date})
                    
                        new_agg_id = self.env["locasix.agg.aller"].search([("date", "=", wizard.retour_date), ("address_id", "=", wizard.order_id.partner_id.id), ("day_id", "=", newday_id.id), ("aller_type", "=", "in")], limit=1)
                        if not new_agg_id:
                            new_agg_id = self.env["locasix.agg.aller"].create({
                                "day_id": newday_id.id,
                                "date": wizard.retour_date,
                                "aller_type": "in",
                                "address_id": wizard.order_id.partner_id.id,
                            })

                        self.env["locasix.aller"].create({
                            "day_id": newday_id.id,
                            "date": new_agg_id.date,
                            "aller_type": "in",
                            "agg_id": new_agg_id.id,
                            "order_id": wizard.order_id.id,
                            "address_id": new_agg_id.address_id.id,
                            "product_id": line.product_id.id,
                        })