from odoo import fields, api, models
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class OrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = "sale.order.line"

    has_ref_to_condi = fields.Boolean(string="C.A.", default=False)

    is_section = fields.Boolean(string="Est une section de l'offre", default=False)
    category_id = fields.Many2one(comodel_name="product.category", string="Product category")
    section_id = fields.Many2one(comodel_name="sale.order.line", string="Section")
    is_multi = fields.Boolean(string="A plusieurs tarifs", default=False)
    from_compute = fields.Boolean(string="Est venu automatiqument", default=False)
    weekend_offer = fields.Boolean(string="Est une offre de weekend", related="order_id.weekend_offer")
    has_24_price = fields.Boolean(string="24h options", related="product_id.product_tmpl_id.has_24_price")

    day_price = fields.Float(string="Prix/jour", default=0.0)
    week_price = fields.Float(string="Prix/sem.", default=0.0)
    month_price = fields.Float(string="Prix/mois", default=0.0)

    months_2_discount = fields.Float(string="Remise 2")
    months_3_discount = fields.Float(string="Remise 3")
    months_6_discount = fields.Float(string="Remise 6")



    def retrieve_top_section(self, lines):
        nearest_top_section_id = False
        for line in self:
            seq = line.sequence
            for order_line in lines:
                if order_line.is_section and order_line.sequence <= seq:
                    if nearest_top_section_id:
                        if order_line.sequence > nearest_top_section_id.sequence:
                            nearest_top_section_id = order_line
                    else:
                        nearest_top_section_id = order_line
        return nearest_top_section_id

    @api.onchange('product_id', 'order_id', 'weekend_offer')
    def product_changed(self):
        _logger.info("product changed")
        self.update_line_values()
        _logger.info(self.category_id)
        _logger.info(self.price_unit)
        _logger.info(self._origin.price_unit)

    def write(self, vals):
        _logger.info("write order line")
        _logger.info(vals)
        
        if vals.get('product_id', False) and not vals.get("from_update", False):
            vals.pop("from_update", 1)
            res = super(OrderLine, self).write(vals)
            self.update_line_values()
            
        else:
            vals.pop("from_update", 1)
            res = super(OrderLine, self).write(vals)
        
        return res

    @api.model
    def create(self, vals):
        _logger.info("in create order lines")
        _logger.info(vals)
        obj = super(OrderLine, self).create(vals)
        obj.update_line_values()
        return obj


    def is_insurance(self):
        for line in self:
            return line.product_id.is_insurance

    def enforce_computation(self, is_multi, section_lines):
        for line in self:
            if line.is_insurance():
                percentage = line.product_id.insurance_percentage
                price_unit = 0.0
                day_price = 0.0
                week_price = 0.0
                month_price = 0.0
                _logger.info("MULTO")
                _logger.info(is_multi)
                for section_line in section_lines:
                    if not section_line.is_insurance():
                        if is_multi:
                            day_price += section_line.day_price * percentage
                            week_price += section_line.week_price * percentage
                            month_price += section_line.month_price * percentage
                        else:
                            price_unit += section_line.price_unit * percentage
                line.price_unit = price_unit
                line.day_price = day_price
                line.week_price = week_price
                line.month_price = month_price

    def update_line_values(self):
        if self.product_id:
            product = self.product_id.product_tmpl_id
            _logger.info("update line values")
            _logger.info(product.weekend_price)
            _logger.info(product.name)
            _logger.info(product.has_multi_price)
            _logger.info(self.weekend_offer)
            _logger.info(product.categ_id)
            vals = {}
            self.category_id = product.categ_id
            vals["day_price"] = product.day_price
            vals["week_price"] = product.week_price
            vals["month_price"] = product.month_price
            vals["months_2_discount"] = product.months_2_discount
            vals["months_3_discount"] = product.months_3_discount
            vals["months_6_discount"] = product.months_6_discount
            vals["has_ref_to_condi"] = product.has_ref_to_condi
            vals["is_multi"] = product.has_multi_price
            vals["from_update"] = True
            if self.weekend_offer and product.weekend_price and product.weekend_price != 0.0:
                _logger.info("update price for weekend")
                vals["price_unit"] = product.weekend_price 
            self.write(vals)