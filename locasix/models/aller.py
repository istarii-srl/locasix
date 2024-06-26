from odoo import fields, api, models
from odoo.exceptions import UserError
from odoo.http import request
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
    _order = "state, postal_code, address_id"

    state = fields.Selection(string="Statut", selection=lambda self: self._state_selection(), default="aprogress", required=True)
    name = fields.Char(string="Nom", compute="_compute_name", store=True)
    day_id = fields.Many2one(comodel_name="locasix.day", string="Journée", required=True)
    date = fields.Date(string="Date", required=True)
    agg_id = fields.Many2one(comodel_name="locasix.agg.aller", required=True)
    
    aller_type = fields.Selection(string="type de livraison", selection=[("out", "Aller"), ("in", "Retour"), ("depl", "Déplacement")], default="out")
    aller_type_name = fields.Char(string="Type", store=True, compute="_compute_aller_type_name")
    color = fields.Integer(compute='_compute_color')

    is_first_line = fields.Boolean(default=False)


    order_id = fields.Many2one(string="Offre", comodel_name="sale.order")
    address_id = fields.Many2one(comodel_name="res.partner", string="Client", required=True)
    is_depl = fields.Boolean(string="Est un déplacement", default=False)
    is_proposition = fields.Boolean(string="Est une proposition", default=False)
    asking_prop_time = fields.Datetime(string="Date de la demande", default= lambda self: self.get_prop_time())
    asking_prop_time_date = fields.Date(string="Date demande", compute="_compute_asking_prop_time_date", store=True)
    asking_user = fields.Many2one(string="Demandeur", comodel_name="res.users", default=lambda self: self.env.user)
    proposition_status = fields.Selection(string="Statut de la proposition", selection=[("rejected", "Rejeté"), ("pending_boss", "En attente de confirmation du responsable"), ("pending_worker", "En attente de rectification du demandeur"), ("accepted", "Accepté")], default="pending_boss")

    postal_code = fields.Char(string="Postal code", related="localite_id.postal_code", store=True)
    localite_id = fields.Many2one(comodel_name="locasix.municipality", string="Localité")
    localite_id_depl = fields.Many2one(comodel_name="locasix.municipality", string="Localité arrivé déplacement")

    full_name = fields.Char(string="Nom du client ", related="address_id.display_name")
    displayed_client = fields.Char(string="Nom du client", compute="_compute_displayed_names")
    city = fields.Char(string="Ville ", compute="_compute_city", store=True)
    displayed_city = fields.Char(string="Ville", compute="_compute_displayed_names")
    contract = fields.Char(string="Contrat ")
    contract_id = fields.Many2one(string="Contrat", comodel_name="locasix.contract", domain="[('id', '=', -1)]")

    product_default_code = fields.Char(string="Ref", related="product_id.default_code")
    product_id = fields.Many2one(string="Produit", comodel_name="product.product", required=True)
    product_unique_ref = fields.Many2one(string="N°", comodel_name="locasix.product.ref")
    is_retour_created = fields.Boolean(string="Retour crée", default=False)
    inverse_aller_id = fields.Many2one(string="Aller inverse en cas d'aller/retour", comodel_name="locasix.aller")

    is_weekend = fields.Boolean(string="weekend", related="agg_id.is_weekend")

    history_ids = fields.One2many(string="Lignes de l'historique", comodel_name="locasix.aller.history.line", inverse_name="aller_id")
    remarque_ids = fields.Many2many(string="Remarques", comodel_name="locasix.remarque", default=lambda self: self.get_default_remarque())
    remarque_string = fields.Char(string="Remarques en charactères", compute="_compute_remarque_string")
    note = fields.Text(string="Remarque libre ")
    displayed_note = fields.Text(string="Remarque libre", compute="_compute_displayed_names")

    should_send_mail_to_assembler = fields.Boolean(string="Should send mail to assembler", compute="_compute_shoud_sent_mail_to_assembler")

    active = fields.Boolean(string="Actif", default=True)
    has_been_set_done = fields.Boolean(string="Déjà fini", default=False)


    def _compute_shoud_sent_mail_to_assembler(self):
        for aller in self:
            flag = False
            for remarque in aller.remarque_ids:
                if remarque.send_mail_to_assembler:
                    flag = True
            if aller.product_id and aller.product_id.should_notify_assembler:
                flag = True
            
            aller.should_send_mail_to_assembler = flag

    @api.depends("asking_prop_time")
    def _compute_asking_prop_time_date(self):
        for aller in self:
            date = datetime.date(aller.asking_prop_time.year, aller.asking_prop_time.month, aller.asking_prop_time.day)
            aller.asking_prop_time_date = date

    def _compute_remarque_string(self):
        for aller in self:
            txt = ""
            for remarque in aller.remarque_ids:
                txt += remarque.name + " "
            aller.remarque_string = txt 

    @api.depends("aller_type", "is_depl")
    def _compute_aller_type_name(self):
        for aller in self:
            if aller.is_depl:
                aller.aller_type_name = "Déplacement"
            else:
                if aller.aller_type == "out":
                    aller.aller_type_name = "Aller"
                else:
                    aller.aller_type_name = "Retour"

    def get_prop_time(self):
        return datetime.datetime.now()


    @api.constrains("date")
    def check_date_if_done(self):
        for aller in self:
            if aller.state == "zdone":
                raise UserError("Vous ne pouvez pas déplacer une ligne avec le statut fini !")

    def get_record_url(self):
        for aller in self:
            url = self.get_base_url()
            url += "/web#id="+str(aller.id)+"&model=locasix.aller&view_type=form&cids=1&menu_id=217"
            return f"<a href={url}>Lien vers l'enregistrement</a>"

    def get_default_remarque(self):
        for aller in self:
            if aller.agg_id and not aller.remarque_ids:
                return aller.agg_id.remarque_ids
            else:
                return False          

    @api.onchange("agg_id")
    def on_agg_id_changed_remarque(self):
        for aller in self:
            if aller.agg_id and not aller.remarque_ids:
                aller.remarque_ids = aller.agg_id.remarque_ids

    @api.onchange("product_id")
    def on_product_changed(self):
        for aller in self:
            if aller.product_id.is_assemblage_product:
                remarques = self.env["locasix.remarque"].search([("is_montage", "=", True)])
                for rem in remarques:
                    aller.remarque_ids = [(4,rem.id)]

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

    @api.constrains("state", "is_proposition")
    def not_done_if_not_admin(self):
        for aller in self:
            if aller.state == "zdone" and not self.env.user.has_group('locasix.group_locasix_admin'):
                raise UserError("Seul les administrateurs peuvent mettre une ligne à 'fini' !")
            elif aller.has_been_set_done and not self.env.user.has_group('locasix.group_locasix_admin'):
                raise UserError("Seul les administrateurs peuvent changer le statut d'une ligne finie !")
            if aller.state == "zzprop" and not aller.is_proposition:
                raise UserError("Le statut 'proposition' ne peut pas être changé manuellement")
            if aller.state != "zzprop" and aller.is_proposition and aller.proposition_status != "accepted":
                raise UserError("Le statut 'proposition' ne peut pas être changé manuellement")

    def _state_selection(self):
        select = [("aprogress", "En cours"), ("cancel", "Annulé"), ("move", "Déplacé"), ('a', "Statut technique")]
        #if self.env.user.has_group('locasix.group_locasix_admin'):
        select.append(('zdone', "Fini"))
        select.append(("zzprop", "Proposition"))
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
        vals["aller_type"] = agg_id.aller_type
        vals["address_id"] = agg_id.address_id.id
        vals["localite_id"] = agg_id.localite_id.id
        vals["day_id"] = agg_id.day_id.id
        vals["is_proposition"] = agg_id.is_proposition
        if agg_id.is_proposition:
            vals["state"] = "zzprop"
        vals["date"] = agg_id.date
        obj = super(Aller, self).create(vals)
        if not obj.remarque_ids:
            obj.remarque_ids = obj.agg_id.remarque_ids
        obj.is_depl = obj.agg_id.is_depl
        if obj.is_proposition:
            obj.create_history_message("Création de la proposition")
            if obj.agg_id.prop_mail_sent:
                obj.send_creation_mail()
        else:
            obj.create_history_message("Création de l'aller")
        return obj

    def write(self, vals):
        _logger.info("write Aller")
        _logger.info(vals)
        old_state = self.state
        old_date = self.date
        old_note = self.note
        old_address_id = self.address_id
        old_localite_depl = self.localite_id_depl
        old_localite = self.localite_id
        old_prop_status = self.proposition_status
        old_product = self.product_id
        old_ref = self.product_unique_ref
        old_contract = self.contract_id
        from_inverse = vals.pop("from_inverse", False)
        res = super(Aller, self).write(vals)
        if "note" in vals:
            if old_note == self.note:
                pass
            elif old_note and self.note:
                self.create_history_message("Changement de la remarque libre : "+old_note+" -> "+self.note)
            elif old_note:
                self.create_history_message("Changement de la remarque libre : "+old_note+" -> pas de remarque")
            elif self.note:
                self.create_history_message("Changement de la remarque libre : "+ "pas de remarque -> "+self.note)
        if "remarque_ids" in vals:
            self.create_history_message("Une ou plusieurs remarques ont été modifiés")

        if "localite_id_depl" in vals:
            if old_localite_depl and self.localite_id_depl and old_localite_depl.id == self.localite_id_depl.id:
                pass
            elif old_localite_depl and self.localite_id_depl :
                self.create_history_message("Changement de l'addresse d'arrivée du déplacement : "+old_localite_depl.name+" -> "+self.localite_id_depl.name)
            elif old_localite_depl:
                self.create_history_message("Changement de l'addresse d'arrivée du déplacement : "+old_localite_depl.name+" -> Aucune addresse")
            elif self.localite_id_depl:
                self.create_history_message("Changement de l'addresse d'arrivée du déplacement : Aucune addresse -> "+self.localite_id_depl.name)    

        if "localite_id" in vals:
            if old_localite and self.localite_id and old_localite.id == self.localite_id.id:
                pass
            elif old_localite and self.localite_id:
                self.create_history_message("Changement de l'addresse : "+old_localite.name+" -> "+self.localite_id.name)
            elif old_localite:
                self.create_history_message("Changement de l'addresse : "+old_localite.name+" -> Aucune addresse")
            elif self.localite_id:
                self.create_history_message("Changement de l'addresse : Aucune addresse -> "+self.localite_id.name)            
        
        if "address_id" in vals:
            if old_address_id and self.address_id and old_address_id.id == self.address_id.id:
                pass
            elif old_address_id and self.address_id:
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
            if str(self.state_to_string(old_state)) == str(self.state_to_string(self.state)):
                pass
            else:
                self.create_history_message("Changement de statut : "+str(self.state_to_string(old_state))+" -> "+str(self.state_to_string(self.state)))
            if self.state == "zdone":
                self.has_been_set_done = True
            else:
                self.has_been_set_done = False
                #self.active = False
        if "contract_id" in vals:
            if self.contract_id and old_contract:
                self.create_history_message("Changement de contrat : "+ old_contract.name +" -> "+ self.contract_id.name)
            elif self.contract_id:
                self.create_history_message("Changement de contrat : "+ "Pas de contrat" +" -> "+ self.contract_id.name)
            elif old_contract:
                self.create_history_message("Changement de contrat : "+ old_contract.name +" -> "+ "Pas de contrat")
        if "proposition_status" in vals:
            self.create_history_message("Changement de statut pour la proposition : "+self.prop_status_to_string(old_prop_status)+" -> "+ self.prop_status_to_string(self.proposition_status))
        if "product_unique_ref" in vals:
            if old_ref and self.product_unique_ref and old_ref.name == self.product_unique_ref:
                pass
            elif old_ref == self.product_unique_ref:
                pass
            else:
                self.create_history_message("Changement du N° : "+ (old_ref.name if old_ref else "Pas de numéro") +" -> "+ (self.product_unique_ref.name if self.product_unique_ref else "Pas de numéro"))
        if "product_id" in vals:
            if not old_product or not self.product_id or old_product.id != self.product_id.id:
                self.create_history_message("Changement du produit° : "+ (old_product.name if old_product else "Pas de produit") +" -> "+ (self.product_id.name if self.product_id else "Pas de produit"))
        
        if self.inverse_aller_id and not from_inverse and any(name in vals for name in ['product_unique_ref', 'proposition_status', 'product_id', 'contract_id', 'address_id', 'localite_id', 'note', 'remarque_ids', 'localite_id_depl']) :
            self.inverse_aller_id.write({
                'from_inverse': True, 'product_unique_ref': self.product_unique_ref,
                'proposition_status': self.proposition_status, 'product_id': self.product_id.id,
                'contract_id': self.contract_id.id, 'address_id': self.address_id.id,
                'localite_id': self.localite_id.id, 'note': self.note,
                'remarque_ids': self.remarque_ids.ids, 'localite_id_depl': self.localite_id_depl.id,
                })


        return res

    def prop_status_to_string(self, status):
        if status == "accepted":
            return "Accepté"
        elif status == "rejected":
            return "Refusé"
        elif status == "pending_boss":
            return "En attente de confirmation du responsable"
        else:
            return "En attente de rectification du demandeur"

    def state_to_string(self, state_key):
        if state_key == "aprogress":
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
                "contract_id": aller.contract_id.id,
                "product_id": aller.product_id.id,
                "product_unique_ref": aller.product_unique_ref.id,
                "note": aller.note,
            })
            for remarque in aller.remarque_ids:
                new_aller.remarque_ids = [(4, remarque.id, 0)]
    
    def action_accept(self):
        j = 0
        agg_id = False
        for aller in self:
            j += 1
            if not agg_id:
                agg_id = aller.agg_id.id
            elif agg_id != aller.agg_id.id:
                raise UserError("Vous ne pouvez accepter des propositions que d'un même groupement")
            if aller.proposition_status != "pending_boss":
                raise UserError("Vous ne pouvez accepter que les propositions en attente de confirmation du responsable")


        mail_values = {
            'subject': f"Proposition acceptée",
            'email_to': f"{aller.asking_user.email}",
            'date': datetime.datetime.now(),
            'auto_delete': False,
            'email_from': self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') if self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') else "o.libbrecht@locasix.be",
        }

        body = f"Bonjour,"
        for aller in self:
            aller.proposition_status = "accepted"
            aller.state = "aprogress"
            self.create_history_message("Proposition acceptée")
            
            type_aller = "Aller" if aller.aller_type == "out" else "Retour"
            if aller.is_depl:
                type_aller = "Déplacement"
            note = aller.note if aller.note else ""
            body += f"<br/><br/>Votre proposition {aller.name} a été acceptée. <br/>Type de proposition : {type_aller}<br/>Date : {aller.date}<br/>Lien : {aller.get_record_url()} <br/><br/>Remarque: {aller.remarque_string}<br/>Remarque libre:{note}"

        if j > 0:
            batch_mails_sudo = self.env['mail.mail'].sudo()
            body += "<br/><br/>Cordialement,"
            mail_values['body_html'] = body
            batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
            batch_mails_sudo.send(auto_commit=False)  

    def action_reject(self):
        j = 0
        agg_id = False
        for aller in self:
            j+= 1
            if not agg_id:
                agg_id = aller.agg_id.id
            elif agg_id != aller.agg_id.id:
                raise UserError("Vous ne pouvez rejeter des propositions que d'un même groupement")
            if aller.proposition_status != "pending_boss":
                raise UserError("Vous ne pouvez rejeter que les propositions en attente de confirmation du responsable")

        mail_values = {
            'subject': f"Proposition refusée",
            'email_to': f"{aller.asking_user.email}",
            'date': datetime.datetime.now(),
            'auto_delete': False,
            'email_from': self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') if self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') else "o.libbrecht@locasix.be",
        }
        body = f"Bonjour,"
        for aller in self:
            aller.proposition_status = "rejected"
            self.create_history_message("Proposition refusée")
            type_aller = "Aller" if aller.aller_type == "out" else "Retour"
            if aller.is_depl:
                type_aller = "Déplacement"
            note = aller.note if aller.note else ""
            body += f"<br/><br/>Votre proposition {aller.name} a été refusée. <br/>Type de proposition : {type_aller}<br/>Date : {aller.date}<br/>Lien : {aller.get_record_url()}<br/><br/>Remarque: {aller.remarque_string}<br/>Remarque libre:{note} <br/><br/>Cordialement,"

            aller.active = False

        if j > 0:
            batch_mails_sudo = self.env['mail.mail'].sudo()
            body += "<br/><br/>Cordialement,"
            mail_values['body_html'] = body
            batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
            batch_mails_sudo.send(auto_commit=False)  

    def action_ask_changes(self):
        for aller in self:
            _logger.info("action in prop status")
            view = self.env.ref('locasix.locasix_prop_status_form_confirmation')
            return {
            'name': 'Changer le statut de la proposition',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'locasix.prop.status.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                "default_aller_id": aller.id,
                "default_is_asking_confirmation": False,
                "default_is_depl": aller.is_depl,
                "default_address_id": aller.address_id.id,
                "default_date": aller.date,
                "default_product_id": aller.product_id.id,
                "default_product_unique_ref": aller.product_unique_ref.id,
                "default_contract_id": aller.contract_id.id,
                "default_localite_id": aller.localite_id.id,
                "default_localite_id_depl": aller.localite_id_depl.id,
                },
            }

    def ask_changes(self, note, i=0):
        for aller in self:
            aller.proposition_status = "pending_worker" 
            self.create_history_message("Demande de changements : "+ note)
            if i == 0:
                batch_mails_sudo = self.env['mail.mail'].sudo()
                type_aller = "Aller" if aller.aller_type == "out" else "Retour"
                if aller.is_depl:
                    type_aller = "Déplacement"
                #note = aller.note if aller.note else ""
                mail_values = {
                    'subject': f"Demande de changement",
                    'date': datetime.datetime.now(),
                    'body_html': f"Bonjour,<br/><br/>Concernant votre proposition {aller.name}, des changements doivent être apportés. <br/>Type de proposition : {type_aller}<br/>Date : {aller.date} <br/><br/>Remarque: {aller.remarque_string}<br/>Remarque libre:{note} <br/>Lien : {aller.get_record_url()}  <br/><br/>Cordialement,",
                    'email_to': f"{aller.asking_user.email}",
                    'auto_delete': False,
                    'email_from': self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') if self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') else "o.libbrecht@locasix.be",
                }
                batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
                batch_mails_sudo.send(auto_commit=False)
                return ""
            else:
                type_aller = "Aller" if aller.aller_type == "out" else "Retour"
                if aller.is_depl:
                    type_aller = "Déplacement"
                note = aller.note if aller.note else ""
                body = f"<br/><br/>Concernant votre proposition {aller.name}, des changements doivent être apportés. <br/>Type de proposition : {type_aller}<br/>Date : {aller.date} <br/><br/>Remarque: {aller.remarque_string}<br/>Remarque libre:{note} <br/>Lien : {aller.get_record_url()}"
                return body

    def action_ask_confirmation(self):
        for aller in self:
            _logger.info("action in prop status")
            view = self.env.ref('locasix.locasix_prop_status_form_confirmation')
            return {
            'name': 'Changer le statut de la proposition',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'locasix.prop.status.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                "default_aller_id": aller.id,
                "default_is_asking_confirmation": True,
                "default_is_depl": aller.is_depl,
                "default_address_id": aller.address_id.id,
                "default_date": aller.date,
                "default_product_id": aller.product_id.id,
                "default_product_unique_ref": aller.product_unique_ref.id,
                "default_contract_id": aller.contract_id.id,
                "default_localite_id": aller.localite_id.id,
                "default_localite_id_depl": aller.localite_id_depl.id,
                },
            }


    def send_creation_mail(self):
        _logger.info("SEND PROP ALLER")
        for aller in self:
            batch_mails_sudo = self.env['mail.mail'].sudo()
            type_aller = "Aller" if aller.aller_type == "out" else "Retour"
            if aller.is_depl:
                type_aller = "Déplacement"
            from_email = aller.asking_user.email if aller.asking_user.email else "b.quintart@locasix.be"
            note = aller.note if aller.note else ""
            mail_values = {
                'subject': f"Demande de confirmation",
                'date': datetime.datetime.now(),
                'body_html': f"Bonjour,<br/><br/>Une demande de confirmation pour la proposition {aller.name} a été introduite par {aller.asking_user.name}<br/>Type de proposition : {type_aller}<br/>Date : {aller.date}<br/>Lien : {aller.get_record_url()} <br/><br/>Remarque: {aller.remarque_string}<br/>Remarque libre:{note}  <br/><br/>Cordialement,",
                'email_to': self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') if self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') else "o.libbrecht@locasix.be",
                'auto_delete': False,
                'email_from': from_email,
            }
            batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
            batch_mails_sudo.send(auto_commit=False)

            if aller.should_send_mail_to_assembler:
                batch_mails_sudo = self.env['mail.mail'].sudo()
                type_aller = "Aller" if aller.aller_type == "out" else "Retour"
                if aller.is_depl:
                    type_aller = "Déplacement"
                from_email = aller.asking_user.email if aller.asking_user.email else "b.quintart@locasix.be"
                note = aller.note if aller.note else ""
                mail_values = {
                    'subject': f"Demande de confirmation",
                    'date': datetime.datetime.now(),
                    'body_html': f"Bonjour,<br/><br/>Une demande de confirmation pour la proposition {aller.name} a été introduite par {aller.asking_user.name}<br/>Type de proposition : {type_aller}<br/>Date : {aller.date}<br/><br/>Remarque: {aller.remarque_string}<br/>Remarque libre:{note}  <br/><br/>Cordialement,",
                    'email_to': self.env['ir.config_parameter'].sudo().get_param('locasix.email_assembling_handler') if self.env['ir.config_parameter'].sudo().get_param('locasix.email_assembling_handler') else "o.libbrecht@locasix.be",
                    'auto_delete': False,
                    'email_from': from_email,
                }
                batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
                batch_mails_sudo.send(auto_commit=False)



    
    def ask_confirmation(self, note, i=0):
        for aller in self:
            aller.proposition_status = "pending_boss"
            self.create_history_message("Demande de confirmation : "+ note)
            type_aller = "Aller" if aller.aller_type == "out" else "Retour"
            if aller.is_depl:
                type_aller = "Déplacement"
            if i == 0:
                batch_mails_sudo = self.env['mail.mail'].sudo()
                from_email = aller.asking_user.email if aller.asking_user.email else "b.quintart@locasix.be"
                #note = aller.note if aller.note else ""
                mail_values = {
                    'subject': f"Demande de confirmation",
                    'date': datetime.datetime.now(),
                    'body_html': f"Bonjour,<br/><br/>Une demande de confirmation pour la proposition {aller.name} a été introduite par {aller.asking_user.name}<br/>Type de proposition : {type_aller}<br/>Date : {aller.date}<br/>Lien : {aller.get_record_url()}<br/><br/>Remarque: {aller.remarque_string}<br/>Remarque libre:{note}  <br/><br/>Cordialement,",
                    'email_to': self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') if self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') else "o.libbrecht@locasix.be",
                    'auto_delete': False,
                    'email_from': from_email,
                }
                batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
                batch_mails_sudo.send(auto_commit=False)
            else:

                body = f"la proposition {aller.name} a été modifiée par {aller.asking_user.name}<br/>Type de proposition : {type_aller}<br/>Date : {aller.date}<br/>Lien : {aller.get_record_url()}<br/><br/>Remarque: {aller.remarque_string}<br/>Remarque libre:{note}"
                return body

    def open_agg(self):
        view = self.env.ref('locasix.locasix_agg_aller_form')
        name = "Allers"
        if self.is_depl:
            view = self.env.ref('locasix.locasix_agg_depl_form')
            name = "Déplacements"
        elif self.aller_type == "in":
            view = self.env.ref('locasix.locasix_agg_retour_form')
            name = "Retours"

        return {
        'name': name,
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
                    "state": "aprogress",
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
            if sorted_days[i].state != "a":
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

    def run_cron_migrate(self):
        _logger.info("migrate cron")
        allers = self.env["locasix.aller"].search([])
        for aller in allers:
            if aller.state == "progress":
                aller.state = "aprogress" 
        aggs = self.env["locasix.agg.aller"].search([])
        for agg in aggs:
            agg.state = "aprogress"  