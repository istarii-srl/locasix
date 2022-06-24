from odoo import fields, api, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class PropositionMultiUpdate(models.TransientModel):
    _name = "locasix.proposition.multi.wizard"
    _description = "Proposition multi update"

    prop_ids = fields.Many2many(comodel_name="locasix.aller", string="Propositions", default=lambda self: self._default_prop_ids())

    user_id = fields.Many2one(string="Demandeur", comodel_name="res.users", default=lambda self: self.env.user)
    note = fields.Text(string="Remarque")
    date = fields.Date(string="Date", required=True)

    def _default_prop_ids(self):
        return self.env['locasix.aller'].browse(self._context.get('active_ids'))

    def validate(self):
        for wizard in self:
            agg_id = False
            is_boss = False
            is_boss = bool(wizard.user_id.has_group('locasix.group_locasix_admin') or wizard.user_id.has_group('locasix.group_locasix_agenda_resp'))
            _logger.info(is_boss)
            for prop in wizard.prop_ids:      
                if not agg_id:
                    agg_id = prop.agg_id.id
                elif agg_id != prop.agg_id.id:
                    raise UserError("Vous ne pouvez modifier des propositions que d'un même groupement")
                _logger.info(prop.proposition_status)
                if (prop.proposition_status != "pending_boss" and is_boss) or (prop.proposition_status != "pending_worker" and not is_boss):
                    raise UserError("Vous ne pouvez modifier que les propositions en attente de confirmation de la même personne (responsable ou demandeur)")
            i = 0
            for prop in wizard.prop_ids:
                prop.date = wizard.date
                if wizard.is_asking_confirmation:
                    prop.ask_confirmation(wizard.note if wizard.note else " ", i)
                else:
                    prop.ask_changes(wizard.note if wizard.note else " ", i)
                i += 1