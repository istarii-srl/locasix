from odoo import fields, api, models

import logging
_logger = logging.getLogger(__name__)


class OrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = "sale.order.line"

    has_ref_to_condi = fields.Boolean(string="C.A.", default=False)
    day_price = fields.Float(string="Prix/jour")
    week_price = fields.Float(string="Prix/sem.")
    month_price = fields.Float(string="Prix/mois")

    months_2_discount = fields.Float(string="Remise 2")
    months_3_discount = fields.Float(string="Remise 3")
    months_6_discount = fields.Float(string="Remise 6")

    def _prepare_add_missing_fields(self, values):
        _logger.info("YOYO")
        _logger.info(values)
        return super(OrderLine, self)._prepare_add_missing_fields(values)

    
    def write(self, values):
        res = super(OrderLine, self).write(values)
        if 'product_id' in values:
            links = self.env["locasix.product.link"].search([("product_master_id", "=", self.product_id.id)])
            if self.order_id:
                for link in links:
                    self.env["sale.order.line"].create({'order_id': self._origin.order_id.id, 'product_id': link.product_linked_id.id})
        return res

    @api.onchange('product_id', 'order_id')
    def product_changed(self):
        _logger.info("product changed")
        _logger.info(self._origin.order_id.id)
        _logger.info(self.order_id.id)
        _logger.info(self._origin.product_id.id)
        _logger.info(self.product_id.id)
        if self.product_id:
            product = self.product_id
            vals = {}
            vals['day_price'] = product.day_price
            vals['week_price'] = product.week_price
            vals['month_price'] = product.month_price
            vals['months_2_discount'] = product.months_2_discount
            vals['months_3_discount'] = product.months_3_discount
            vals['months_6_discount'] =product.months_6_discount
            vals['has_ref_to_condi'] = product.has_ref_to_condi
            self.update(vals)

        return
