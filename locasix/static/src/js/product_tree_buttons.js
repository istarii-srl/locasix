/**
odoo.define("locasix.product.buttons", function (require) {
    "use strict";
    var ListController = require("web.ListController");
    var ListView = require("web.ListView");
  
    var viewRegistry = require("web.view_registry");
  
    function renderProductTreeButtons() {
      if (this.$buttons) {
        var self = this;
        this.$buttons.on("click", ".o_button_export_product", function () {
          self.do_action({
            name: "Exporter les produits",
            type: "ir.actions.act_window",
            res_model: "locasix.product.export",
            target: "new",
            views: [[false, "form"]],
            context: { is_modal: true },
          });
        });
        this.$buttons.on("click", ".o_button_import_product", function () {
            self.do_action({
              name: "Importer les produits",
              type: "ir.actions.act_window",
              res_model: "locasix.product.import",
              target: "new",
              views: [[false, "form"]],
              context: { is_modal: true },
            });
          });
      }
    }
  
    var ProductTreeButtonsListController = ListController.extend({
      willStart: function () {
        var self = this;
        var ready = this.getSession().user_has_group('base.group_no_one').then(function (_) {
          self.buttons_template = "ProductTreeButtonsListView.buttons";
        });
        return Promise.all([this._super.apply(this, arguments), ready]);
      },
      renderButtons: function () {
        this._super.apply(this, arguments);
        renderProductTreeButtons.apply(this, arguments);
      },
    });
  
    var ProductTreeButtonsListView = ListView.extend({
      config: _.extend({}, ListView.prototype.config, {
        Controller: ProductTreeButtonsListController,
      }),
    });
  
    viewRegistry.add("locasix_product_tree_buttons", ProductTreeButtonsListView);
  });
  
 */
  odoo.define('locasix.product_tree_view_button', function (require){
    "use strict";

    var ajax = require('web.ajax');
    var ListController = require('web.ListController');

    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            var self = this;
            if (this.$buttons) {
                $(this.$buttons).find('.o_button_export_product').on('click', function() {
                  self.do_action({
                    name: "Exporter les produits",
                    type: "ir.actions.act_window",
                    res_model: "locasix.product.export",
                    target: "new",
                    views: [[false, "form"]],
                    context: { is_modal: true },
                  });                 //custom code
                });
            }
        },
    });
});