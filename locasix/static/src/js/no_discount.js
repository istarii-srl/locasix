/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import ProductDiscountField from "@sale/js/product_discount_field";

patch(ProductDiscountField.prototype, "debug mps", {
    onChange(ev) {
        console.log("Test");
  },

});