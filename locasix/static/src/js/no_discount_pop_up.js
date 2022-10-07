odoo.define("locasix.SaleOrderView", function (require) {
  "use strict";

  const FormController = require("sale.SaleOrderView");
  const FormView = require("web.FormView");
  const viewRegistry = require("web.view_registry");
  const Dialog = require("web.Dialog");
  const core = require("web.core");
  const _t = core._t;

  FormController.include({
    // -------------------------------------------------------------------------
    // Handlers
    // -------------------------------------------------------------------------

    /**
     * Handler called if user changes the discount field in the sale order line.
     * The wizard will open only if
     *  (1) Sale order line is 3 or more
     *  (2) First sale order line is changed to discount
     *  (3) Discount is the same in all sale order line
     */
    _onOpenDiscountWizard(ev) {
      console.log("No discount");
    },
  });

  const SaleOrderView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
      Controller: SaleOrderFormController,
    }),
  });

  viewRegistry.add("sale_discount_form", SaleOrderView);

  return SaleOrderView;
});
