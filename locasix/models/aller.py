from odoo import fields, api, models
import datetime
import logging
_logger = logging.getLogger(__name__)


COLORS_BY_STATE = {
    'out': 1,
    'in': 7,
    'depl': 9,
}


class Aller(models.Model):
    _name = "locasix.aller"
    _description = "Un aller"
    _order = "state, address_id"

    name = fields.Char(string="Nom", compute="_compute_name", store=True)
    day_id = fields.Many2one(comodel_name="locasix.day", string="Journée", required=True)
    date = fields.Date(string="Date", required=True)
    agg_id = fields.Many2one(comodel_name="locasix.agg.aller", required=True)
    state = fields.Selection(string="Statut", selection=lambda self: self._state_selection(), default="progress", required=True)
    aller_type = fields.Selection(string="type de livraison", selection=[("out", "Aller"), ("in", "Retour"), ("depl", "Déplacement")], default="out")
    color = fields.Integer(compute='_compute_color')

    is_first_line = fields.Boolean(default=False)


    order_id = fields.Many2one(string="Offre", comodel_name="sale.order")
    address_id = fields.Many2one(comodel_name="res.partner", string="Client", required=True)
    is_depl = fields.Boolean(string="Est un déplacement", default=False)

    localite_id = fields.Many2one(comodel_name="locasix.municipality", string="Localité")
    localite_id_depl = fields.Many2one(comodel_name="locasix.municipality", string="Localité arrivé déplacement")

    full_name = fields.Char(string="Nom du client ", related="address_id.display_name")
    displayed_client = fields.Char(string="Nom du client", compute="_compute_displayed_names")
    city = fields.Char(string="Ville ", compute="_compute_city", store=True)
    displayed_city = fields.Char(string="Ville", compute="_compute_displayed_names")
    contract = fields.Char(string="Contrat ")
    contract_id = fields.Many2one(string="Contrat", comodel_name="locasix.contract")

    product_default_code = fields.Char(string="Ref", related="product_id.default_code")
    product_id = fields.Many2one(string="Produit", comodel_name="product.product", required=True)
    product_unique_ref = fields.Many2one(string="N°", comodel_name="locasix.product.ref")

    history_ids = fields.One2many(string="Lignes de l'historique", comodel_name="locasix.aller.history.line", inverse_name="aller_id")
    remarque_ids = fields.Many2many(string="Remarques", comodel_name="locasix.remarque")
    note = fields.Text(string="Remarque libre ")
    displayed_note = fields.Text(string="Remarque libre", compute="_compute_displayed_names")

    active = fields.Boolean(string="Actif", default=True)

    @api.depends('city', 'address_id', 'localite_id', 'localite_id_depl', 'is_depl', 'note')
    def _compute_displayed_names(self):
        for aller in self:
            if aller.city:
                if len(aller.city) > 23:
                    aller.displayed_city = aller.city[:23] +".."
                else:
                    aller.displayed_city = aller.city
            else:
                aller.displayed_city = "/"
            if aller.address_id and aller.address_id.display_name:
                if len(aller.address_id.display_name) > 17:
                    aller.displayed_client = aller.address_id.display_name[:17] +".."
                else:
                    aller.displayed_client = aller.address_id.display_name
            else:
                aller.displayed_client = "/"
            if aller.note:
                if len(aller.note) > 20:
                    aller.displayed_note = aller.note[:20] + ".."
                else:
                    aller.displayed_note = aller.note
            else:
                aller.displayed_note = "/"
                


    def _compute_color(self):
        for record in self:
            record.color = COLORS_BY_STATE[record.aller_type]

    def _state_selection(self):
        select = [("progress", "En cours"), ("cancel", "Annulé"), ("move", "Déplacé")]
        if self.env.user.has_group('locasix.group_locasix_admin'):
            select.append(('zdone', "Fini"))
            select.append(('a', "Statut technique"))
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
            if aggAller.is_first_line and aggAller.date:
                aggAller.name = aggAller.date.strftime('%d/%m/%Y')
            elif aggAller.address_id:
                aggAller.name = aggAller.address_id.name + (" - "+aggAller.city if aggAller.city else "")
            else:
                aggAller.name = "/"
    
    def unlink(self):
        for aller in self:
            for history in aller.history_ids:
                history.unlink()
        return super(Aller, self).unlink()

    @api.model
    def create(self, vals):
        # CHECK IF MERGE NEEDED
        _logger.info("in create aller")
        agg_id = self.env["locasix.agg.aller"].search([("id", "=", vals["agg_id"])])
        vals["localite_id_depl"] = agg_id.localite_id_depl.id
        vals["is_depl"] = agg_id.is_depl
        vals["address_id"] = agg_id.address_id.id
        vals["localite_id"] = agg_id.localite_id.id
        vals["day_id"] = agg_id.day_id.id
        vals["date"] = agg_id.date
        obj = super(Aller, self).create(vals)
        obj.is_depl = obj.agg_id.is_depl
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
            if self.state == "zdone":
                pass
                #self.active = False
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
        elif state_key == "zdone":
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

