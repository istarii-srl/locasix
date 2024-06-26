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
    aller_type = fields.Selection(string="type de livraison", selection=[("out", "Aller"), ("in", "Retour")], default="out")

    address_id = fields.Many2one(comodel_name="res.partner", string="Client", required=True)
    localite_id = fields.Many2one(comodel_name="locasix.municipality", string="Localité")
    localite_id_depl = fields.Many2one(comodel_name="locasix.municipality", string="Localité arrivé déplacement")
    is_depl = fields.Boolean(string="Est un déplacement", default=False)
    is_proposition = fields.Boolean(string='Est une proposition', default=False)

    city = fields.Char(string="Ville", compute="_compute_city", store=True)
    contract = fields.Char(string="Contrat")
    remarque_ids = fields.Many2many(string="Remarques", comodel_name="locasix.remarque")
    note = fields.Text(string="Remarque libre")
    state = fields.Selection(string='Statut', selection=[("aprogress", "En cours")], default="aprogress", required=True)
    aller_ids = fields.One2many(comodel_name="locasix.aller", string="Allers", inverse_name="agg_id")

    is_weekend = fields.Boolean("Weekend", default=False)
    date_retour = fields.Datetime(string="Date de retour", default=lambda self: self._get_default_date())
    is_retours_created = fields.Boolean(default=False)
    is_first_agg = fields.Boolean(default=False)

    prop_mail_sent = fields.Boolean(string="Prop mail sent")

    should_send_mail_to_assembler = fields.Boolean(string="Should send mail to assembler", compute="_compute_shoud_sent_mail_to_assembler")

    is_waiting_worked_modif = fields.Boolean(string="Is waiting for worked modif", compute="_compute_is_waiting_worked_modif")

    def _compute_is_waiting_worked_modif(self):
        for agg_aller in self:
            flag = False
            for aller in agg_aller.aller_ids:
                if aller.proposition_status == "pending_worker" and aller.is_proposition:
                    flag = True
            agg_aller.is_waiting_worked_modif = flag
    
    def _compute_shoud_sent_mail_to_assembler(self):
        for aller in self:
            flag = False
            for remarque in aller.remarque_ids:
                if remarque.send_mail_to_assembler:
                    flag = True
            
            for line in aller.aller_ids:
                if line.product_id and line.product_id.should_notify_assembler:
                    flag = True
            
            aller.should_send_mail_to_assembler = flag


    @api.onchange("aller_type")
    def on_aller_type_changed(self):
        for aller in self:
            if aller.aller_type != "out":
                aller.is_depl = False

    def _get_default_date(self):
        return datetime.date.today()

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

    def update_proposition(self):
        for agg_aller in self:
            waiting_prop = agg_aller.aller_ids.filtered(lambda x: x.proposition_status == "pending_worker")
            if waiting_prop:
                from_email = waiting_prop.asking_user.email if waiting_prop.asking_user.email else "b.quintart@locasix.be"
                mail_values = {
                    'subject': f"Demande de confirmation",
                    'email_to': self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') if self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') else "o.libbrecht@locasix.be",
                    'auto_delete': False,
                    'email_from': from_email,
                }
                body = "Bonjour,<br/><br/>"

                for prop in agg_aller.aller_ids:
                    prop.date = agg_aller.date
                    body += prop.ask_confirmation(" ", 1)

                body += "<br/><br/>Cordialement,"
                mail_values["body_html"] = body
                batch_mails_sudo = self.env['mail.mail'].sudo()
                batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
                batch_mails_sudo.send(auto_commit=False)

    # TODO USE THAT IN WRITE AND CREATE
    def check_and_merge(self):
        for agg_aller in self:
            aggs = self.env["locasix.agg.aller"].search([("date", '=', agg_aller.date), ("address_id", "=", agg_aller.address_id.id), ("id", '!=', agg_aller.id), ("aller_type", "=", agg_aller.aller_type), ("is_depl", "=", agg_aller.is_depl), ("localite_id", "=", agg_aller.localite_id.id)])
            for other_agg in aggs:
                if other_agg.is_retours_created:
                    agg_aller.is_retours_created = True
                    agg_aller.is_weekend = True
                    agg_aller.date_retour = other_agg.date_retour
                for other_aller in other_agg.aller_ids:
                    other_aller.agg_id = agg_aller
                allers = self.env["locasix.aller"].search([("active", "=", False), ('agg_id', "=", other_agg.id)])
                for aller in allers:
                    aller.unlink()
                other_agg.unlink()
        return
 
    def weekend_check(self):
        for agg_aller in self:
            if agg_aller.date_retour and not agg_aller.is_retours_created and agg_aller.address_id and agg_aller.is_weekend:
                agg_retour_id = self.env["locasix.agg.aller"].search([("date", "=", agg_aller.date_retour), ("address_id", "=", agg_aller.address_id.id), ("aller_type", "=", "in"), ("is_depl", "=", False), ("localite_id", "=", agg_aller.localite_id.id)], limit=1)
                if not agg_retour_id:
                    newday_id = self.env["locasix.day"].search([("day", "=", agg_aller.date_retour)], limit=1)
                    if not newday_id:
                        newday_id = self.env["locasix.day"].create({"day": agg_aller.date_retour})
                    agg_retour_id = self.env["locasix.agg.aller"].create({
                        "day_id": newday_id.id,
                        "aller_type": "in",
                        "is_weekend": True,
                        "localite_id": agg_aller.localite_id.id,
                        "date": agg_aller.date_retour,
                        "address_id": agg_aller.address_id.id,
                    })
                for aller in agg_aller.aller_ids:
                    if not aller.is_retour_created: 
                        retour = self.env["locasix.aller"].create({
                        "day_id": agg_retour_id.day_id.id,
                        "aller_type": "in",
                        "is_retour_created": True,
                        "inverse_aller_id": aller.id,
                        "date": agg_retour_id.date,
                        "agg_id": agg_retour_id.id,
                        "localite_id": aller.localite_id.id,
                        "address_id": aller.address_id.id,
                        "contract_id": aller.contract_id.id,
                        "product_id": aller.product_id.id,
                        "product_unique_ref": aller.product_unique_ref.id,
                        "note": aller.note,
                    })
                        aller.is_retour_created = True
                        aller.inverse_aller_id = retour
                        for remarque in aller.remarque_ids:
                            retour.remarque_ids = [(4, remarque.id, 0)]     
                #agg_aller.is_retours_created = True                                   

    @api.model
    def create(self, vals):
        obj = super(AggAller, self).create(vals)
        obj.enforce_day_matches_date()
        obj.check_and_merge()
        obj.weekend_check()
        obj.send_proposition_creation_mail()
        return obj
    
    def send_proposition_creation_mail(self):
        _logger.info("SEND PROP AGG")
        for agg_aller in self:
            if agg_aller.is_proposition and len(agg_aller.aller_ids) > 0 and not agg_aller.prop_mail_sent:
                mail_values = {
                        'subject': f"Demande de confirmation",
                        'date': datetime.datetime.now(),
                        'email_to': self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') if self.env['ir.config_parameter'].sudo().get_param('locasix.email_shipping_handler') else "o.libbrecht@locasix.be",
                        'auto_delete': False,
                        'email_from': agg_aller.aller_ids[0].asking_user.email if agg_aller.aller_ids[0].asking_user.email else "b.quintart@locasix.be",
                    }
                body = "Bonjour,"
                for aller in agg_aller.aller_ids:
                
                    type_aller = "Aller" if aller.aller_type == "out" else "Retour"
                    if aller.is_depl:
                        type_aller = "Déplacement"
                    #from_email = aller.asking_user.email if aller.asking_user.email else "b.quintart@locasix.be"
                    note = aller.note if aller.note else ""
                    body += f"<br/><br/>Une demande de confirmation pour la proposition {aller.name} a été introduite par {aller.asking_user.name}<br/>Type de proposition : {type_aller}<br/>Date : {aller.date}<br/>Lien : {aller.get_record_url()} <br/><br/>Remarque: {aller.remarque_string}<br/>Remarque libre:{note}"

                body += "<br/><br/>Cordialement,"
                mail_values["body_html"] = body
                batch_mails_sudo = self.env['mail.mail'].sudo()
                batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
                batch_mails_sudo.send(auto_commit=False)
                agg_aller.prop_mail_sent = True 
            
                if agg_aller.should_send_mail_to_assembler:
                    mail_values = {
                            'subject': f"Demande de confirmation",
                            'date': datetime.datetime.now(),
                            'email_to': self.env['ir.config_parameter'].sudo().get_param('locasix.email_assembling_handler') if self.env['ir.config_parameter'].sudo().get_param('locasix.email_assembling_handler') else "o.libbrecht@locasix.be",
                            'auto_delete': False,
                            'email_from': agg_aller.aller_ids[0].asking_user.email if agg_aller.aller_ids[0].asking_user.email else "b.quintart@locasix.be",
                        }
                    body = "Bonjour,"
                    for aller in agg_aller.aller_ids:
                    
                        type_aller = "Aller" if aller.aller_type == "out" else "Retour"
                        if aller.is_depl:
                            type_aller = "Déplacement"
                        #from_email = aller.asking_user.email if aller.asking_user.email else "b.quintart@locasix.be"
                        note = aller.note if aller.note else ""
                        body += f"<br/><br/>Une demande de confirmation pour la proposition {aller.name} a été introduite par {aller.asking_user.name}<br/>Type de proposition : {type_aller}<br/>Date : {aller.date} <br/><br/>Remarque: {aller.remarque_string}<br/>Remarque libre:{note}"

                    body += "<br/><br/>Cordialement,"
                    mail_values["body_html"] = body
                    batch_mails_sudo = self.env['mail.mail'].sudo()
                    batch_mails_sudo |= self.env['mail.mail'].sudo().create(mail_values)
                    batch_mails_sudo.send(auto_commit=False)
                    agg_aller.prop_mail_sent = True 

    def enforce_day_matches_date(self):
        if self.date != self.day_id.day:
            newday_id = self.env["locasix.day"].search([("day", "=", self.date)], limit=1)
            if not newday_id:
                newday_id = self.env["locasix.day"].create({"day": self.date})
            
            self.day_id = newday_id
            for aller in self.aller_ids:
                aller.day_id = newday_id
                aller.date = self.date        

    def write(self, vals):
        _logger.info("write aggAller")
        _logger.info(vals)
        res = super(AggAller, self).write(vals)
        if "date" in vals:
            if self.date != self.day_id.day:
                self.enforce_day_matches_date()
                self.check_and_merge()
        if "address_id" in vals or "localite_id" in vals or "localite_id_depl" in vals:
            if self.date == self.day_id.day:
                for aller in self.aller_ids:
                    aller.localite_id = self.localite_id
                    aller.address_id = self.address_id
                    aller.localite_id_depl = self.localite_id_depl
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
                "is_depl": aggAller.is_depl,
                "localite_id": aggAller.localite_id.id,
                "localite_id_depl": aggAller.localite_id_depl.id,
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


    def action_archive(self):
        for agg in self:
            for aller in agg.aller_ids:
                aller.active = False


    def action_validate(self):
        return

