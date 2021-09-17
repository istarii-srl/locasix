odoo.define("locasix.product_tree_view_button", function (require) {
  "use strict";

  var ajax = require("web.ajax");
  var ListController = require("web.ListController");
  var rpc = require("web.rpc");

  ListController.include({
    renderButtons: function ($node) {
      this._super.apply(this, arguments);
      var self = this;
      if (this.$buttons) {
        $(this.$buttons)
          .find(".o_button_export_product")
          .on("click", function () {
            self.do_action({
              name: "Exporter les produits",
              type: "ir.actions.act_window",
              res_model: "locasix.product.export",
              target: "new",
              views: [[false, "form"]],
              context: { is_modal: true },
            }); //custom code
          });
          $(this.$buttons)
          .find(".o_button_export_product")
          .on("click", function () {
            self.do_action({
              name: "Importer les produits",
              type: "ir.actions.act_window",
              res_model: "locasix.product.import",
              target: "new",
              views: [[false, "form"]],
              context: { is_modal: true },
            }); //custom code
          });
      }
    },
  });
});
