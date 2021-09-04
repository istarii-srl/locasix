from odoo import fields, api, models

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

    day_price = fields.Float(string="Prix par jour")
    week_price = fields.Float(string="Prix par semaine")
    month_price = fields.Float(string="Prix par mois")

    months_2_discount = fields.Float(string="Remise 2 mois")
    months_3_discount = fields.Float(string="Remise 3 mois")
    months_6_discount = fields.Float(string="Remise 6 mois")

    technical_file = fields.Image(string="Fiche technique")

    is_insurance = fields.Boolean(string="Est une assurance", default=False)
    insurance_percentage = fields.Float(string="Pourcentage de la prime", default=0.08)