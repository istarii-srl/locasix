from odoo import _, api, fields, models

import logging


_logger = logging.getLogger(__name__)

class MarkLostPopup(models.TransientModel):
    _name = "locasix.mark.lost"
    _description = "Locasix mark lost popup"

    order_id = fields.Many2one(string="Commande", comodel_name="sale.order", required=True)

    lost_reason = fields.Many2one(string="Raison de refus", comodel_name="locasix.lost.reason", required=True)

    note = fields.Text(string="Note")


    def confirm(self):
        for wizard in self:
            wizard.order_id.lost_reason = wizard.lost_reason
            wizard.order_id.note_lost = wizard.note
            wizard.order_id.state = "lost"