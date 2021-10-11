from odoo import fields, api, models
import datetime

import logging
_logger = logging.getLogger(__name__)

class AggAller(models.Model):
    _name = "locasix.agg.aller"
    _description = "Un agglomérat d'allers"

    name = fields.Char(string="Nom", compute="_compute_name")
    day_id = fields.Many2one(string="Journée", comodel_name="locasix.day")
    date = fields.Date(string="Date", required=True)
    aller_type = fields.Selection(string="type de livraison", selection=[("out", "Aller"), ("in", "Retour"), ("depl", "Déplacement")], default="out")

    address_id = fields.Many2one(comodel_name="res.partner", string="Contact", required=True)
    city = fields.Char(string="Ville", related="address_id.city")
    contract = fields.Char(string="Contrat")
    remarque_ids = fields.Many2many(string="Remarques", comodel_name="locasix.remarque")
    note = fields.Text(string="Remarque libre")
    state = fields.Selection(string='Statut', selection=[("progress", "En cours")], default="progress", required=True)
    aller_ids = fields.One2many(comodel_name="locasix.aller", string="Allers", inverse_name="agg_id")

    is_weekend = fields.Boolean("Weekend", default=False)
    date_retour = fields.Datetime(string="Date de retour", default=lambda self: self._get_default_date())
    is_retours_created = fields.Boolean(default=False)

    def _get_default_date(self):
        return datetime.date.today()


    # TODO USE THAT IN WRITE AND CREATE
    def check_and_merge(self):
        for agg_aller in self:
            aggs = self.env["locasix.agg.aller"].search([("date", '=', agg_aller.date), ("address_id", "=", agg_aller.address_id.id), ("id", '!=', agg_aller.id), ("aller_type", "=", agg_aller.aller_type)])
            for other_agg in aggs:
                if other_agg.is_retours_created:
                    agg_aller.is_retours_created = True
                    agg_aller.is_weekend = True
                    agg_aller.date_retour = other_agg.date_retour
                for other_aller in other_agg.aller_ids:
                    other_aller.agg_id = agg_aller
                other_agg.unlink()
        return
 
    def weekend_check(self):
        for agg_aller in self:
            if agg_aller.date_retour and not agg_aller.is_retours_created and agg_aller.address_id and agg_aller.is_weekend:
                agg_retour_id = self.env["locasix.agg.aller"].search([("date", "=", agg_aller.date_retour), ("address_id", "=", agg_aller.address_id.id), ("aller_type", "=", "in")], limit=1)
                if not agg_retour_id:
                    newday_id = self.env["locasix.day"].search([("day", "=", agg_aller.date_retour)], limit=1)
                    if not newday_id:
                        newday_id = self.env["locasix.day"].create({"day": agg_aller.date_retour})
                    agg_retour_id = self.env["locasix.agg.aller"].create({
                        "day_id": newday_id.id,
                        "aller_type": "in",
                        "date": agg_aller.date_retour,
                        "address_id": agg_aller.address_id.id,
                    })
                for aller in agg_aller.aller_ids:
                    retour = self.env["locasix.aller"].create({
                    "day_id": agg_retour_id.day_id.id,
                    "aller_type": "in",
                    "date": agg_retour_id.date,
                    "agg_id": agg_retour_id.id,
                    "address_id": aller.address_id.id,
                    "contract": aller.contract,
                    "product_id": aller.product_id.id,
                    "product_unique_ref": aller.product_unique_ref.id,
                    "note": aller.note,
                })
                    for remarque in aller.remarque_ids:
                        retour.remarque_ids = [(4, remarque.id, 0)]     
                agg_aller.is_retours_created = True                                   

    @api.model
    def create(self, vals):
        obj = super(AggAller, self).create(vals)
        obj.check_and_merge()
        obj.weekend_check()
        return obj

    def write(self, vals):
        _logger.info("write aggAller")
        _logger.info(vals)
        res = super(AggAller, self).write(vals)
        if "address_id" in vals:
            if self.date == self.day_id.day:
                for aller in self.aller_ids:
                    aller.address_id = self.address_id
                self.check_and_merge()                

        if "date" in vals:
            if self.date != self.day_id.day:
                newday_id = self.env["locasix.day"].search([("day", "=", self.date)], limit=1)
                if not newday_id:
                    newday_id = self.env["locasix.day"].create({"day": self.date})
                
                self.day_id = newday_id
                for aller in self.aller_ids:
                    aller.day_id = newday_id
                    aller.date = self.date
                self.check_and_merge()
        self.weekend_check()

        return res

    @api.depends('date', 'address_id')
    def _compute_name(self):
        for aggAller in self:
            if aggAller.date and aggAller.address_id:
                aggAller.name = aggAller.date.strftime('%d/%m/%Y') + " - " + aggAller.address_id.name
            else:
                aggAller.name = "/"
    
    # def action_open_duplicate_wizard(self):
    #     view = self.env.ref('locasix.locasix_agg_aller_form')
    #     return {
    #     'name': 'Allers',
    #     'type': 'ir.actions.act_window',
    #     'view_type': 'form',
    #     'view_mode': 'form',
    #     'res_model': 'locasix.agg.aller',
    #     'views': [(view.id, 'form')],
    #     'view_id': view.id,
    #     'target': 'new',
    #     'context': {
    #         "default_address_id": self.address_id.id,
    #         }
    #     }      

    def action_open_duplicate_wizard(self):
        view = self.env.ref('locasix.locasix_duplicate_aller_form')
        return {
        'name': 'Allers',
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'locasix.duplicate.aller',
        'views': [(view.id, 'form')],
        'view_id': view.id,
        'target': 'new',
        'context': {
            'default_agg_id': self.id
            },
        }              
        

    def duplicate_to(self, new_date, aller_type):
        for aggAller in self:
            newday_id = self.env["locasix.day"].search([("day", "=", new_date)], limit=1)
            if not newday_id:
                newday_id = self.env["locasix.day"].create({"day": new_date})
            
            new_agg = self.env["locasix.agg.aller"].create({
                "day_id": newday_id.id,
                "date": newday_id.day,
                "aller_type": aller_type,
                "address_id": aggAller.address_id.id,
                "contract": aggAller.contract,
                #"remarque_ids": aggAller.remarque_ids,
                "note": aggAller.note,
            })
            for remarque in aggAller.remarque_ids:
                new_agg.remarque_ids = [(4, remarque.id, 0)]
            
            for aller in aggAller.aller_ids:
                aller.create_copy_to_new_agg(new_agg)
            view = self.env.ref('locasix.locasix_day_form')
            return {
            'name': 'Allers et retours',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'locasix.day',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id': newday_id.id,
            'target': 'current',
            }      



    def action_validate(self):
        return

