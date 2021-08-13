from odoo import fields, api, models

import logging
_logger = logging.getLogger(__name__)


class OrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = "sale.order.line"

    has_ref_to_condi = fields.Boolean(string="cond. add.", default=False)

    def _prepare_add_missing_fields(self, values):
        _logger.info("YOYO")
        _logger.info(values)
        return super(OrderLine, self)._prepare_add_missing_fields(values)

    @api.onchange('product_id')
    def product_changed(self):
        _logger.info("product changed")
        if self.product_id:
            product = self.product_id
            vals = {}
            vals['has_ref_to_condi'] = product.has_ref_to_condi
            self.update(vals)
        return