class AllerCron(models.Model):
    _name = "locasix.aller.cron"
    _description = "Cron job to create allers"

    def create_aller(self, date):
        day_id = self.env["locasix.day"].search([("day", "=", date)], limit=1)
        if day_id:
            agg_id = self.env["locasix.agg.aller"].search([("is_first_agg", "=", True), ("day_id", "=", day_id.id)], limit=1)
            product_id = self.env["product.template"].search([("name", "=", "Produit aller")], limit=1)
            if not product_id:
                product_id = self.env["product.template"].create({
                    "name": "Produit aller",
                })
            if not agg_id:
                address_id = self.env["res.partner"].search([("name", "=", "Contact de configuration")], limit=1)
                if not address_id:
                    address_id = self.env["res.partner"].create({"name": "Contact de configuration"})
                
                localite_id = self.env["locasix.municipality"].search([("postal_code", "=", "0000")], limit=1)
                if not localite_id:
                    localite_id = self.env["locasix.municipality"].create({
                        "postal_code": "0000",
                        "city": "Commune de configuration",
                    })

                agg_id = self.env['locasix.agg.aller'].create({
                    "address_id": address_id.id,
                    "date": date,
                    "state": "progress",
                    "day_id": day_id.id,
                    "localite_id": localite_id.id,
                    "is_first_agg": True,
                })

            self.env["locasix.aller"].create({
                        'date': date,
                        "day_id": day_id.id,
                        "agg_id": agg_id.id,
                        'state': "a",
                        "product_id": product_id.product_variant_id.id,
                        "is_first_line": True,
            })

    def run_cron(self):
        _logger.info("CRON JOB Aller")
        today = datetime.date.today()
        max_limit = today + datetime.timedelta(days=363)
        min_limit = today - datetime.timedelta(days=30)
        
        # Automated archiving
        #min_limit = today - datetime.timedelta(days=15)
        #days_to_archived = self.env["locasix.day"].search([("day", '<', min_limit)])
        #for day in days_to_archived:
        #    day.active = False

        allers = self.env["locasix.aller"].search([('date', '>=', min_limit), ('date', '<', max_limit), ('is_first_line', '=', True)])
        sorted_days = sorted(allers, key=lambda day: day.date)
        new_day = min_limit
        i = 0
        while new_day < max_limit and i < len(sorted_days):
            sorted_days[i].state = "a"
            if sorted_days[i].date == new_day:
                i += 1
                new_day = new_day + datetime.timedelta(days=1)
            elif sorted_days[i].date < new_day:
                i += 1
            else:
                self.create_aller(new_day)
                new_day = new_day + datetime.timedelta(days=1)
        while new_day < max_limit:
            self.create_aller(new_day)
            new_day = new_day + datetime.timedelta(days=1)

        return      