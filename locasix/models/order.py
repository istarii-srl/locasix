from odoo import fields, api, models


import logging
_logger = logging.getLogger(__name__)

class Order(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    front_page_body = fields.Html(string="Page de garde", default="<span>Bonjour Madame Intel <br/><br/>Suite à votre demande pour laquelle je vous remercie, veuillez trouver ci-dessous l'offre de prix.<br/><br/>Espérant vous être utile par cette proposition et restant à votre disposition pour tout renseignement complémentaire, je vous prie d'agréer, Madame, mes salutations les plus distinguées. <br/><br/>Alexandre Chevalier<br/>a.chevalier@locasix.be<br/>T : 065 660 596<span>")
    
    added_terms = fields.Html(string="Conditions additionnelles", default="<span><b>Conditions de location</b></span><ul><li style='margin:0px;'><span>Prix hors TVA 21%.</span></li><li style='margin:0px;'><span>Facturation minimale de 28 jours.</span></li><li style='margin:0px;'><span>Si annulation de la commande dans les 48H avant la date de livraison, des frais de dossier de 50,00€ par pièce vous seront facturés.</span></li><li style='margin:0px;'><span>Si demande de retour impératif à une date précise, les frais de transport seront majorés de 30%.</span></li><li style='margin:0px;'><span>Une caution peut vous être demandée avant la livraison.</span></li><li style='margin:0px;'><span><u>Si location de groupes électrogènes et/ou mâts d'éclairage :</u></span><ul><li style='margin:0px;'><span>Entretien journalier : carburant, niveau d'huile, niveau d'eau ... à votre charge.</span></li><li style='margin:0px;'><span>Entretien périodique comprenant filtres, huile ... à notre charge.</span></li><li style='margin:0px;'><span>Service de dépannage assuré uniquement du lundi au vendredi de 7h à 16h.</span></li></ul></li><li style='margin:0px;'><span>Délai : à convenir et suivant disponibilité.</span></li><li style='margin:0px;'><span>Validité de l'offre : 30 jours.</span></li><li style='margin:0px;'><span>Tous raccordements électriques et raccordements à l'alimentation en eau sont à votre charge.</span></li><li style='margin:0px;'><span>Voir conditions détaillées en dernière page.<br></span></li></ul><span><br></span><span><b><br/>Transport<br/></b></span><span>Transport et déchargement de l'ensemble repris ci-dessus sur un terrain dur, horizontal et accessible par nos camions-grues.<br/></span><span>Attention, selon le type de matériel livré, nos camions peuvent avoir une longueur entre 11 et 21m, une largeur entre 2,6 et 3m, une hauteur entre 4 et 11m, un poids entre 17 et 26T.<br/></span><span>Si demande de retour impératif à une date précise, les frais de transport seront majorés de 30%.</span><span><br></span><span><b><br/>Assurance contre bris de machine<br/></b></span><span>Y compris vol, incendie, dégâts des eaux (8% du loyer) :<br/></span><span>Une franchise de 350,00€ par sinistre éventuel, sauf en cas de vol, la franchise sera de 20% de la valeur du bien. Sauf en cas de faute grave, dol ou malveillance. La Compagnie renonce au recours qu'elle serait en droit d'exercer contre le locataire.<br/></span><span>Pour le mobilier des modules habitables, une franchise de 500,00€ est d'application.<br/></span><span>Veuillez nous confirmer la souscription à l'option assurance lors de votre commande.</span><span><br></span><span><b><br/>Contribution environnementale<br/></b></span><span>Par respect pour l'environnement et dans le cadre de la législation en vigueur, Locasix ne cesse de faire des efforts. Traitement et enlèvement des déchets utilisés au cours du projet (filtres, pièces de rechange, lubrifiants, mazout pollué, réfrigérant, etc. Locasix demande au locataire une contribution environnementale forfaitaire de 2% du loyer total de la (des) machine(s).</span><span><br></span><span><b><br/>Nettoyage<br/></b></span><span>Texte à rédiger. Inclus dans les limites du raisonnable. On se réserve le droit de facturer. Un forfait de nettoyage à partir de 150€ HTVA/pièce vous sera facturé au retour si l'état de propreté et d'hygiène le requiert.</span>")
    weekend_offer = fields.Boolean(string="Offre week-end", default=False)

    has_computed = fields.Boolean(string="Y a t-il eu une calculation ?", default=False)


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
            


    def line_computations(self):
        for order in self:
            order.has_computed = True

    def action_remove_computed_lines(self):
        for order in self:
            order.has_computed = False