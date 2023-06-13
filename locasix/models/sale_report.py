# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    city = fields.Many2one(string="Ville", comodel_name="locasix.municipality")

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['city'] = "s.city"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.city"""
        return res
