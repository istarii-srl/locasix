from odoo import fields, api, models
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class OrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = "sale.order.line"

    has_ref_to_condi = fields.Boolean(string="C.A.", default=False)
    show_images = fields.Boolean(string="Ajout Fiches", default=True)

    is_section = fields.Boolean(string="Est une section de l'offre", default=False)
    category_id = fields.Many2one(comodel_name="product.category", string="Product category")
    section_id = fields.Many2one(comodel_name="sale.order.line", string="Section")
    is_multi = fields.Boolean(string="A plusieurs tarifs", default=False)
    from_compute = fields.Boolean(string="Est venu automatiqument", default=False)
    usage_rate_display = fields.Selection(related="order_id.usage_rate_display")
    show_discount2 = fields.Boolean(related="order_id.show_discount2")
    show_discount3 = fields.Boolean(related="order_id.show_discount3")
    show_discount6 = fields.Boolean(related="order_id.show_discount6")
    offer_type = fields.Selection(string="Type d'offre", related="order_id.offer_type")
    has_24_price = fields.Boolean(string="Option 24/24", related="product_id.product_tmpl_id.has_24_price")
    has_months_discounts = fields.Boolean(string="Appliquer les réductions sur locations longues durées", default=True)
    temporary_product = fields.Boolean(string="Temporaire", related="product_id.is_temporary_product", readonly=False, default=False)
    extra_cost_link = fields.Many2one(string="Extra costs link", comodel_name="sale.order.line")

    day_price = fields.Float(string="Prix/jour", default=0.0)
    week_price = fields.Float(string="Prix/sem.", default=0.0)
    month_price = fields.Float(string="Prix/mois", default=0.0)

    months_2_discount_rate = fields.Float(string="Taux remise 2", related="order_id.months_2_discount_rate")
    months_3_discount_rate = fields.Float(string="Taux remise 3", related="order_id.months_3_discount_rate")
    months_6_discount_rate = fields.Float(string="Taux remise 6", related="order_id.months_6_discount_rate")

    months_2_discount = fields.Float(string="Remise 2", compute="_compute_2_discount", store=True)
    months_3_discount = fields.Float(string="Remise 3", compute="_compute_3_discount", store=True)
    months_6_discount = fields.Float(string="Remise 6", compute="_compute_6_discount", store=True)

    def show_discount_rates(self):
        for line in self:
            if not line.has_months_discounts or (line.product_id and not line.product_id.categ_id.has_months_discounts):
                return False
            else:
                return (line.show_discount2 or line.show_discount3 or line.show_discount6)


    def get_line_type(self):
        for line in self:
            if line.offer_type == "weekend" and line.usage_rate_display == "duo" and line.has_24_price:
                return "weekend_double"
            elif line.offer_type == "weekend" and line.usage_rate_display == "24" and line.has_24_price:
                return "weekend_24"
            elif line.offer_type == "weekend" and line.usage_rate_display == "8" and line.has_24_price:
                return "weekend_8"
            elif line.offer_type == "weekend":
                return "weekend"
            elif line.is_multi and line.usage_rate_display == "duo" and line.show_discount_rates() and line.has_24_price:
                return "prix_6_double"
            elif line.is_multi and line.usage_rate_display == "24" and line.show_discount_rates() and line.has_24_price:
                return "prix_6_24"
            elif line.is_multi and line.usage_rate_display == "8" and line.show_discount_rates() and line.has_24_price:
                return "prix_6_8"
            elif line.is_multi and line.usage_rate_display == "duo" and not line.show_discount_rates() and line.has_24_price:
                return "prix_3_double"
            elif line.is_multi and line.usage_rate_display == "24" and not line.show_discount_rates() and line.has_24_price:
                return "prix_3_24"
            elif line.is_multi and line.usage_rate_display == "8" and not line.show_discount_rates() and line.has_24_price:
                return "prix_3_8"
            elif line.is_multi and line.show_discount_rates():
                return "prix_6"
            elif line.is_multi and not line.show_discount_rates():
                return "prix_3"
            elif not line.is_multi and line.product_id and line.product_id.uom_id.name == "Jours" and line.has_24_price and line.usage_rate_display == "duo":
                return "prix_jour_double"
            elif not line.is_multi and line.product_id and line.product_id.uom_id.name == "Jours" and line.has_24_price and line.usage_rate_display == "24":
                return "prix_jour_24"
            elif not line.is_multi and line.product_id and line.product_id.uom_id.name == "Jours" and line.has_24_price and line.usage_rate_display == "8":
                return "prix_jour_8"
            elif not line.is_multi and line.product_id and line.product_id.uom_id.name == "Jours":
                return "prix_jour"
            elif not line.is_multi and line.product_id and line.product_id.uom_id.name == "Mois":
                return "prix_mois"
            else:
                return "prix_fixe"

    def is_section_multi(self):
        for line in self:
            section_type = line.get_section_type()
            if "6" in section_type or "3" in section_type:
                return True
            else:
                return False
    
    def is_section_condi(self):
        for line in self:
            section_lines = line.order_id.retrieve_lines_from_section_without_id(line)
            res = False
            for section_line in section_lines:
                if section_line.has_ref_to_condi:
                    res = True
            return res

    def get_section_type(self):
        #section weekend - done
        #section prix jour
        # section prix fixe
        # section 3 prix - done
        # section 3 prix 8h - done
        # section 3 prix 24h - done
        # section 6 prix - done
        # section 6 prix 8 - done
        # section 6 prix 24 - done
        # section prix jour 24
        # section 3 prix double - done
        # section 6 prix double - done
        # secttion prix jour double
        # section forfait mensuel
        for line in self:
            precedence = {
               "weekend_double": 0,
               "weekend_24": 1,
               "weekend_8": 2,
               "weekend":3,
               "prix_6_double": 4,
               "prix_6_24": 5,
               "prix_6_8": 5,
               "prix_3_double": 5,
               "prix_3_24": 6,
               "prix_3_8": 6,
               "prix_6": 7,
               "prix_3": 8,
               "prix_jour_double": 9,
               "prix_jour_8": 10,
               "prix_jour_24": 10,
               "prix_mois": 11,
               "prix_jour": 12,
               "prix_fixe": 13
            }
            section_lines = line.order_id.retrieve_lines_from_section_without_id(line)
            best_type = "prix_fixe"
            prec = 13
            best_has_24 = False
            hour_suffix = ""
            for line in section_lines:
                line_type = line.get_line_type()
                line_prec = precedence[line_type]
                if line_prec < prec:
                    best_has_24 = line.has_24_price
                    best_type = line_type
                    prec = line_prec
                if line.has_24_price and line.usage_rate_display == "duo":
                    hour_suffix = "_double"
                elif line.has_24_price and line.usage_rate_display == "24":
                    hour_suffix = "_24"
                elif line.has_24_price and line.usage_rate_display == "8":
                    hour_suffix = "_8"
                
            if not best_has_24:
                best_type+hour_suffix
                
            return best_type

    # CHANGE SEQUENCE
    def recompute_insurance(self):
        for line in self:
            if not line.order_id.is_computing:
                line.order_id.enforce_computations()
    


    @api.depends('month_price','months_2_discount_rate')
    def _compute_2_discount(self):
        for line in self:
            if line.product_id and line.product_id.categ_id and not line.product_id.categ_id.has_months_discounts:
                line.months_2_discount = line.month_price
            else:
                line.months_2_discount = line.month_price * (1-line.months_2_discount_rate)

    @api.depends('month_price','months_3_discount_rate')
    def _compute_3_discount(self):
        for line in self:
            if line.product_id and line.product_id.categ_id and not line.product_id.categ_id.has_months_discounts:
                line.months_3_discount = line.month_price
            else:
                line.months_3_discount = line.month_price * (1-line.months_3_discount_rate)

    @api.depends('month_price','months_6_discount_rate')
    def _compute_6_discount(self):
        for line in self:
            if line.product_id and line.product_id.categ_id and not line.product_id.categ_id.has_months_discounts:
                line.months_6_discount = line.month_price
            else:
                line.months_6_discount = line.month_price * (1-line.months_6_discount_rate)


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

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(OrderLine, self).product_id_change()
        self.update_line_values()
        return res
    
    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        res = super(OrderLine, self).product_uom_change()
        self.update_line_values()
        return res        

    @api.onchange('product_id', 'order_id', 'offer_type')
    def product_changed(self):
        _logger.info("product changed")
        self.update_line_values()
        _logger.info(self.category_id)
        _logger.info(self.price_unit)
        _logger.info(self._origin.price_unit)

    def write(self, vals):
        _logger.info("write order line")
        _logger.info(vals)

        if vals.get('day_price', False) or vals.get('week_price', False) or vals.get('month_price', False) or vals.get('months_2_discount', False) or vals.get('months_3_discount', False) or vals.get('months_6_discount', False) or vals.get('price_unit', False) or vals.get('sequence', False) or vals.get("product_uom_qty", False):
            vals.pop("from_update", 1)
            if vals.get("from_compute_ins", False) or vals.get('from_transport', False):
                vals.pop("from_transport", None)
                vals.pop("from_compute_ins", None)
                res = super(OrderLine, self).write(vals)
            else:
                res = super(OrderLine, self).write(vals)
                if self.product_id and self.product_id.default_code in ["TA", "TR"] and vals.get('price_unit', False):
                    self.update_transport_costs(vals.get('price_unit'))
                if self.product_id and self.product_id.default_code in ["FASSA", "FASSR"] and vals.get('price_unit', False):
                    self.update_assemblage_costs(vals.get('price_unit'))
                self.recompute_insurance()


        if (vals.get('product_id', False) or 'offer_type' in vals) and not vals.get("from_update", False):
            vals.pop("from_update", 1)
            res = super(OrderLine, self).write(vals)
            self.update_line_values(pricing=False)
            self.enforce_cuve()
            self.recompute_insurance()
            
            
        else:
            vals.pop("from_update", 1)
            vals.pop("from_transport", None)
            vals.pop("from_compute_ins", None)
            res = super(OrderLine, self).write(vals)
        return res

    def update_assemblage_costs(self, new_price):
        _logger.info("update assemblage costs")
        for line in self:
            assemblage_product = False
            if line.product_id.default_code == "FASSA":
                assemblage_product = self.env["product.product"].search([("default_code", "=", "FASSR")], limit=1)
            elif line.product_id.default_code == "FASSR":
                assemblage_product = self.env["product.product"].search([("default_code", "=", "FASSA")], limit=1)

            if assemblage_product:
                other_transport_line = self.env["sale.order.line"].search([("product_id", "=", assemblage_product.id)], limit=1)
                if other_transport_line:
                    other_transport_line.write({
                        "price_unit": new_price,
                        "from_transport": True
                    })


    def update_transport_costs(self, new_price):
        _logger.info("update transport costs")
        for line in self:
            transport_product = False
            if line.product_id.default_code == "TA":
                transport_product = self.env["product.product"].search([("default_code", "=", "TR")], limit=1)
            elif line.product_id.default_code == "TR":
                transport_product = self.env["product.product"].search([("default_code", "=", "TA")], limit=1)

            if transport_product:
                other_transport_line = self.env["sale.order.line"].search([("product_id", "=", transport_product.id)], limit=1)
                if other_transport_line:
                    other_transport_line.write({
                        "price_unit": new_price,
                        "from_transport": True
                    })

    def enforce_cuve(self):
        _logger.info("line enforce cuve")
        for line in self:
            if not line.order_id.is_computing:
                line.order_id.enforce_cuve()

    @api.model
    def create(self, vals):
        _logger.info("in create order lines")
        _logger.info(vals)
        obj = super(OrderLine, self).create(vals)
        obj.update_line_values(pricing=False)
        obj.enforce_cuve()
        if obj.display_type == "line_section":
            obj.is_section = True
        return obj

    def is_insurance(self):
        for line in self:
            return line.product_id.is_insurance

    def is_transport(self):
        for line in self:
            categ_id = self.env["product.category"].search([("name", "=", "Transport")], limit=1)
            if not categ_id:
                categ_id = self.env["product.category"].create({
                    "name": "Transport",
                    "show_section_order": True,
                })
            return line.product_id.categ_id.id == categ_id.id 

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
                    if not section_line.is_insurance() and section_line.product_id:
                        if is_multi:
                            day_price += section_line.day_price * percentage * section_line.product_uom_qty
                            week_price += section_line.week_price * percentage * section_line.product_uom_qty
                            month_price += section_line.month_price * percentage * section_line.product_uom_qty
                        else:
                            price_unit += section_line.price_unit * percentage * section_line.product_uom_qty

                if line.get_section_type() == "prix_mois":
                    uom = self.env["uom.uom"].search([("name", "=", "Mois")], limit=1)
                    if not uom:
                        uom = line.product_uom
                else:
                    uom = uom = self.env["uom.uom"].search([("name", "=", "Jours")], limit=1)
                    if not uom:
                        uom = line.product_uom
                _logger.info(price_unit)
                _logger.info(day_price)
                vals = {"price_unit": price_unit, "product_uom": uom, "day_price": day_price, "week_price": week_price, "month_price": month_price , 'from_compute_ins': True}
                line.write(vals)
            elif line.is_transport() and line.product_id.default_code in ["SURCA", "SURCAR", "SURCR"]:
                price = 0
                rate = float(self.env['ir.config_parameter'].sudo().get_param('locasix.extra_cost_transport_rate'))
                categ_id = self.env["product.category"].search([("name", "=", "Transport")], limit=1)
                if not categ_id:
                    categ_id = self.env["product.category"].create({
                        "name": "Transport",
                        "show_section_order": True,
                    })
                for section in section_lines:
                    if section.product_id and section.product_id.default_code and line.extra_cost_link and line.extra_cost_link.id == section.id:
                        price = rate * section.price_unit

                        # if section.product_id.categ_id.id == categ_id.id and section.product_id.default_code in ["TAR", "TA/R", "TA/RC"] and line.product_id.default_code == "SURCAR":
                        #     price = rate * section.price_unit
                        # elif section.product_id.categ_id.id == categ_id.id and "TA" in section.product_id.default_code and line.product_id.default_code == "SURCA":
                        #     price = rate * section.price_unit
                        # elif section.product_id.categ_id.id == categ_id.id and "TR" in section.product_id.default_code and line.product_id.default_code == "SURCR":
                        #     price = rate * section.price_unit
                vals = {"price_unit": price, 'from_compute_ins': True}
                line.write(vals)

    def update_line_values(self, pricing=True):
        if self.product_id:
            product = self.product_id.product_tmpl_id
            _logger.info("update line values")
            _logger.info(product.weekend_price)
            _logger.info(product.name)
            _logger.info(product.has_multi_price)
            _logger.info(self.offer_type)
            _logger.info(product.categ_id)
            vals = {}
            if not self.category_id:
                vals["category_id"] = product.categ_id
            if pricing:
                vals["day_price"] = product.day_price
                vals["week_price"] = product.week_price
                vals["month_price"] = product.month_price
            vals["has_ref_to_condi"] = product.has_ref_to_condi
            vals["is_multi"] = product.has_multi_price
            vals["from_update"] = True
            if pricing:
                if self.offer_type == "weekend" and product.weekend_price and product.weekend_price != 0.0:
                    _logger.info("update price for weekend")
                    if self.order_id.pricelist_id:
                        lst_price = product.lst_price
                        product.lst_price = product.weekend_price
                        vals["price_unit"] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(self.product_id), self.product_id.taxes_id, self.tax_id, self.company_id)
                        _logger.info("reset 2")
                        _logger.info(lst_price)
                        product.lst_price = lst_price
                    else:
                        vals["price_unit"] = product.weekend_price
                else:
                    if self.order_id.pricelist_id:
                        vals["price_unit"] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(self.product_id), self.product_id.taxes_id, self.tax_id, self.company_id)
                    else:
                        vals["price_unit"] = product.lst_price
            self.write(vals)