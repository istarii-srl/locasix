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

    day_price = fields.Float(string="Prix/jour")
    week_price = fields.Float(string="Prix/sem.")
    month_price = fields.Float(string="Prix/mois")

    months_2_discount = fields.Float(string="Remise 2")
    months_3_discount = fields.Float(string="Remise 3")
    months_6_discount = fields.Float(string="Remise 6")


    @api.constrains('sequence')
    def check_if_in_right_section(self):
        _logger.info("check right section")
        for line in self:
            if line.product_id and not line.is_section and line.product_id.categ_id.show_section_order:
                top_section = line.retrieve_top_section()
                if top_section and top_section.category_id:
                    if top_section.category_id.id != line.product_id.categ_id.id:
                        raise UserError("Ce produit ne peut pas être déplacer hors de sa section")
                elif not top_section and line.section_id:
                    raise UserError("Ce produit ne peut pas être déplacer hors de sa section")


    #@api.onchange('sequence')
    #def check_if_in_right_section_2(self):
    #    _logger.info("check right section")
    #    for line in self:
    #        if line.product_id and not line.is_section and line.product_id.categ_id.show_section_order:
    #            top_section = line.retrieve_top_section()
    #            _logger.info(line.section_id)
    #            _logger.info(top_section)
    #            if top_section and top_section.category_id:
    #                _logger.info("has top section")
    #                if top_section.category_id.id != line.product_id.categ_id.id:
    #                    line.sequence = line._origin.sequence
    #                    raise UserError("Ce produit ne peut pas être déplacer hors de sa section")
    #            elif not top_section and line.section_id:
    #                _logger.info("youhou")
    #                _logger.info(line.sequence)
    #                _logger.info(line._origin.sequence)
    #                line.sequence = line._origin.sequence
    #                raise UserError("Ce produit ne peut pas être déplacer hors de sa section")
    #    return

    def retrieve_top_section(self):
        nearest_top_section_id = False
        for line in self:
            seq = line.sequence
            for order_line in line.order_id.order_line:
                if order_line.is_section and order_line.sequence <= seq:
                    if nearest_top_section_id:
                        if order_line.sequence > nearest_top_section_id.sequence:
                            nearest_top_section_id = order_line
                    else:
                        nearest_top_section_id = order_line
        return nearest_top_section_id
        

    @api.model
    def create(self, vals):
        _logger.info("IN CREATE")
        line = super(OrderLine, self).create(vals)
        _logger.info(line.id)
        if line.product_id and line.order_id:
            line.enforce_links()
            line.enforce_section()
        return line
    
    def write(self, values):
        res = super(OrderLine, self).write(values)
        _logger.info("in write")
        _logger.info(values)
        if 'product_id' in values:
            self.enforce_links()
            self.enforce_section()
        return res

    @api.onchange('product_id', 'order_id')
    def product_changed(self):
        _logger.info("product changed")
        _logger.info(self._origin.order_id.id)
        _logger.info(self.order_id.id)
        _logger.info(self._origin.product_id.id)
        _logger.info(self.product_id.id)
        self.update_line_values
        return

    def enforce_section(self):
        for line in self:
            if line.product_id and line.order_id:
                if line.product_id.categ_id and line.product_id.categ_id.show_section_order:
                    section_id = self.env["sale.order.line"].search([("is_section", "=", True), ("category_id", "=", line.product_id.categ_id.id), ('order_id', "=", line.order_id.id)], limit=1)
                    if not section_id:
                        section_id = self.env["sale.order.line"].create({
                            "order_id": line.order_id.id,
                            "name": line.product_id.categ_id.name,
                            "category_id": line.product_id.categ_id.id,
                            "is_multi": line.product_id.has_multi_price,
                            "sequence": len(line.order_id.order_line)+1,
                            "display_type": "line_section",
                            'product_id': False,})
                        section_id.section_id = self.id
                    line.section_id = section_id.section_id
                    line.sequence = section_id.sequence+1
                    


    def enforce_links(self):
        _logger.info("in create lines")
        for line in self:
            if line.product_id and line.order_id:
                links = self.env["locasix.product.link"].search([("product_master_id", "=", line.product_id.id)])
                for link in links:
                    no_doublon = True
                    for order_line in line.order_id.order_line:
                        if order_line.product_id.id == link.product_linked_id.id:
                            no_doublon = False
                    if no_doublon:
                        new_line = self.env["sale.order.line"].create({'order_id': line.order_id.id, 'product_id': link.product_linked_id.id})
                        new_line.update_line_values()


    def is_insurance(self):
        for line in self:
            return line.product_id.code == "ASSM"

    def enforce_computation(self, is_multi):
        for line in self:
            if line.is_insurance():
                pass

    def update_line_values(self):
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