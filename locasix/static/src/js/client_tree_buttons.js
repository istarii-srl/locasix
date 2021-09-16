odoo.define("locasix.client.buttons", function (require) {
  "use strict";
  var ListController = require("web.ListController");
  var ListView = require("web.ListView");

  var viewRegistry = require("web.view_registry");

  function renderClientTreeButtons() {
    if (this.$buttons) {
      var self = this;
      this.$buttons.on("click", ".o_button_import_client", function () {
        self.do_action({
          name: "Importer les clients",
          type: "ir.actions.act_window",
          res_model: "locasix.client.import",
          target: "new",
          views: [[false, "form"]],
          context: { is_modal: true },
        });
      });
    }
  }

  var ClientTreeButtonsListController = ListController.extend({
    willStart: function () {
      var self = this;
      var ready = this.getSession().user_has_group('base.group_no_one').then(function (_) {
        self.buttons_template = "ClientTreeButtonsListView.buttons";
      });
      return Promise.all([this._super.apply(this, arguments), ready]);
    },
    renderButtons: function () {
      this._super.apply(this, arguments);
      renderClientTreeButtons.apply(this, arguments);
    },
  });

  var ClientTreeButtonsListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
      Controller: ClientTreeButtonsListController,
    }),
  });

  viewRegistry.add("locasix_client_tree_buttons", ClientTreeButtonsListView);
});
