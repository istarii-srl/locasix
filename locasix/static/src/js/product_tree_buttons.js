odoo.define("locasix.product_tree_button", function (require) {
  "use strict";
  var ListController = require("web.ListController");
  var ListView = require("web.ListView");
  var viewRegistry = require("web.view_registry");
  var TreeButton = ListController.extend({
    buttons_template: "locasix.product_buttons",
    events: _.extend({}, ListController.prototype.events, {
      "click .o_button_export_product": "_OpenWizardExport",
      "click .o_button_import_product": "_OpenWizardImport",
    }),
    _OpenWizardExport: function () {
      var self = this;
      this.do_action({
        name: "Exporter les produits",
        type: "ir.actions.act_window",
        res_model: "locasix.product.export",
        target: "new",
        views: [[false, "form"]],
        context: { is_modal: true},
      });
    },

    _OpenWizardImport: function () {
      var self = this;
      this.do_action({
        name: "Importer les produits",
        type: "ir.actions.act_window",
        res_model: "locasix.product.import",
        target: "new",
        views: [[false, "form"]],
        context: { is_modal: true },
      }); 
    },
  
  });
  var LocasixProductView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
      Controller: TreeButton,
    }),
  });
  viewRegistry.add("locasix_product_buttons", LocasixProductView);
});