from odoo import fields, api, models
import datetime
import logging
_logger = logging.getLogger(__name__)

class Aller(models.Model):
    _name = "locasix.aller"
    _description = "Un aller"

    name = fields.Char(string="Nom", compute="_compute_name", store=True)
    day_id = fields.Many2one(comodel_name="locasix.day", string="Journée", required=True)
    date = fields.Date(string="Date", required=True)
    agg_id = fields.Many2one(comodel_name="locasix.agg.aller", required=True)
    state = fields.Selection(string="Statut", selection=lambda self: self._state_selection(), default="progress", required=True)
    aller_type = fields.Selection(string="type de livraison", selection=[("out", "Aller"), ("in", "Retour"), ("depl", "Déplacement")], default="out")

    order_id = fields.Many2one(string="Offre", comodel_name="sale.order")
    address_id = fields.Many2one(comodel_name="res.partner", string="Client", required=True)
    is_depl = fields.Boolean(string="Est un déplacement", default=False)

    localite_id = fields.Many2one(comodel_name="locasix.municipality", string="Localité")
    localite_id_depl = fields.Many2one(comodel_name="locasix.municipality", string="Localité arrivé déplacement")

    full_name = fields.Char(string="Nom du client", related="address_id.display_name")
    city = fields.Char(string="Ville", compute="_compute_city", store=True)
    contract = fields.Char(string="Contrat")

    product_default_code = fields.Char(string="Ref", related="product_id.default_code")
    product_id = fields.Many2one(string="Produit", comodel_name="product.product", required=True)
    product_unique_ref = fields.Many2one(string="N°", comodel_name="locasix.product.ref")

    history_ids = fields.One2many(string="Lignes de l'historique", comodel_name="locasix.aller.history.line", inverse_name="aller_id")
    remarque_ids = fields.Many2many(string="Remarques", comodel_name="locasix.remarque")
    note = fields.Text(string="Remarque libre")

    active = fields.Boolean(string="Actif", default=True)

    def _state_selection(self):
        select = [("progress", "En cours"), ("cancel", "Annulé"), ("move", "Déplacé")]
        if self.env.user.has_group('locasix.group_locasix_admin'):
            select.append(('done', "Fini"))
        return select

    @api.depends('localite_id', 'localite_id_depl', 'is_depl')
    def _compute_city(self):
        for aller in self:
            if not aller.is_depl:
                if aller.localite_id:
                    aller.city = aller.localite_id.city
                else:
                    aller.city = "/"
            else:
                if aller.localite_id_depl and aller.localite_id:
                    aller.city = aller.localite_id.city + " -> "+aller.localite_id_depl.city
                elif aller.localite_id:
                    aller.city = aller.localite_id.city
                else:
                    aller.city = "/"

    @api.depends('date', 'address_id')
    def _compute_name(self):
        for aggAller in self:
            if aggAller.address_id:
                aggAller.name = aggAller.address_id.name + (" - "+aggAller.city if aggAller.city else "")
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
        if not "localite_id" in vals or not vals.get("localite_id", False):
            _logger.info("address")
            agg_id = self.env["locasix.agg.aller"].search([("id", "=", vals["agg_id"])])
            _logger.info(agg_id.localite_id)
            vals["localite_id"] = agg_id.localite_id.id
        if not "localite_id_depl" in vals or not vals.get("localite_id_depl", False):
            _logger.info("address")
            agg_id = self.env["locasix.agg.aller"].search([("id", "=", vals["agg_id"])])
            _logger.info(agg_id.address_id)
            vals["localite_id_depl"] = agg_id.localite_id_depl.id
            vals["is_depl"] = agg_id.is_depl
        if not "date" in vals or not vals.get("date", False):
            agg_id = self.env["locasix.agg.aller"].search([("id", "=", vals["agg_id"])])
            vals["date"] = agg_id.date
        obj = super(Aller, self).create(vals)
        obj.create_history_message("Création de l'aller")
        return obj

    def write(self, vals):
        _logger.info("write Aller")
        _logger.info(vals)
        old_state = self.state
        old_date = self.date
        old_address_id = self.address_id
        old_localite_depl = self.localite_id_depl
        old_localite = self.localite_id
        old_contract = self.contract
        res = super(Aller, self).write(vals)
        if "localite_id_depl" in vals:
            if old_localite_depl and self.localite_id_depl:
                self.create_history_message("Changement de l'addresse d'arrivée du déplacement : "+old_localite_depl.name+" -> "+self.localite_id_depl.name)
            elif old_localite_depl:
                self.create_history_message("Changement de l'addresse d'arrivée du déplacement : "+old_localite_depl.name+" -> Aucune addresse")
            elif self.localite_id_depl:
                self.create_history_message("Changement de l'addresse d'arrivée du déplacement : Aucune addresse -> "+self.localite_id_depl.name)    

        if "localite_id" in vals:
            if old_localite and self.localite_id:
                self.create_history_message("Changement de l'addresse : "+old_localite.name+" -> "+self.localite_id.name)
            elif old_localite:
                self.create_history_message("Changement de l'addresse : "+old_localite.name+" -> Aucune addresse")
            elif self.localite_id:
                self.create_history_message("Changement de l'addresse : Aucune addresse -> "+self.localite_id.name)            
        
        if "address_id" in vals:
            if old_address_id and self.address_id:
                self.create_history_message("Changement de client : "+old_address_id.display_name+" -> "+self.address_id.display_name)
            elif old_address_id:
                self.create_history_message("Changement de client : "+old_address_id.display_name+" -> Pas de client")
            elif self.address_id:
                self.create_history_message("Changement de client : Pas de client -> "+self.address_id.display_name)

            if self.date == self.agg_id.date:
                new_agg_id = self.env["locasix.agg.aller"].search([("date", "=", self.date), ("address_id", "=", self.address_id.id), ("aller_type", "=", self.aller_type), ("is_depl", "=", self.is_depl), ("localite_id", "=", self.localite_id.id)], limit=1)
                if not new_agg_id:
                    new_agg_id = self.env["locasix.agg.aller"].create({
                        "day_id": self.day_id.id,
                        "date": self.date,
                        "is_depl": self.is_depl,
                        "aller_type": self.aller_type,
                        "address_id": self.address_id.id,
                    })
                self.agg_id = new_agg_id

        if "date" in vals:
            self.create_history_message("Changement de date : "+str(old_date)+" -> "+str(self.date))
            if self.date != self.agg_id.date:
                newday_id = self.env["locasix.day"].search([("day", "=", self.date)], limit=1)
                if not newday_id:
                    newday_id = self.env["locasix.day"].create({"day": self.date})
                
                new_agg_id = self.env["locasix.agg.aller"].search([("date", "=", self.date), ("address_id", "=", self.address_id.id), ("aller_type", "=", self.aller_type), ("day_id", "=", newday_id.id), ("is_depl", "=", self.is_depl), ("localite_id", "=", self.localite_id.id)], limit=1)
                if not new_agg_id:
                    new_agg_id = self.env["locasix.agg.aller"].create({
                        "day_id": newday_id.id,
                        "date": self.date,
                        "is_depl": self.is_depl,
                        "localite_id": self.localite_id.id,
                        "aller_type": self.aller_type,
                        "address_id": self.address_id.id,
                    })
                
                self.agg_id = new_agg_id
                self.day_id = newday_id

        if "state" in vals:
            self.create_history_message("Changement de statut : "+str(self.state_to_string(old_state))+" -> "+str(self.state_to_string(self.state)))
            if self.state == "done":
                self.active = False
        if "contract" in vals:
            if self.contract and old_contract:
                self.create_history_message("Changement de contrat : "+ old_contract +" -> "+ self.contract)
            elif self.contract:
                self.create_history_message("Changement de contrat : "+ "Pas de contrat" +" -> "+ self.contract)
            elif old_contract:
                self.create_history_message("Changement de contrat : "+ old_contract +" -> "+ "Pas de contrat")
        return res
    
    def state_to_string(self, state_key):
        if state_key == "progress":
            return "En cours"
        elif state_key == "done":
            return "Fini"
        elif state_key == "cancel":
            return "Annulé"
        elif state_key == "move":
            return "Déplacé"
        else:
            return "Pas de statut"



    def create_history_message(self, message):
        for aller in self:
            user = self.env.user
            timestamp = datetime.datetime.now()
            self.env["locasix.aller.history.line"].create({
                "user_id": user.id,
                "timestamp": timestamp,
                "aller_id": aller.id,
                "message": message,
            })

    def create_copy_to_new_agg(self, new_agg):
        for aller in self:
            new_aller = self.env["locasix.aller"].create({
                "day_id": new_agg.day_id.id,
                "date": new_agg.date,
                "agg_id": new_agg.id,
                "is_depl": new_agg.is_depl,
                "localite_id": aller.localite_id.id,
                "localite_id_depl": aller.localite_id_depl.id,
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