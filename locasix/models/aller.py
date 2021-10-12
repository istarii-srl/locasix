from odoo import fields, api, models

import logging
_logger = logging.getLogger(__name__)

class Aller(models.Model):
    _name = "locasix.aller"
    _description = "Un aller"

    name = fields.Char(string="Nom", compute="_compute_name")
    day_id = fields.Many2one(comodel_name="locasix.day", string="Journée", required=True)
    date = fields.Date(string="Date", required=True)
    agg_id = fields.Many2one(comodel_name="locasix.agg.aller", required=True)
    state = fields.Selection(string="Statut", selection=[("progress", "En cours"), ("done", "Fini"), ("cancel", "Annulé"), ("move", "Déplacé")], default="progress", required=True)
    aller_type = fields.Selection(string="type de livraison", selection=[("out", "Aller"), ("in", "Retour"), ("depl", "Déplacement")], default="out")

    order_id = fields.Many2one(string="Offre", comodel_name="sale.order")
    address_id = fields.Many2one(comodel_name="res.partner", string="Contact", required=True)
    city = fields.Char(string="Ville", related="address_id.city", store=True)
    contract = fields.Char(string="Contrat")

    product_id = fields.Many2one(string="Produit", comodel_name="product.product")
    product_unique_ref = fields.Many2one(string="N°", comodel_name="locasix.product.ref")

    remarque_ids = fields.Many2many(string="Remarques", comodel_name="locasix.remarque")
    note = fields.Text(string="Remarque libre")

    active = fields.Boolean(string="Actif", default=True)

    # @api.depends("state")
    # def _compute_active(self):
    #     _logger.info("Compute active")
    #     for aller in self:
    #         if aller.state:
    #             if aller.state == "done":
    #                 aller.active = False
    #         aller.active = True

    @api.depends('date', 'address_id')
    def _compute_name(self):
        for aggAller in self:
            if aggAller.address_id:
                aggAller.name = aggAller.address_id.name + " - "+aggAller.city if aggAller.city else ""
            else:
                aggAller.name = "/"

    @api.model
    def create(self, vals):
        # CHECK IF MERGE NEEDED
        _logger.info("in create aller")
        if not "address_id" in vals or not vals.get("address_id", False):
            _logger.info("address")
            agg_id = self.env["locasix.agg.aller"].search([("id", "=", vals["agg_id"])])
            _logger.info(agg_id.address_id)
            vals["address_id"] = agg_id.address_id.id
        if not "date" in vals or not vals.get("date", False):
            agg_id = self.env["locasix.agg.aller"].search([("id", "=", vals["agg_id"])])
            vals["date"] = agg_id.date
        obj = super(Aller, self).create(vals)
        return obj

    def write(self, vals):
        _logger.info("write Aller")
        _logger.info(vals)
        res = super(Aller, self).write(vals)
        if "address_id" in vals:
            if self.date == self.agg_id.date:
                new_agg_id = self.env["locasix.agg.aller"].search([("date", "=", self.date), ("address_id", "=", self.address_id.id), ("aller_type", "=", self.aller_type)], limit=1)
                if not new_agg_id:
                    new_agg_id = self.env["locasix.agg.aller"].create({
                        "day_id": self.day_id.id,
                        "date": self.date,
                        "aller_type": self.aller_type,
                        "address_id": self.address_id.id,
                    })
                self.agg_id = new_agg_id

        if "date" in vals:
            if self.date != self.agg_id.date:
                newday_id = self.env["locasix.day"].search([("day", "=", self.date)], limit=1)
                if not newday_id:
                    newday_id = self.env["locasix.day"].create({"day": self.date})
                
                new_agg_id = self.env["locasix.agg.aller"].search([("date", "=", self.date), ("address_id", "=", self.address_id.id), ("aller_type", "=", self.aller_type), ("day_id", "=", newday_id.id)], limit=1)
                if not new_agg_id:
                    new_agg_id = self.env["locasix.agg.aller"].create({
                        "day_id": newday_id.id,
                        "date": self.date,
                        "aller_type": self.aller_type,
                        "address_id": self.address_id.id,
                    })
                
                self.agg_id = new_agg_id
                self.day_id = newday_id

        if "state" in vals:
            if self.state == "done":
                _logger.info("yyoyoyoy")
                self.active = False

        return res


    def create_copy_to_new_agg(self, new_agg):
        for aller in self:
            new_aller = self.env["locasix.aller"].create({
                "day_id": new_agg.day_id.id,
                "date": new_agg.date,
                "agg_id": new_agg.id,
                "address_id": aller.address_id.id,
                "aller_type": new_agg.aller_type,
                "contract": aller.contract,
                "product_id": aller.product_id.id,
                "product_unique_ref": aller.product_unique_ref.id,
                "note": aller.note,
            })
            for remarque in aller.remarque_ids:
                new_aller.remarque_ids = [(4, remarque.id, 0)]
    

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