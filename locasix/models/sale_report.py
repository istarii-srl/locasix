# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    city = fields.Many2one(string="Ville", comodel_name="locasix.municipality")
    offer_type = fields.Selection(string="Type d'offre", selection=[("classic", "Location"), ("weekend", "Weekend"), ("sale", "Vente")], default="classic")

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['city'] = "s.city"
        res['offer_type'] = "s.offer_type"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.city,
            s.offer_type"""
        return res
