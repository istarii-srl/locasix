from odoo import fields, api, models


import logging
_logger = logging.getLogger(__name__)

class Order(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    front_page_body = fields.Html(string="Page de garde", default="<span>Bonjour !title! !name!, <br/><br/>Suite à votre demande pour laquelle je vous remercie, veuillez trouver ci-dessous l'offre de prix.<br/><br/>Espérant vous être utile par cette proposition et restant à votre disposition pour tout renseignement complémentaire, je vous prie d'agréer, !title!, mes salutations les plus distinguées. <br/><br/>!uname!<br/>!login!<br/>!phone!<span>")
    front_page_body_template = fields.Char(string="Page de garde template") 

    added_terms = fields.Html(string="Conditions additionnelles", default="<span><b>Conditions de location</b></span><ul><li style='margin:0px;'><span>Prix hors TVA 21%.</span></li><li style='margin:0px;'><span>Facturation minimale de 28 jours.</span></li><li style='margin:0px;'><span>Si annulation de la commande dans les 48H avant la date de livraison, des frais de dossier de 50,00€ par pièce vous seront facturés.</span></li><li style='margin:0px;'><span>Si demande de retour impératif à une date précise, les frais de transport seront majorés de 30%.</span></li><li style='margin:0px;'><span>Une caution peut vous être demandée avant la livraison.</span></li><li style='margin:0px;'><span><u>Si location de groupes électrogènes et/ou mâts d'éclairage :</u></span><ul><li style='margin:0px;'><span>Entretien journalier : carburant, niveau d'huile, niveau d'eau ... à votre charge.</span></li><li style='margin:0px;'><span>Entretien périodique comprenant filtres, huile ... à notre charge.</span></li><li style='margin:0px;'><span>Service de dépannage assuré uniquement du lundi au vendredi de 7h à 16h.</span></li></ul></li><li style='margin:0px;'><span>Délai : à convenir et suivant disponibilité.</span></li><li style='margin:0px;'><span>Validité de l'offre : 30 jours.</span></li><li style='margin:0px;'><span>Tous raccordements électriques et raccordements à l'alimentation en eau sont à votre charge.</span></li><li style='margin:0px;'><span>Voir conditions détaillées en dernière page.<br></span></li></ul><span><br></span><span><b><br/>Transport<br/></b></span><span>Transport et déchargement de l'ensemble repris ci-dessus sur un terrain dur, horizontal et accessible par nos camions-grues.<br/></span><span>Attention, selon le type de matériel livré, nos camions peuvent avoir une longueur entre 11 et 21m, une largeur entre 2,6 et 3m, une hauteur entre 4 et 11m, un poids entre 17 et 26T.<br/></span><span>Si demande de retour impératif à une date précise, les frais de transport seront majorés de 30%.</span><span><br></span><span><b><br/>Assurance contre bris de machine<br/></b></span><span>Y compris vol, incendie, dégâts des eaux (8% du loyer) :<br/></span><span>Une franchise de 350,00€ par sinistre éventuel, sauf en cas de vol, la franchise sera de 20% de la valeur du bien. Sauf en cas de faute grave, dol ou malveillance. La Compagnie renonce au recours qu'elle serait en droit d'exercer contre le locataire.<br/></span><span>Pour le mobilier des modules habitables, une franchise de 500,00€ est d'application.<br/></span><span>Veuillez nous confirmer la souscription à l'option assurance lors de votre commande.</span><span><br></span><span><b><br/>Contribution environnementale<br/></b></span><span>Par respect pour l'environnement et dans le cadre de la législation en vigueur, Locasix ne cesse de faire des efforts. Traitement et enlèvement des déchets utilisés au cours du projet (filtres, pièces de rechange, lubrifiants, mazout pollué, réfrigérant, etc. Locasix demande au locataire une contribution environnementale forfaitaire de 2% du loyer total de la (des) machine(s).</span><span><br></span><span><b><br/>Nettoyage<br/></b></span><span>Texte à rédiger. Inclus dans les limites du raisonnable. On se réserve le droit de facturer. Un forfait de nettoyage à partir de 150€ HTVA/pièce vous sera facturé au retour si l'état de propreté et d'hygiène le requiert.</span>")
    weekend_offer = fields.Boolean(string="Offre week-end", default=False)
    usage_rate_display = fields.Selection(string="Affichage des tarifs", selection=[('24', "Afficher les tarifs 24h"), ('8', "Afficher les tarifs 8h"), ("duo", "Afficher les deux tarifs")])
    show_discount_rates = fields.Boolean(string="Afficher les remises", default=False)

    months_2_discount_rate = fields.Float(string="Remise 2", default=0.10)
    months_3_discount_rate = fields.Float(string="Remise 3", default=0.15)
    months_6_discount_rate = fields.Float(string="Remise 6", default=0.2)

    done_order = fields.Boolean(string="Offre terminée", default=False)
    is_computing = fields.Boolean(string="En cours de calculation", default=False)
    has_computed = fields.Boolean(string="Y a t-il eu une calculation ?", default=False)

    @api.model
    def create(self, vals):
        obj = super(Order, self).create(vals)
        obj.adapt_front_page()
        return obj

    def write(self, vals):
        _logger.info("write template")
        _logger.info(vals)
        if vals.get('adapt_front_page', False):
            vals.pop('adapt_front_page', 1)
            res = super(Order, self).write(vals)
        else:
            res = super(Order, self).write(vals)
            self.adapt_front_page()
        
        return res

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
                if order.partner_id.title:
                    text = text.replace("!title!", order.partner_id.title.name)
                else:
                    text = text.replace("!title!", "")
                text = text.replace("!name!", order.partner_id.name)

                text = text.replace("!uname!", order.user_id.name)
                text = text.replace("!login!", order.user_id.login)
                if order.user_id.phone:
                    text = text.replace("!phone!", "T : "+order.user_id.phone)
                else:
                    text = text.replace("!phone!", "")

                if condi:
                    order.write({"front_page_body": text, "adapt_front_page": True, "front_page_body_template": copy_txt,})
                else:
                    order.write({"front_page_body": text, "adapt_front_page": True,})
                _logger.info(order.front_page_body)
                _logger.info(order.front_page_body_template)

    def action_compute(self):
        _logger.info("action compute")
        for order in self:
            if order.has_computed:
                view = self.env.ref('locasix.view_warning_computed')
                return {
                'name': 'Attention ! Lignes déjà ajoutées',
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
            else:
                order.line_computations()
            

    def _action_confirm(self):
        super(Order, self)._action_confirm()
        self.done_order = True
        for line in self.order_line:
            if line.temporary_product and line.product_id:
                line.product_id.active = False
                line.product_id.product_tmpl_id.active = False
        return True
    
    def action_quotation_send(self):
        for order in self:
            if order.has_transport_prices():
                super(Order, self).action_quotation_send()
            else:
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

    def line_computations(self):
        sections = {}
        for order in self:
            order.is_computing = True
            order.mark_manual_sections()
            order.enforce_links()
            order.enforce_transport()
            order.enforce_sections(sections)
            order.place_sections(sections)
            order.place_products(sections)
            order.remove_doublons(sections)
            order.enforce_computations()
            order.has_computed = True
            order.is_computing = False
    
    @api.onchange('weekend_offer')
    def weekend_offer_changed(self):
        _logger.info("weekend offer changed")
        for order in self:
            for line in order.order_line:
                line.update_line_values(pricing=True)

    def mark_manual_sections(self):
        _logger.info("mark manual section")
        for order in self:
            for line in order.order_line:
                if line.display_type == "line_section" and not line.is_section:
                    line.is_section = True
                    line.section_id = line.id
    
    def enforce_transport(self):
        _logger.info("enforce transport")
        for order in self:
            if order.weekend_offer:
                tar = self.env["product.template"].search([("default_code", "=", "TAR")], limit=1)
                if not tar:
                    tar = self.env["product.template"].create({"default_code": "TAR", "name": "Transport aller et retour"})
                
                tar_in_order = self.env["sale.order.line"].search([("product_id", "=", tar.product_variant_id.id)], limit=1)
                if not tar_in_order:
                    self.env["sale.order.line"].create({
                        'order_id': self.id,
                        'product_id': tar.product_variant_id.id,
                        'from_compute': True,
                    })
            else:
                ta = self.env["product.template"].search([("default_code", "=", "TA")], limit=1)
                if not ta:
                    ta = self.env["product.template"].create({"default_code": "TA", "name": "Transport aller"})
                tr = self.env["product.template"].search([("default_code", "=", "TR")], limit=1)
                if not tr:
                    tr = self.env["product.template"].create({"default_code": "TR", "name": "Transport retour"})
                
                ta_in_order = self.env["sale.order.line"].search([("product_id", "=", ta.product_variant_id.id)], limit=1)
                if not ta_in_order:
                    self.env["sale.order.line"].create({
                    'order_id': self.id,
                    'product_id': ta.product_variant_id.id,
                #    'section_id': line.section_id.id,
                    'from_compute': True,
                })

                tr_in_order = self.env["sale.order.line"].search([("product_id", "=", tr.product_variant_id.id)], limit=1)
                if not tr_in_order:
                    self.env["sale.order.line"].create({
                    'order_id': self.id,
                    'product_id': tr.product_variant_id.id,
                #    'section_id': line.section_id.id,
                    'from_compute': True,
                })
    
    def fetch_transport(self, ref):
        _logger.info("fetch transport")
        


    def enforce_sections(self, sections):
        _logger.info("enforce sections")
        for order in self:
            lines = order.order_line
            for line in lines:
                _logger.info(line.name)
                _logger.info(line.category_id)
                if line.product_id and line.order_id:
                    if line.category_id and line.category_id.show_section_order:
                        section_id = self.env["sale.order.line"].search([("is_section", "=", True), ("category_id", "=", line.category_id.id), ('order_id', "=", line.order_id.id)], limit=1)
                        if not section_id:
                            section_id = self.env["sale.order.line"].create({
                                "order_id": line.order_id.id,
                                "name": line.category_id.name,
                                "category_id": line.category_id.id,
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
            for section_id in sorted(sections.keys()):
                sections[section_id]["section"].sequence = i
                sections[section_id]["first"] = i
                sections[section_id]["last"] = i+39
                sections[section_id]["next_available"] = i+1
                i += 40
        _logger.info(sections)


    def place_products(self, sections):
        _logger.info("place products")
        for order in self:
            for line in order.order_line:
                if not line.is_section and line.section_id:
                    line.sequence = sections[line.section_id.id]["next_available"]
                    sections[line.section_id.id]["next_available"] += 1
    
    def remove_doublons(self, sections):
        _logger.info("remove doublons")
        _logger.info(sections)
        for order in self:
            for section in sections:
                product_count = {}
                section_lines = self.retrieve_lines_from_section(sections[section]["section"])
                for line in section_lines:
                    if line.product_id and not line.is_section and line.from_compute:
                        if line.product_id.id in product_count:
                            order.order_line = [(2, line.id, 0)]
                        else:
                            product_count[line.product_id.id] = 1

                    

    def enforce_links(self):
        _logger.info("enforce links")
        for order in self:
            for line in order.order_line:
                if line.product_id and line.order_id:
                    links = self.env["locasix.product.link"].search([("product_master_id", "=", line.product_id.product_tmpl_id.id)])
                    _logger.info(links)
                    for link in links:
                        _logger.info("links")
                        #no_doublon = True
                        #lines = self.retrieve_lines_from_section(line.section_id)
                        #for section_line in lines:
                        #    if section_line.product_id.product_tmpl_id.id == link.product_linked_id.id:
                        #        no_doublon = False
                        #_logger.info("doublon status")
                        #_logger.info(no_doublon)
                        #if no_doublon:
                        new_line = self.env["sale.order.line"].create({
                            'order_id': line.order_id.id,
                            'product_id': link.product_linked_id.product_variant_id.id,
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
                            _logger.info(new_line.category_id.name)
                            _logger.info(line.category_id.name)
                        _logger.info(new_line.name)
                        if new_line.is_insurance():
                            _logger.info("MULTO 2")
                            _logger.info(line.is_multi)
                            _logger.info(line.name)
                            _logger.info(line.product_id.has_multi_price)
                            new_line.is_multi = line.is_multi

    def enforce_computations(self):
        _logger.info("enforce computations")
        for order in self:
            for line in order.order_line:
                if line.product_id and line.is_insurance() and line.section_id:
                    lines = self.retrieve_lines_from_section_without_id(line)
                    _logger.info(line.is_multi)
                    for logo in lines:
                        _logger.info(logo.name)
                    line.enforce_computation(line.is_multi, lines)


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

    def action_compute_insurances(self):
        _logger.info("action compute insurances")
        for order in self:
            order.enforce_computations()
    
    def action_put_in_agenda(self):
        _logger.info("action put in agenda")
        for order in self:
            pass