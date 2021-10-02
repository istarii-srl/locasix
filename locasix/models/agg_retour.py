from odoo import fields, api, models

import logging
_logger = logging.getLogger(__name__)

class AggRetour(models.Model):
    _name = "locasix.agg.retour"
    _description = "Un agglomérat de retours"

    retour_ids = fields.One2many(comodel_name="locasix.retour", string="Retours", inverse_name="agg_id")
    name = fields.Char(string="Nom", compute="_compute_name")
    day_id = fields.Many2one(string="Journée", comodel_name="locasix.day")
    date = fields.Date(string="Date")

    address_id = fields.Many2one(comodel_name="res.partner", string="Contact")
    city = fields.Char(string="Ville", related="address_id.city")
    contract = fields.Char(string="Contrat")
    remarque_ids = fields.Many2many(string="Remarques", comodel_name="locasix.remarque")
    note = fields.Text(string="Remarque libre")
    state = fields.Selection(string='Statut', selection=[("progress", "En cours")], default="progress")

    def check_and_merge(self):
        for agg_retour in self:
            aggs = self.env["locasix.agg.retour"].search([("date", '=', agg_retour.date), ("address_id", "=", agg_retour.address_id.id), ("id", '!=', agg_retour.id)])
            for other_agg in aggs:
                for other_retour in other_agg.retour_ids:
                    other_retour.agg_id = agg_retour
                other_agg.unlink()
        return
 
    @api.model
    def create(self, vals):
        obj = super(AggRetour, self).create(vals)
        obj.check_and_merge()
        return obj

    def write(self, vals):
        _logger.info("write aggRetour")
        _logger.info(vals)
        res = super(AggRetour, self).write(vals)
        if "address_id" in vals:
            if self.date == self.day_id.day:
                for retour in self.retour_ids:
                    retour.address_id = self.address_id
                self.check_and_merge()                

        if "date" in vals:
            if self.date != self.day_id.day:
                newday_id = self.env["locasix.day"].search([("day", "=", self.date)], limit=1)
                if not newday_id:
                    newday_id = self.env["locasix.day"].create({"day": self.date})
                
                self.day_id = newday_id
                for retour in self.retour_ids:
                    retour.day_id = newday_id
                    retour.date = self.date
                self.check_and_merge()

        return res

    @api.depends('date', 'address_id')
    def _compute_name(self):
        for aggRetour in self:
            if aggRetour.date and aggRetour.address_id:
                aggRetour.name = aggRetour.date.strftime('%d/%m/%Y') + " - " + aggRetour.address_id.name
            else:
                aggRetour.name = "/"
    
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
        view = self.env.ref('locasix.locasix_duplicate_retour_form')
        return {
        'name': 'Retours',
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'locasix.duplicate.retour',
        'views': [(view.id, 'form')],
        'view_id': view.id,
        'target': 'new',
        'context': {
            'default_agg_id': self.id
            },
        }              

    def duplicate_to(self, new_date):
        for aggRetour in self:
            newday_id = self.env["locasix.day"].search([("day", "=", new_date)], limit=1)
            if not newday_id:
                newday_id = self.env["locasix.day"].create({"day": new_date})
            
            new_agg = self.env["locasix.agg.retour"].create({
                "day_id": newday_id.id,
                "date": newday_id.day,
                "address_id": aggRetour.address_id.id,
                "contract": aggRetour.contract,
                #"remarque_ids": aggRetour.remarque_ids,
                "note": aggRetour.note,
            })
            for remarque in aggRetour.remarque_ids:
                new_agg.remarque_ids = [(4, remarque.id, 0)]
            
            for retour in aggRetour.aller_ids:
                retour.create_copy_to_new_agg(new_agg)
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
