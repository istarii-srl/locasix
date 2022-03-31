from email.policy import default
from odoo import fields, api, models


import logging
_logger = logging.getLogger(__name__)

class Order(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    front_page_body = fields.Html(string="Page de garde", default=lambda self: self._get_front_page())
    front_page_body_template = fields.Char(string="Page de garde template") 

    added_terms_id = fields.Many2one(string="Liste de conditions additionnelles", comodel_name="locasix.template.html", domain=['|', ("id", "=", False), ("is_condi_add", "=", True)])
    added_terms_template = fields.Html(string="Conditions additionnelles ")
    added_terms = fields.Html(string="Conditions additionnelles", default=lambda self: self._get_added_terms())
    added_terms_week_end = fields.Html(string="Conditions additionnelles de week-end", default=lambda self: self._get_added_terms_weekend())
    added_terms_sale = fields.Html(string="Conditions additionnelles de vente", default=lambda self: self._get_added_terms_sale())
    electro_annexe = fields.Html(string="Annexe groupes électrogènes", default=lambda self: self._get_electro_annexe())
    sale_confirm = fields.Html(string="Confirmation de la commande", default=lambda self: self._get_sale_confirm())
    sale_confirm_template = fields.Char(string="Confirmation de la commande template") 
    
    offer_type = fields.Selection(string="Type d'offre", selection=[("classic", "Location"), ("weekend", "Weekend"), ("sale", "Vente")], default="classic", required=True)
    usage_rate_display = fields.Selection(string="Affichage des tarifs", selection=[('24', "Afficher les tarifs 24h"), ('8', "Afficher les tarifs 8h"), ("duo", "Afficher les deux tarifs")], default="8", required=True)
    show_discount2 = fields.Boolean(string="Afficher remise 2 mois", default=False)
    show_discount3 = fields.Boolean(string="Afficher remise 3 mois", default=False)
    show_discount6 = fields.Boolean(string="Afficher remise 6 mois", default=False)

    months_2_discount_rate = fields.Float(string="G.E. 2 mois", default=0.10)
    months_3_discount_rate = fields.Float(string="G.E. 3 mois", default=0.15)
    months_6_discount_rate = fields.Float(string="G.E. 6 mois", default=0.2)

    date_aller = fields.Char(string="Date aller")
    date_retour = fields.Char(string="Date retour")

    city = fields.Many2one(string="Ville", comodel_name="locasix.municipality")
    rue = fields.Char(string="Rue")
    street_number = fields.Char(string="Numéro")
    street_note = fields.Char(string="Remarque libre")

    done_order = fields.Boolean(string="Offre terminée", default=False)
    is_computing = fields.Boolean(string="En cours de calculation", default=False)
    has_computed = fields.Boolean(string="Y a t-il eu une calculation ?", default=False)
    exported_to_agenda = fields.Boolean(default=False)

    aller_ids = fields.One2many(string="Allers", comodel_name="locasix.aller", inverse_name="order_id", domain=[('aller_type', '=', 'out')])
    aller_count = fields.Integer(compute="_compute_aller_count")
    retour_ids = fields.One2many(string="Retours", comodel_name="locasix.aller", inverse_name="order_id", domain=[('aller_type', '=', 'in')])
    retour_count = fields.Integer(compute="_compute_retour_count")

    client_ref = fields.Char(string="Votre référence")

    space_between_sections = fields.Selection(string="Espace entre les sections", selection=[('small', 'Petit'), ('medium', 'Moyen'), ('large', 'Grand')], default="medium");
    has_extra_cost_transport = fields.Boolean(default=False)
    extra_cost_transport_rate = fields.Float(default=0)
    visual_discounts = fields.Boolean(string="Afficher les réductions", default=False)

    display_front_page = fields.Boolean(string="Afficher la page de garde", default=True)
    display_confirmation_box = fields.Boolean(string="Afficher l'encadré de confirmation", default=True)


    @api.onchange("added_terms_id")
    def on_added_terms_changed(self):
        for order in self:
            if order.added_terms_id:
                order.added_terms_template = order.added_terms_id.template
            else:
                order.added_terms_template = False

    def get_transport_address(self):
        for order in self:
            text = ""
            if order.rue:
                text += order.rue + " "
            if order.street_number:
                text += order.street_number + ", "
            if order.city:
                text += order.city.postal_code+ " "+order.city.city+", "
                if order.city.postal_code == "FR":
                    text += "France"
                else:
                    text += "Belgique"
            if order.street_note:
                text+= " : "+order.street_note
            return text

    def _get_electro_annexe(self):
        #template = self.env["locasix.template.html"].search([('name', '=', 'Template annexe groupes électrogènes')], limit=1)
        template = self.env.ref("locasix.locasix_template_electro")
        if template:
            return template.template
        else:
            return "<p>Nous portons à votre connaissance que nous n’avons pas de service de dépannage organisé durant les weekends (Du vendredi 16h00 jusqu’au lundi 07h00).</p><p><br></p><p>Notre expérience nous démontre que les problèmes qui surviennent sont généralement : </p><ul><li><p>Soit une panne par manque de gasoil </p></li><li><p>Soit un acte de malveillance. </p></li></ul><p>Nous constatons également qu’entre le moment où le technicien est informé du problème et le dépannage sur site (Ou encore remplacement de la machine), plusieurs heures sont parfois nécessaires. </p><p><br></p><p>Aussi, pour palier à ces inconvénients et vous protéger contre tout problème qui pourrait surgir, nous vous proposons la location d’un second groupe électrogène ou mât d'éclairage en réserve (Sous réserve des stocks disponibles). </p><p><br></p><p>Cette deuxième machine (Sous réserve qu’elle n’ait pas été utilisée) serait facturée à 50 \% du prix de la première. Si cette proposition vous intéresse, merci de nous en informer. </p><p><br></p><p>Cette démarche ne nous empêche nullement de toujours faire le maximum pour vous servir un matériel en parfait état de fonctionnement.<br></p>"
    def _get_sale_confirm(self):
        #template = self.env["locasix.template.html"].search([('name', '=', 'Template confirmation de commande')], limit=1)
        template = self.env.ref("locasix.locasix_template_confirm_sale")
        if template:
            return template.template
        else:
            return "<span style='font-size:10px'><b>Confirmation de la commande :</b><br>Veuillez nous retourner toutes les pages de l'offre paraphées ainsi que cette page signée avec la mention<br>\"Bon pour accord\" + le cachet de l'entreprise.</span>"

    def _get_added_terms_sale(self):
        #template = self.env["locasix.template.html"].search([('name', '=', 'Template conditions additionnelles de vente')], limit=1)
        template = self.env.ref("locasix.locasix_template_condi_sale")
        if template:
            return template.template
        else:
            return "<span><b style='font-size:11px;'>Conditions de location</b></span><ul><li style='margin:0px;'><span>Prix hors TVA 21%.</span></li><li style='margin:0px;'><span>Facturation minimale de 28 jours.</span></li><li style='margin:0px;'><span>Si annulation de la commande dans les 48H avant la date de livraison, des frais de dossier de 50,00€ par pièce vous seront facturés.</span></li><li style='margin:0px;'><span>Si demande de retour impératif à une date précise, les frais de transport seront majorés de 30%.</span></li><li style='margin:0px;'><span>Une caution peut vous être demandée avant la livraison.</span></li><li style='margin:0px;'><span><u>Si location de groupes électrogènes et/ou mâts d'éclairage :</u></span><ul><li style='margin:0px;'><span>Entretien journalier : carburant, niveau d'huile, niveau d'eau ... à votre charge.</span></li><li style='margin:0px;'><span>Entretien périodique comprenant filtres, huile ... à notre charge.</span></li><li style='margin:0px;'><span>Service de dépannage assuré uniquement du lundi au vendredi de 7h à 16h.</span></li></ul></li><li style='margin:0px;'><span>Délai : à convenir et suivant disponibilité.</span></li><li style='margin:0px;'><span>Validité de l'offre : 30 jours.</span></li><li style='margin:0px;'><span>Tous raccordements électriques et raccordements à l'alimentation en eau sont à votre charge.</span></li><li style='margin:0px;'><span>Voir conditions détaillées en dernière page.<br></span></li></ul><span><br></span><span><b style='font-size:11px;'><br/>Transport<br/></b></span><span>Transport et déchargement de l'ensemble repris ci-dessus sur un terrain dur, horizontal et accessible par nos camions-grues.<br/></span><span>Attention, selon le type de matériel livré, nos camions peuvent avoir une longueur entre 11 et 21m, une largeur entre 2,6 et 3m, une hauteur entre 4 et 11m, un poids entre 17 et 26T.<br/></span><span>Si demande de retour impératif à une date précise, les frais de transport seront majorés de 30%.</span><span><br></span><span><b style='font-size:11px;'><br/>Assurance contre bris de machine<br/></b></span><span>Y compris vol, incendie, dégâts des eaux (8% du loyer) :<br/></span><span>Une franchise de 350,00€ par sinistre éventuel, sauf en cas de vol, la franchise sera de 20% de la valeur du bien. Sauf en cas de faute grave, dol ou malveillance. La Compagnie renonce au recours qu'elle serait en droit d'exercer contre le locataire.<br/></span><span>Pour le mobilier des modules habitables, une franchise de 500,00€ est d'application.<br/></span><span>Veuillez nous confirmer la souscription à l'option assurance lors de votre commande.</span><span><br></span><span><b style='font-size:11px;'><br/>Contribution environnementale<br/></b></span><span>Par respect pour l'environnement et dans le cadre de la législation en vigueur, Locasix ne cesse de faire des efforts. Traitement et enlèvement des déchets utilisés au cours du projet (filtres, pièces de rechange, lubrifiants, mazout pollué, réfrigérant, etc. Locasix demande au locataire une contribution environnementale forfaitaire de 2% du loyer total de la (des) machine(s).</span><span><br></span><span><b style='font-size:11px;'><br/>Nettoyage<br/></b></span><span>Texte à rédiger. Inclus dans les limites du raisonnable. On se réserve le droit de facturer. Un forfait de nettoyage à partir de 150€ HTVA/pièce vous sera facturé au retour si l'état de propreté et d'hygiène le requiert.</span>"        

    def _get_added_terms(self):
        #template = self.env["locasix.template.html"].search([('name', '=', 'Template conditions additionnelles')], limit=1)
        template = self.env.ref("locasix.locasix_template_condi")
        if template:
            return template.template
        else:
            return "<span><b style='font-size:11px;'>Conditions de location</b></span><ul><li style='margin:0px;'><span>Prix hors TVA 21%.</span></li><li style='margin:0px;'><span>Facturation minimale de 28 jours.</span></li><li style='margin:0px;'><span>Si annulation de la commande dans les 48H avant la date de livraison, des frais de dossier de 50,00€ par pièce vous seront facturés.</span></li><li style='margin:0px;'><span>Si demande de retour impératif à une date précise, les frais de transport seront majorés de 30%.</span></li><li style='margin:0px;'><span>Une caution peut vous être demandée avant la livraison.</span></li><li style='margin:0px;'><span><u>Si location de groupes électrogènes et/ou mâts d'éclairage :</u></span><ul><li style='margin:0px;'><span>Entretien journalier : carburant, niveau d'huile, niveau d'eau ... à votre charge.</span></li><li style='margin:0px;'><span>Entretien périodique comprenant filtres, huile ... à notre charge.</span></li><li style='margin:0px;'><span>Service de dépannage assuré uniquement du lundi au vendredi de 7h à 16h.</span></li></ul></li><li style='margin:0px;'><span>Délai : à convenir et suivant disponibilité.</span></li><li style='margin:0px;'><span>Validité de l'offre : 30 jours.</span></li><li style='margin:0px;'><span>Tous raccordements électriques et raccordements à l'alimentation en eau sont à votre charge.</span></li><li style='margin:0px;'><span>Voir conditions détaillées en dernière page.<br></span></li></ul><span><br></span><span><b style='font-size:11px;'><br/>Transport<br/></b></span><span>Transport et déchargement de l'ensemble repris ci-dessus sur un terrain dur, horizontal et accessible par nos camions-grues.<br/></span><span>Attention, selon le type de matériel livré, nos camions peuvent avoir une longueur entre 11 et 21m, une largeur entre 2,6 et 3m, une hauteur entre 4 et 11m, un poids entre 17 et 26T.<br/></span><span>Si demande de retour impératif à une date précise, les frais de transport seront majorés de 30%.</span><span><br></span><span><b style='font-size:11px;'><br/>Assurance contre bris de machine<br/></b></span><span>Y compris vol, incendie, dégâts des eaux (8% du loyer) :<br/></span><span>Une franchise de 350,00€ par sinistre éventuel, sauf en cas de vol, la franchise sera de 20% de la valeur du bien. Sauf en cas de faute grave, dol ou malveillance. La Compagnie renonce au recours qu'elle serait en droit d'exercer contre le locataire.<br/></span><span>Pour le mobilier des modules habitables, une franchise de 500,00€ est d'application.<br/></span><span>Veuillez nous confirmer la souscription à l'option assurance lors de votre commande.</span><span><br></span><span><b style='font-size:11px;'><br/>Contribution environnementale<br/></b></span><span>Par respect pour l'environnement et dans le cadre de la législation en vigueur, Locasix ne cesse de faire des efforts. Traitement et enlèvement des déchets utilisés au cours du projet (filtres, pièces de rechange, lubrifiants, mazout pollué, réfrigérant, etc. Locasix demande au locataire une contribution environnementale forfaitaire de 2% du loyer total de la (des) machine(s).</span><span><br></span><span><b style='font-size:11px;'><br/>Nettoyage<br/></b></span><span>Texte à rédiger. Inclus dans les limites du raisonnable. On se réserve le droit de facturer. Un forfait de nettoyage à partir de 150€ HTVA/pièce vous sera facturé au retour si l'état de propreté et d'hygiène le requiert.</span>"

    def _get_added_terms_weekend(self):
        #template = self.env["locasix.template.html"].search([('name', '=', 'Template conditions additionnelles week-end')], limit=1)
        template = self.env.ref("locasix.locasix_template_condi_weekend")
        if template:
            return template.template
        else:
            return "<span><b style='font-size:11px;'>Conditions de location de week-end</b></span><ul><li style='margin:0px;'><span>Prix hors TVA 21%.</span></li><li style='margin:0px;'><span>Paiement dans son intégralité avant départ.</span></li><li style='margin:0px;'><span>Si annulation de la commande dans les 48H avant la date de livraison, des frais de dossier de minimum 150,00€ vous seront facturés.</span></li><li style='margin:0px;'><span>Délai : à convenir et suivant disponibilité.</span></li><li style='margin:0px;'><span><u>Si location de groupes électrogènes et/ou mâts d'éclairage :</u></span><ul><li style='margin:0px;'><span>Entretien journalier : carburant, niveau d'huile, niveau d'eau ... à votre charge.</span></li><li style='margin:0px;'><span>Entretien périodique comprenant filtres, huile ... à notre charge.</span></li><li style='margin:0px;'>Service de dépannage assuré <b>uniquement</b> du lundi au vendredi de 7h à 16h.</li></ul></li><li style='margin:0px;'><span>Validité de l'offre : 30 jours.</span></li><li style='margin:0px;'><span>Tous raccordements électriques et raccordements à l'alimentation en eau sont à votre charge.</span></li><li style='margin:0px;'><span>Voir conditions détaillées en dernière page.<br></span></li></ul><span><br></span><span><b style='font-size:11px;'><br/>Transport<br/></b></span><span>Transport et déchargement de l'ensemble repris ci-dessus sur un terrain dur, horizontal et accessible par nos camions-grues.<br/></span><span>Attention, selon le type de matériel livré, nos camions peuvent avoir une longueur entre 11 et 21m, une largeur entre 2,6 et 3m, une hauteur entre 4 et 11m, un poids entre 17 et 26T.<br/></span><span>Si demande de retour impératif à une date précise, les frais de transport seront majorés de 30%.</span><span><br></span><span><b style='font-size:11px;'><br/>Assurance contre bris de machine<br/></b></span><span>Y compris vol, incendie, dégâts des eaux (8% du loyer) :<br/></span><span>Une franchise de 350,00€ par sinistre éventuel, sauf en cas de vol, la franchise sera de 20% de la valeur du bien. Sauf en cas de faute grave, dol ou malveillance. La Compagnie renonce au recours qu'elle serait en droit d'exercer contre le locataire.<br/></span><span>Pour le mobilier des modules habitables, une franchise de 500,00€ est d'application.<br/></span><span>Veuillez nous confirmer la souscription à l'option assurance lors de votre commande.</span><span><br></span><span><b style='font-size:11px;'><br/>Contribution environnementale<br/></b></span><span>Par respect pour l'environnement et dans le cadre de la législation en vigueur, Locasix ne cesse de faire des efforts. Traitement et enlèvement des déchets utilisés au cours du projet (filtres, pièces de rechange, lubrifiants, mazout pollué, réfrigérant, etc. Locasix demande au locataire une contribution environnementale forfaitaire de 2% du loyer total de la (des) machine(s).</span><span><br></span><span><b style='font-size:11px;'><br/>Nettoyage<br/></b></span><span>Texte à rédiger. Inclus dans les limites du raisonnable. On se réserve le droit de facturer. Un forfait de nettoyage à partir de 150€ HTVA/pièce vous sera facturé au retour si l'état de propreté et d'hygiène le requiert.</span>"


    def _get_front_page(self):
        #template = self.env["locasix.template.html"].search([('name', '=', 'Template page de garde')], limit=1)
        template = self.env.ref("locasix.locasix_template_front")
        if template:
            return template.template
        else:
            return "<span>Bonjour !title! !name!, <br/><br/>Suite à votre demande pour laquelle je vous remercie, veuillez trouver ci-dessous l'offre de prix.<br/><br/>Espérant vous être utile par cette proposition et restant à votre disposition pour tout renseignement complémentaire, je vous prie d'agréer, !title!, mes salutations les plus distinguées. <br/><br/>!uname!<br/>!login!<br/>!phone!<span>"


    @api.model
    def create(self, vals):
        obj = super(Order, self).create(vals)
        obj.adapt_pages()
        obj.name = obj.name
        return obj

    def write(self, vals):
        _logger.info("write template")
        if "name" in vals:
            user_names = self.env.user.name.split(" ")
            initials = ""
            for name in user_names:
                initials = initials+name[0]
            vals["name"] = vals["name"] + "-"+ initials
        if vals.get('adapt_front_page', False) or vals.get('adapt_sale_confirm', False):
            vals.pop('adapt_sale_confirm', 1)
            vals.pop('adapt_front_page', 1)
            res = super(Order, self).write(vals)
        elif "offer_type" in vals:
            res = super(Order, self).write(vals)
            _logger.info("order trigger")
            self.enforce_cuve()
            self.enforce_computations()
        else:
            res = super(Order, self).write(vals)
            _logger.info("order trigger")
            self.adapt_pages()
            self.enforce_cuve()
            self.enforce_computations()
        


            
        return res

    @api.depends("aller_ids")
    def _compute_aller_count(self):
        for order in self:
            if order.aller_ids:
                order.aller_count = len(order.aller_ids)
            else:
                order.aller_count = 0

    @api.depends("retour_ids")
    def _compute_retour_count(self):
        for order in self:
            if order.retour_ids:
                order.retour_count = len(order.retour_ids)
            else:
                order.retour_count = 0

    def update_prices(self):
        for order in self:
            if order.offer_type == "weekend":
                products_lst_price = {}
                for line in order.order_line.sudo():
                    if line.product_id:
                        if not line.product_id.id in products_lst_price:
                            products_lst_price[line.product_id.id] = line.product_id.lst_price
                        _logger.info("test")
                        line.product_id.sudo().write({"is_switching": True, "lst_price": line.product_id.weekend_price})
                        _logger.info("test2")
                res = super(Order, self).update_prices()
                for line in order.order_line:
                    if line.product_id:
                        line.product_id.sudo().write({"lst_price": products_lst_price[line.product_id.id]})
                        line.product_id.is_switching = False
            else:
                res = super(Order, self).update_prices()

    def has_electro_annexe(self):
        for order in self:
            if order.offer_type == "weekend":
                for line in order.order_line:
                    if line.product_id and line.product_id.categ_id:
                        if line.product_id.categ_id.show_electro_annexe:
                            return True
            return False
    

    def adapt_pages(self):
        for order in self:
            order.adapt_front_page()
            order.adapt_confirmation_page()

    
    def get_text_transformed(self, text):
        for order in self:
            if order.partner_id.title:
                text = text.replace("!title!", order.partner_id.title.name)
            else:
                text = text.replace("!title!", "")
            text = text.replace("!name!", order.partner_id.name)

            text = text.replace("!uname!", order.user_id.name)
            text = text.replace("!login!", order.user_id.login)
            text = text.replace("!offernum!", order.name)
            if order.user_id.phone:
                text = text.replace("!phone!", "T : "+order.user_id.phone)
            else:
                text = text.replace("!phone!", "")
        return text

    def adapt_confirmation_page(self):
        _logger.info("adapt confirmation template")
        for order in self:
            if order.partner_id and order.partner_id.name:
                condi = not order.sale_confirm_template
                if condi:
                    copy_txt = str(order.sale_confirm)
                if not condi:
                    text = order.sale_confirm_template
                else:
                    text = order.sale_confirm
                
                text = order.get_text_transformed(text)

                if condi:
                    order.write({"sale_confirm": text, "adapt_sale_confirm": True, "sale_confirm_template": copy_txt})
                else:
                    order.write({"sale_confirm": text, "adapt_sale_confirm": True})


    def adapt_front_page(self):
        _logger.info("adapt front page")
        for order in self:
            if order.partner_id and order.partner_id.name:
                _logger.info("in adaptation")
                _logger.info(order.front_page_body)
                _logger.info(order.front_page_body_template)
                condi = not order.front_page_body_template
                if condi:
                    copy_txt = str(order.front_page_body)
                if not condi:
                    text = order.front_page_body_template
                else:
                    text = order.front_page_body

                text = order.get_text_transformed(text)

                if condi:
                    order.write({"front_page_body": text, "adapt_front_page": True, "front_page_body_template": copy_txt,})
                else:
                    order.write({"front_page_body": text, "adapt_front_page": True,})
                _logger.info(order.front_page_body)
                _logger.info(order.front_page_body_template)

    def action_compute(self):
        _logger.info("action compute")
        for order in self:
            view = self.env.ref('locasix.view_warning_computed')
            return {
            'name': 'Ajout automatique',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'locasix.compute.warning',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_order_id': order.id,
                },
            }
            

    def action_confirm(self):
        _logger.info("action confirm")
        for order in self:
            if order.has_transport_prices():
                _logger.info("has transport price")
                self.done_order = True
                for line in self.order_line:
                    if line.temporary_product and line.product_id:
                        line.product_id.active = False
                        line.product_id.product_tmpl_id.active = False
                return super(Order, self).action_confirm()
            else:
                _logger.info("warning")
                view = self.env.ref('locasix.view_warning_transport')
                return {
                'name': 'Attention ! Il manque des prix pour le transport',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'locasix.transport.warning',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': {
                    },
                }                
        
    
    def action_quotation_send(self):
        _logger.info("action quotation")
        for order in self:
            if order.has_transport_prices():
                _logger.info("has transport price")
                return super(Order, self).action_quotation_send()
            else:
                _logger.info("warning")
                view = self.env.ref('locasix.view_warning_transport')
                return {
                'name': 'Attention ! Il manque des prix pour le transport',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'locasix.transport.warning',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': {
                    },
                }
    
    def enforce_cuve(self):
        _logger.info("enforce cuve")
        for order in self:
            cuve_line = False
            has_electro = False
            for line in order.order_line:
                if line.product_id:
                    if line.product_id.default_code == "CUK2":
                        cuve_line = line
                    if line.product_id.categ_id and line.product_id.categ_id.show_electro_annexe:
                        has_electro = True
            if cuve_line and has_electro:
                cuve_line.price_unit = 50.0
            elif cuve_line and not has_electro:
                if cuve_line.price_unit == 50:
                    cuve_line.price_unit = cuve_line.product_id.lst_price

    def has_transport_prices(self):
        for order in self:
            for line in order.order_line:
                if line.product_id and line.product_id.default_code in ["TA", "TR", "TAR"] and line.price_unit == 0.0:
                    return False
            return True


    def action_cancel(self):
        super(Order, self).action_cancel()
        self.done_order = False
        return True        

    def get_order_technicals(self):
        for order in self:
            technicals = []
            used_product = set()
            for line in order.order_line:
                if line.show_images and line.product_id and not line.product_id.id in used_product:
                    used_product.add(line.product_id.id)
                    tec = line.product_id.get_technicals()
                    if tec:
                        technicals += tec
            return technicals
    
    def get_order_plans(self):
        for order in self:
            plans = []
            used_product = set()
            for line in order.order_line:
                if line.show_images and line.product_id and not line.product_id.id in used_product:
                    used_product.add(line.product_id.id)
                    pl = line.product_id.get_plans()
                    if pl:
                        plans += pl
            return plans


    def line_computations(self, transport_aller, transport_retour, assemblage_aller, assemblage_retour, already_transport):
        sections = {}
        for order in self:
            order.is_computing = True
            order.mark_manual_sections()
            order.enforce_links()
            order.enforce_assemblage_fee(assemblage_aller, assemblage_retour)
            order.enforce_transport(transport_aller, transport_retour, already_transport)
            order.enforce_sections(sections)
            order.place_sections(sections)
            order.place_products(sections)
            order.remove_doublons(sections)
            order.enforce_computations()
            order.has_computed = True
            order.is_computing = False
    
    @api.onchange('offer_type')
    def weekend_offer_changed(self):
        _logger.info("weekend offer changed")
        for order in self:
            if order.offer_type == "weekend":
                for line in order.order_line:
                    line.update_line_values(pricing=True)
            #order.enforce_computations()

    def mark_manual_sections(self):
        _logger.info("mark manual section")
        for order in self:
            for line in order.order_line:
                if line.display_type == "line_section" and not line.is_section:
                    line.is_section = True
                    line.section_id = line.id
    
    def enforce_assemblage_fee(self, assemblage_aller, assemblage_retour):
        _logger.info("enforce assemblage fee")
        for order in self:
            has_assemblage = False
            for line in order.order_line:
                if line.product_id and line.product_id.is_assemblage_product and not line.from_compute:
                    has_assemblage = True
            if has_assemblage:
                categ_id = self.env["product.category"].search([("name", "=", "Montage et assemblage")], limit=1)
                if not categ_id:
                    categ_id = self.env["product.category"].create({
                        "name": "Montage et assemblage",
                        "show_section_order": True,
                    })
                montage = self.env["product.template"].search([("default_code", "=", "FASSA")], limit=1)
                if not montage:
                    montage = self.env["product.template"].create({"default_code": "FASSA", "name": "Frais de montage et assemblage aller", "categ_id": categ_id.id, "list_price": 0.0, "is_assemblage_product": False})

                montage_in_order = self.env["sale.order.line"].search([("product_id", "=", montage.product_variant_id.id), ("order_id", '=', order.id)], limit=1)
                if not montage_in_order:
                    self.env["sale.order.line"].create({
                    'order_id': self.id,
                    'product_id': montage.product_variant_id.id,
                    'price_unit': assemblage_aller,
                #    'section_id': line.section_id.id,
                    'from_compute': True,
                })
                if order.offer_type != "sale":
                    demontage = self.env["product.template"].search([("default_code", "=", "FASSR")], limit=1)
                    if not demontage:
                        demontage = self.env["product.template"].create({"default_code": "FASSR", "name": "Frais de montage et assemblage retour", "categ_id": categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
                    demontage_in_order = self.env["sale.order.line"].search([("product_id", "=", demontage.product_variant_id.id), ("order_id", '=', order.id)], limit=1)
                    if not demontage_in_order:
                        self.env["sale.order.line"].create({
                        'order_id': self.id,
                        'product_id': demontage.product_variant_id.id,
                    #    'section_id': line.section_id.id,
                        'price_unit': assemblage_retour,
                        'from_compute': True,
                    })



    def enforce_transport(self, transport_aller, transport_retour, already_transport):
        _logger.info("enforce transport")
        
        for order in self:
            order.has_extra_cost_transport = self.env['ir.config_parameter'].sudo().get_param('locasix.has_extra_cost_transport')
            order.extra_cost_transport_rate = self.env['ir.config_parameter'].sudo().get_param('locasix.extra_cost_transport_rate')

            categ_id = self.env["product.category"].search([("name", "=", "Transport")], limit=1)
            if not categ_id:
                categ_id = self.env["product.category"].create({
                    "name": "Transport",
                    "show_section_order": True,
                })


            if not already_transport:
                if order.offer_type == "weekend":
                    tar = self.env["product.template"].search([("default_code", "=", "TAR")], limit=1)
                    if not tar:
                        tar = self.env["product.template"].create({"default_code": "TAR", "name": "Transport aller et retour", "categ_id": categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
                    
                    tar_in_order = self.env["sale.order.line"].search([("product_id", "=", tar.product_variant_id.id), ("order_id", "=", order.id)], limit=1)
                    if not tar_in_order:

                        self.env["sale.order.line"].create({
                            'order_id': self.id,
                            'price_unit': transport_aller,
                            'product_id': tar.product_variant_id.id,
                            'from_compute': True,
                        })


                else:
                    ta = self.env["product.template"].search([("default_code", "=", "TA")], limit=1)
                    if not ta:
                        ta = self.env["product.template"].create({"default_code": "TA", "name": "Transport aller", "categ_id": categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
                    tr = self.env["product.template"].search([("default_code", "=", "TR")], limit=1)
                    if not tr:
                        tr = self.env["product.template"].create({"default_code": "TR", "name": "Transport retour", "categ_id": categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
                    
                    ta_in_order = self.env["sale.order.line"].search([("product_id", "=", ta.product_variant_id.id), ("order_id", '=', order.id)], limit=1)
                    if not ta_in_order:
                        self.env["sale.order.line"].create({
                        'order_id': self.id,
                        'product_id': ta.product_variant_id.id,
                        'price_unit': transport_aller,
                    #    'section_id': line.section_id.id,
                        'from_compute': True,
                    })

                    if order.offer_type != "sale":
                        tr_in_order = self.env["sale.order.line"].search([("product_id", "=", tr.product_variant_id.id), ("order_id", "=", order.id)], limit=1)
                        if not tr_in_order:
                            self.env["sale.order.line"].create({
                            'order_id': self.id,
                            'product_id': tr.product_variant_id.id,
                            'price_unit': transport_retour,
                        #    'section_id': line.section_id.id,
                            'from_compute': True,
                        })

            transport_address_product_id = self.env["product.template"].search([("is_transport_address_product", "=", True)], limit=1)
            if not transport_address_product_id:
                transport_address_product_id = self.env["product.template"].create({
                    "name": "Adresse de transport",
                    "categ_id": categ_id.id,
                    "is_transport_address_product": True,
                    "list_price": 0.0,
                    "is_assemblage_product": False
                })
            transport_address_in_order = self.env["sale.order.line"].search([("product_id", "=", transport_address_product_id.product_variant_id.id), ("order_id", "=", order.id)], limit=1)
            if not transport_address_in_order:
                self.env["sale.order.line"].create({
                    'order_id': self.id,
                    'product_id': transport_address_product_id.product_variant_id.id,
                    'name': self.get_transport_address(),
                    #'section_id': line.section_id.id,
                    'from_compute': True, 
                })
            if order.offer_type == "weekend":
                if order.date_aller:
                    date_aller_product_id = self.env["product.template"].search([("name", "=", "Date aller")], limit=1)
                    if not date_aller_product_id:
                        date_aller_product_id = self.env["product.template"].create({
                            "name": "Date aller",
                            "categ_id": categ_id.id,
                            "list_price": 0.0,
                            "is_assemblage_product": False
                        })
                    date_aller_in_order = self.env["sale.order.line"].search([("product_id", "=", date_aller_product_id.product_variant_id.id), ("order_id", "=", order.id)], limit=1)
                    if not date_aller_in_order:
                        self.env["sale.order.line"].create({
                            'order_id': self.id,
                            'product_id': date_aller_product_id.product_variant_id.id,
                            'name': order.date_aller,
                            #'section_id': line.section_id.id,
                            'from_compute': True, 
                        })
                if order.date_retour:
                    date_retour_product_id = self.env["product.template"].search([("name", "=", "Date retour")], limit=1)
                    if not date_retour_product_id:
                        date_retour_product_id = self.env["product.template"].create({
                            "name": "Date retour",
                            "categ_id": categ_id.id,
                            "list_price": 0.0,
                            "is_assemblage_product": False
                        })
                    date_retour_in_order = self.env["sale.order.line"].search([("product_id", "=", date_retour_product_id.product_variant_id.id), ("order_id", "=", order.id)], limit=1)
                    if not date_retour_in_order:
                        self.env["sale.order.line"].create({
                            'order_id': self.id,
                            'product_id': date_retour_product_id.product_variant_id.id,
                            'name': order.date_retour,
                            #'section_id': line.section_id.id,
                            'from_compute': True, 
                        })
                
    
        


    def enforce_sections(self, sections):
        _logger.info("enforce sections")
        for order in self:
            lines = order.order_line
            for line in lines:
                _logger.info(line.name)
                _logger.info(line.category_id)
                if line.product_id and line.order_id:
                    _logger.info("1")
                    if line.category_id and line.category_id.show_section_order:
                        _logger.info("2")
                        section_id = self.env["sale.order.line"].search([("is_section", "=", True), ("category_id", "=", line.category_id.id), ('order_id', "=", line.order_id.id)], limit=1)
                        if not section_id:
                            section_id = self.env["sale.order.line"].create({
                                "order_id": line.order_id.id,
                                "name": line.category_id.name,
                                "category_id": line.category_id.id,
                                "has_months_discounts": line.category_id.has_months_discounts,
                                "is_section": True,
                                "from_compute": True,
                                "is_multi": line.product_id.has_multi_price,
                                "sequence": len(line.order_id.order_line)+1,
                                "display_type": "line_section",
                                'product_id': False,})
                            section_id.section_id = section_id.id
                    else:
                        top_section_id = line.retrieve_top_section(lines)
                        if top_section_id:
                            section_id = top_section_id
                        else:
                            section_id = self.env["sale.order.line"].search([("is_section", "=", True), ('order_id', "=", line.order_id.id), ("name", "=", "Autres articles")], limit=1)
                            if not section_id:
                                _logger.info("create autres articles")
                                section_id = self.env["sale.order.line"].create({
                                    "order_id": line.order_id.id,
                                    "name": "Autres articles",
                                    "is_section": True,
                                    "from_compute": True,
                                    "is_multi": False,
                                    "sequence": len(line.order_id.order_line)+1000,
                                    "display_type": "line_section",
                                    'product_id': False,})
                                section_id.section_id = section_id.id
                    sections[section_id.id] = {"section": section_id, "first": section_id.sequence, "last": 1, "next_available": 1}
                    line.section_id = section_id.id
                elif line.display_type == "line_section":
                    if not line.id in sections:
                        sections[line.id] = {"section": line, "first": line.sequence, "last": 1, "next_available": 1}
                        

    def place_sections(self, sections):
        _logger.info("place sections")
        _logger.info(sections)
        for order in self:
            i = 1
            transport = False
            for section_id in sorted(sections.keys()):
                if sections[section_id]["section"].name == "Transport":
                    transport = sections[section_id]
                else:
                    sections[section_id]["section"].sequence = i
                    sections[section_id]["first"] = i
                    sections[section_id]["last"] = i+39
                    sections[section_id]["next_available"] = i+1
                    i += 40
            if transport:
                transport["section"].sequence = i
                transport["first"] = i
                transport["last"] = i+39
                transport["next_available"] = i+1
                i += 40
        _logger.info(sections)


    def place_products(self, sections):
        _logger.info("place products")
        for order in self:
            address_transport_line = False
            date_retour = False
            date_aller = False
            categ_id = self.env["product.category"].search([("name", "=", "Transport")], limit=1)
            if not categ_id:
                categ_id = self.env["product.category"].create({
                    "name": "Transport",
                    "show_section_order": True,
                })

            surc_a = self.env["product.template"].search([('default_code', "=", "SURCA")], limit=1)
            if not surc_a:
                surc_a = self.env["product.template"].create({"default_code": "SURCA", "name": "Surcoût", "categ_id":categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
            surc_r = self.env["product.template"].search([('default_code', "=", "SURCR")], limit=1)
            if not surc_r:
                surc_r = self.env["product.template"].create({"default_code": "SURCR", "name": "Surcoût", "categ_id":categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
            surc_ar = self.env["product.template"].search([('default_code', "=", "SURCAR")], limit=1)
            if not surc_ar:
                surc_ar = self.env["product.template"].create({"default_code": "SURCAR", "name": "Surcoût", "categ_id":categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
            surc_h = self.env["product.template"].search([('default_code', "=", "SURCH")], limit=1)
            if not surc_h:
                surc_h = self.env["product.template"].sudo().create({"default_code": "SURCH", "name": "Surcoût transport horaire", "categ_id":categ_id.id, "list_price": 0.0, "is_assemblage_product": False})

            for line in order.order_line:
                if not line.is_section and line.section_id:
                    if line.product_id and line.product_id.is_transport_address_product:
                        _logger.info("address transport")
                        address_transport_line = line
                    elif line.product_id and line.product_id.name == "Date aller":
                        date_aller = line
                    elif line.product_id and line.product_id.name =="Date retour":
                        date_retour = line
                    elif line.product_id and line.product_id.default_code in ["TAR", "TA/RC", "TA/R"]:
                        line.sequence = sections[line.section_id.id]["next_available"]
                        surc_temp1 = self.env["product.template"].search([('default_code', "=", "SURC-"+line.product_id.default_code)], limit=1)
                        if not surc_temp1:
                            surc_temp1 = self.env["product.template"].sudo().create({"default_code": "SURC-"+line.product_id.default_code, "name": "Surcoût", "categ_id":categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
                        if order.has_extra_cost_transport:
                            self.env["sale.order.line"].create({
                                'order_id': self.id,
                                "name": surc_ar.name,
                                "extra_cost_link": line.id,
                                'price_unit': line.price_unit * order.extra_cost_transport_rate,
                                'section_id': line.section_id.id,
                                "product_uom_qty": 1,
                                'sequence': sections[line.section_id.id]["next_available"] +1,
                                'product_id': surc_temp1.product_variant_id.id,
                                'from_compute': True,
                            })
                        sections[line.section_id.id]["next_available"] += 2
                    elif line.product_id and line.product_id.categ_id.id == categ_id.id and "TA" in line.product_id.default_code:
                        _logger.info("checko")
                        line.sequence = sections[line.section_id.id]["next_available"]
                        surc_temp2 = self.env["product.template"].search([('default_code', "=", "SURC-"+line.product_id.default_code)], limit=1)
                        if not surc_temp2:
                            surc_temp2 = self.env["product.template"].sudo().create({"default_code": "SURC-"+line.product_id.default_code, "name": "Surcoût", "categ_id":categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
                        if order.has_extra_cost_transport:
                            _logger.info("create surca")
                            _logger.info(line.price_unit)
                            self.env["sale.order.line"].create({
                                'order_id': self.id,
                                "name": surc_a.name,
                                "extra_cost_link": line.id,
                                'price_unit': line.price_unit * order.extra_cost_transport_rate,
                                'section_id': line.section_id.id,
                                "product_uom_qty": 1,
                                'sequence': sections[line.section_id.id]["next_available"] +1,
                                'product_id': surc_temp2.product_variant_id.id,
                                'from_compute': True,
                            })
                            #line2.price_unit = line.price_unit * order.extra_cost_transport_rate
                        sections[line.section_id.id]["next_available"] += 2
                    elif line.product_id and line.product_id.default_code in ["TH1", "TH2", "TH1 ", "TH2 "]:
                        _logger.info("checko")
                        line.sequence = sections[line.section_id.id]["next_available"]
                        surc_temp4 = self.env["product.template"].search([('default_code', "=", "SURC-"+line.product_id.default_code)], limit=1)
                        if not surc_temp4:
                            surc_temp4 = self.env["product.template"].sudo().create({"default_code": "SURC-"+line.product_id.default_code, "name": "Surcoût", "categ_id":categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
                        if order.has_extra_cost_transport:
                            _logger.info("create surcar-h")
                            _logger.info(line.price_unit)
                            self.env["sale.order.line"].create({
                                'order_id': self.id,
                                "name": surc_h.name,
                                "extra_cost_link": line.id,
                                'price_unit': line.price_unit * order.extra_cost_transport_rate,
                                'section_id': line.section_id.id,
                                "product_uom_qty": 1,
                                'sequence': sections[line.section_id.id]["next_available"] +1,
                                'product_id': surc_temp4.product_variant_id.id,
                                'from_compute': True,
                            })
                            #line2.price_unit = line.price_unit * order.extra_cost_transport_rate
                        sections[line.section_id.id]["next_available"] += 2
                    elif line.product_id and line.product_id.categ_id.id == categ_id.id and "TR" in line.product_id.default_code:
                        line.sequence = sections[line.section_id.id]["next_available"]
                        surc_temp3 = self.env["product.template"].search([('default_code', "=", "SURC-"+line.product_id.default_code)], limit=1)
                        if not surc_temp3:
                            surc_temp3 = self.env["product.template"].sudo().create({"default_code": "SURC-"+line.product_id.default_code, "name": "Surcoût", "categ_id":categ_id.id, "list_price": 0.0, "is_assemblage_product": False})
                        if order.has_extra_cost_transport:
                            self.env["sale.order.line"].create({
                                'order_id': self.id,
                                "name": surc_r.name,
                                "extra_cost_link": line.id,
                                "product_uom_qty": 1,
                                'price_unit': line.price_unit * order.extra_cost_transport_rate,
                                'section_id': line.section_id.id,
                                'sequence': sections[line.section_id.id]["next_available"] +1,
                                'product_id': surc_temp3.product_variant_id.id,
                                'from_compute': True,
                            })
                        sections[line.section_id.id]["next_available"] += 2
                    else:
                        line.sequence = sections[line.section_id.id]["next_available"]
                        sections[line.section_id.id]["next_available"] += 1
            if address_transport_line:
                _logger.info("address transport correction")
                address_transport_line.sequence = sections[address_transport_line.section_id.id]["next_available"]
                sections[address_transport_line.section_id.id]["next_available"] += 1
            if date_aller:
                _logger.info("date aller correction")
                date_aller.sequence = sections[date_aller.section_id.id]["next_available"]
                sections[date_aller.section_id.id]["next_available"] += 1
            if date_retour:
                _logger.info("date retour correction")
                date_retour.sequence = sections[date_retour.section_id.id]["next_available"]
                sections[date_retour.section_id.id]["next_available"] += 1

    
    def remove_doublons(self, sections):
        _logger.info("remove doublons")
        for order in self:
            for section in sections:
                product_count = {}
                section_lines = self.retrieve_lines_from_section(sections[section]["section"])
                product_line_dic = {}
                for line in section_lines:
                    if line.product_id and not line.is_section and line.from_compute:
                        if line.product_id.id in product_count:
                            product_count[line.product_id.id] += line.product_uom_qty
                            order.order_line = [(2, line.id, 0)]
                        else:
                            product_line_dic[line.product_id.id] = line
                            product_count[line.product_id.id] = line.product_uom_qty
                for line in product_line_dic.values():
                    if line.product_id.id in product_count and line.product_id.qty_same_as_parent:
                        line.product_uom_qty = product_count[line.product_id.id]

                    
    def should_create_link(self, product):
        for order in self:
            if product.is_insurance and (order.offer_type == "weekend" or order.offer_type == "sale"):
                return False
            elif product.default_code in ["FN", "FNG", "FNC"] and order.offer_type == "sale":
                return False
            elif product.is_insurance and not order.partner_id.has_insurance:
                return False
            return True

    def enforce_links(self):
        _logger.info("enforce links")
        for order in self:
            for line in order.order_line:
                if line.product_id and line.order_id:
                    links = self.env["locasix.product.link"].search([("product_master_id", "=", line.product_id.product_tmpl_id.id)])
                    for link in links:
                        if order.should_create_link(link.product_linked_id):
                            new_line = self.env["sale.order.line"].create({
                                'order_id': line.order_id.id,
                                'product_id': link.product_linked_id.product_variant_id.id,
                                'product_uom_qty': line.product_uom_qty if link.product_linked_id.qty_same_as_parent else 1,
                            #    'section_id': line.section_id.id,
                                'from_compute': True,
                            })
                            #'sequence': sections[line.section_id.id]["next_available"]})
                        #sections[line.section_id.id]["next_available"] += 1
                            new_line.update_line_values()
                            if not new_line.product_id.categ_id or not new_line.product_id.categ_id.show_section_order:
                                _logger.info("change of category")
                                _logger.info(new_line.category_id.name)
                                new_line.category_id = line.category_id
                            _logger.info(new_line.name)
                            if new_line.is_insurance():
                                new_line.is_multi = line.product_id.has_multi_price

    def enforce_computations(self):
        _logger.info("enforce computations")
        for order in self:
            for line in order.order_line:
                if line.product_id and line.is_insurance():
                    lines = self.retrieve_lines_from_section_without_id(line)
                    _logger.info(line.is_section_multi())
                    line.enforce_computation(line.is_section_multi(), lines)
                elif line.product_id and line.product_id.default_code and "SURC" in line.product_id.default_code:
                    lines = self.retrieve_lines_from_section_without_id(line)
                    line.enforce_computation(line.is_section_multi(), lines)
    


    def retrieve_lines_from_section_without_id(self, line):
        _logger.info("retrieve lines without id")
        for order in self:
            lines = []
            potential_lines = []
            seq_of_section_above = -1
            stop = False
            sorted_lines = sorted(order.order_line, key=lambda line: line.sequence)
            for order_line in sorted_lines:
                if not stop and order_line.is_section and order_line.sequence <= line.sequence:
                    seq_of_section_above = order_line.sequence
                    potential_lines = []
                    potential_lines.append(order_line)
                elif order_line.is_section and order_line.sequence > line.sequence:
                    stop = True
                elif not stop and not order_line.is_section and seq_of_section_above != -1:
                    potential_lines.append(order_line)
            lines = potential_lines
            return lines

        
    def get_sections(self):
        _logger.info("get sections")
        for order in self:
            return self.env["sale.order.line"].search([("order_id", "=", order.id), ("is_section", "=", True)])

      
    def retrieve_lines_from_section(self, section_id):
        _logger.info("retrieve line from section")
        for order in self:
            return self.env["sale.order.line"].search([("order_id", "=", order.id), ("section_id", "=", section_id.id)])
        

    def action_remove_computed_lines(self):
        for order in self:
            lines_to_be_removed = self.env["sale.order.line"].search([("order_id", "=", order.id), ("from_compute", "=", True)])
            for line in lines_to_be_removed:
                order.order_line = [(2, line.id, 0)]
            order.has_computed = False

    def action_open_retour(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Retours',
            'view_mode': 'tree,form',
            'res_model': 'locasix.aller',
            'domain': [('order_id', '=', self.id), ("aller_type", "=", "in")],
            'context': "{'create': False}"
        }

    def action_open_aller(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Allers',
            'view_mode': 'tree,form',
            'res_model': 'locasix.aller',
            'domain': [('order_id', '=', self.id), ("aller_type", "=", "out")],
            'context': "{'create': False}"
        }

    
    def action_put_in_agenda(self):
        _logger.info("action put in agenda")
        for order in self:
            line_ids = order.order_line.filtered(lambda x: x.product_id and x.product_id.type != "service")
            view = self.env.ref('locasix.locasix_order_to_agenda_form')
            return {
            'name': 'Créer les allers et retours',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'locasix.order.agenda',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                "default_order_id": order.id,
                "default_line_ids": line_ids.ids,
                "default_localite_id": order.city.id,
                },
            }    
    
    def get_discount_rates(self, section_line):
        for order in self:
            if section_line.has_months_discounts:
                return [
                    f'-{int(order.months_2_discount_rate*100)}%', 
                    f'-{int(order.months_3_discount_rate*100)}%', 
                    f'-{int(order.months_6_discount_rate*100)}%'
                        ]
            else:
                return ['', '', '']