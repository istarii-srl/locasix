odoo.define("locasix.tree_button", function (require) {
  "use strict";
  var ListController = require("web.ListController");
  var ListView = require("web.ListView");
  var viewRegistry = require("web.view_registry");
  var TreeButton = ListController.extend({
    buttons_template: "locasix.client_buttons",
    events: _.extend({}, ListController.prototype.events, {
      "click .o_button_import_client": "_OpenWizard",
    }),
    _OpenWizard: function () {
      var self = this;
      // this._rpc({
      //   model: "mailing.mailing",
      //   method: "action_create_from_salesforce_campaign",
      // }).then(function (action) {
      //   return self.do_action({
      //     name: "Choose Salesforce campaign",
      //     type: "ir.actions.act_window",
      //     res_model: "salesforce.contact.import.wizard",
      //     target: "new",
      //     views: [[false, "form"]],
      //     context: { is_modal: true },
      //   });
      // });
      this.do_action({
        name: "Exporter les produits",
        type: "ir.actions.act_window",
        res_model: "locasix.client.import",
        target: "new",
        views: [[false, "form"]],
        context: { is_modal: true },
      });
    },
  });
  var LosixClientView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
      Controller: TreeButton,
    }),
  });
  viewRegistry.add("locasix_client_buttons", LosixClientView);
});