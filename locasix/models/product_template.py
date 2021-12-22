from odoo import fields, api, models, tools

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    product_description = fields.Text(string="Description du produit")

    weekend_price = fields.Float(string="Prix weekend")
    has_24_price = fields.Boolean(string="A un tarif 24/24", default=False)
    has_multi_price = fields.Boolean(string="A plusieurs tarifs", default=False)
    has_ref_to_condi = fields.Boolean(string="Conditions additionnelles", default=False)
    more_details_link = fields.Char(string="Lien vers plus de détail")

    product_linked_ids = fields.One2many(comodel_name="locasix.product.link", inverse_name="product_linked_id", string="Liens passifs")
    product_master_ids = fields.One2many(comodel_name="locasix.product.link", inverse_name="product_master_id", string="Liens actifs")
    assemblage_ids = fields.One2many(comodel_name="locasix.assemblage.link", inverse_name="assemblage_product_id", string="Produits assemblés")

    day_price = fields.Float(string="Prix par jour")
    week_price = fields.Float(string="Prix par semaine")
    month_price = fields.Float(string="Prix par mois")

    months_2_discount = fields.Float(string="Remise 2 mois")
    months_3_discount = fields.Float(string="Remise 3 mois")
    months_6_discount = fields.Float(string="Remise 6 mois")

    qty_same_as_parent = fields.Boolean(string="Même quantity que le produit parent", default=False)

    is_temporary_product = fields.Boolean(string="Temporaire", default=True)
    is_assemblage_product = fields.Boolean(string="Assemblage", default=True)
    
    is_transport_address_product = fields.Boolean(default=False)

    show_offert = fields.Boolean(string="Affiche 'offert' si prix égal 0", default=True)


    technical_ids = fields.One2many(comodel_name="locasix.product.technical", inverse_name="product_tmpl_id")
    plan_ids = fields.One2many(comodel_name="locasix.product.plan", inverse_name="product_tmpl_id")

    is_insurance = fields.Boolean(string="Est une assurance", default=False)
    insurance_percentage = fields.Float(string="Pourcentage de la prime", default=0.08)


    @api.onchange('is_assemblage_product')
    def is_assemblage_changed(self):
        if self.is_assemblage_product:
            categ_id = self.env["product.category"].search([("name", "=", "Location de modules habitables - containers maritimes")], limit=1)
        else:
            categ_id = self.env["product.category"].search([("name", "=", "All")], limit=1)
        if categ_id:
            self.categ_id = categ_id

    @tools.ormcache()
    def _get_default_category_id(self):
        # Deletion forbidden (at least through unlink)
        categ_id = self.env["product.category"].search([("name", "=", "Location de modules habitables - containers maritimes")], limit=1)
        if not categ_id:
            return self.env.ref('product.product_category_all')
        else:
            return categ_id

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        default["is_temporary_product"] = True
        return super(ProductTemplate, self).copy(default=default)

    def should_display_hour(self):
        for product in self:
            if product.uom_id.name == "Heures":
                return True
            else: 
                return False


    def launch_import(self):
        _logger.info("in launch import")
        view = self.env.ref('locasix.import_product_wizard_form')
        return {
            'name': 'Importation des produits',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'locasix.product.import',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
            },
        }

    def get_plans(self):
        for product in self:
            if product.is_assemblage_product:
                if product.plan_ids:
                    plans = product.plan_ids[:]
                else:
                    plans = []
                for assemblage in product.assemblage_ids:
                    pl = assemblage.linked_product_id.get_plans()
                    if pl:
                        plans += pl
                return plans
            else:
                return product.plan_ids
    
    def get_technicals(self):
        for product in self:
            if product.is_assemblage_product:
                if product.technical_ids:
                    plans = product.technical_ids[:]
                else:
                    plans = []
                for assemblage in product.assemblage_ids:
                    tec = assemblage.linked_product_id.get_technicals()
                    if tec:
                        plans += tec
                return plans
            else:
                return product.technical_ids


class ProductCron(models.Model):
    _name ="locasix.product.cron"
    _description = "Archivage automatique des produits temporaire"

    def run_cron(self):
        _logger.info("Cron product")
        products = self.env["product.template"].search([("active", "=", True), ("is_temporary_product", "=", True)])
        for product in products:
            product.active = False