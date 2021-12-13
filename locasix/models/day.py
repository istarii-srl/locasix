from odoo import fields, api, models
import datetime

import logging
_logger = logging.getLogger(__name__)

class Day(models.Model):
    _name = "locasix.day"

    _description = "Gestion des allers et retours pour une journée"

    name = fields.Char(string="Jour", compute="_compute_name", store=True)
    day = fields.Date(string="Date", required=True)
    aller_note = fields.Html(string="Notes allers")
    retour_note = fields.Html(string="Notes retours")

    active = fields.Boolean(string="Actif", default=True)

    aller_ids = fields.One2many(comodel_name="locasix.aller", inverse_name="day_id", string="Allers", domain= lambda self: self._get_default_aller_domain())
    retour_ids = fields.One2many(comodel_name="locasix.aller", inverse_name="day_id", string="Retours", domain= lambda self: self._get_default_retour_domain())

    notes = fields.Text(string="Notes")

    _sql_constraints = [
        ('day_uniq', 'unique (day)', "Cette date a déjà été utilisée. Veuillez en choisir une autre !"),
    ]

    def _get_default_aller_domain(self):
        if self.env.user.has_group('locasix.group_locasix_admin'):
            return [('aller_type', '=', 'out'), ('is_first_line', '=', False), '|', ('active', '=', False), ('active', '=', True)]
        else:
            return [('aller_type', '=', 'out'), ('is_first_line', '=', False), ('active', '=', True)]

    def _get_default_retour_domain(self):
        if self.env.user.has_group('locasix.group_locasix_admin'):
            return [('aller_type', '=', 'in'), '|', ('active', '=', False), ('active', '=', True)]
        else:
            return [('aller_type', '=', 'in'), ('active', '=', True)]

    def action_add_depl(self):
        view = self.env.ref('locasix.locasix_agg_aller_form')
        return {
        'name': 'Allers',
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'locasix.agg.aller',
        'views': [(view.id, 'form')],
        'view_id': view.id,
        'target': 'new',
        'context': {
            'default_is_depl': True,
            'default_aller_type': 'out',
            'default_day_id': self.id,
            'default_date': self.day,
            },
        }     

    def action_add_aller(self):
        view = self.env.ref('locasix.locasix_agg_aller_form')
        return {
        'name': 'Allers',
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'locasix.agg.aller',
        'views': [(view.id, 'form')],
        'view_id': view.id,
        'target': 'new',
        'context': {
            'default_aller_type': 'out',
            'default_day_id': self.id,
            'default_date': self.day,
            },
        }        

    def action_add_retour(self):
        view = self.env.ref('locasix.locasix_agg_retour_form')
        return {
        'name': 'Retours',
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'locasix.agg.aller',
        'views': [(view.id, 'form')],
        'view_id': view.id,
        'target': 'new',
        'context': {
            'default_aller_type': "in",
            'default_day_id': self.id,
            'default_date': self.day,
            },
        }  

    def action_modify(self):
        view = self.env.ref('locasix.view_modify_contract')
        return {
        'name': 'Modifier le statut',
        'type': 'ir.actions.act_window',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'locasix.modify.contract',
        'views': [(view.id, 'form')],
        'view_id': view.id,
        'target': 'new',
        'context': {
            'default_day_id': self.id,
            },
        }          

    def action_today(self):
        for day in self:
            today = datetime.date.today()
            day_id = self.env["locasix.day"].search([("day", "=", today)], limit=1)
            if day_id:
                view = self.env.ref("locasix.locasix_day_form")
                return {
                    'name': 'Journée',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'locasix.day',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': "main",
                    'res_id': day_id.id,
                    'context': {'active_id': day_id.id},
                }            

    def is_day_empty(self, day):
        if (day.aller_ids and len(day.aller_ids) > 0) or (day.retour_ids and len(day.retour_ids) > 0):
            if day.aller_ids:
                for aller in day.aller_ids:
                    if aller.active and not aller.is_first_line:
                        return False
            if day.retour_ids:
                for aller in day.retour_ids:
                    if aller.active and not aller.is_first_line:
                        return False
        return True

    def action_previous(self):
        for day in self:
            min_date = day.day - datetime.timedelta(days=40)
            previous_days = self.env["locasix.day"].search([("day", ">", min_date),("day", "<", day.day)])
            previous_days_sorted = sorted(previous_days, key= lambda x: x.day, reverse=True)
            for new_day in previous_days_sorted:
                if not day.is_day_empty(new_day):
                    view = self.env.ref("locasix.locasix_day_form")
                    return {
                        'name': 'Journée',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'locasix.day',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': "main",
                        'res_id': new_day.id,
                        'context': {'active_id': new_day.id},
                    }
            view = self.env.ref("locasix.locasix_day_form")
            if len(previous_days) > 0:
                return {
                    'name': 'Journée',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'locasix.day',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': "main",
                    'res_id': previous_days_sorted[0].id,
                    'context': {'active_id': previous_days_sorted[0].id},
                }

    def action_next(self):
        for day in self:
            max_date = day.day + datetime.timedelta(days=40)
            next_days = self.env["locasix.day"].search([("day", "<", max_date),("day", ">", day.day)])
            next_days_sorted = sorted(next_days, key= lambda x: x.day)
            for new_day in next_days_sorted:
                if not day.is_day_empty(new_day):
                    view = self.env.ref("locasix.locasix_day_form")
                    return {
                        'name': 'Journée',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'locasix.day',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': "main",
                        'res_id': new_day.id,
                        'context': {'active_id': new_day.id},
                    }
            view = self.env.ref("locasix.locasix_day_form")

            return {
                'name': 'Journée',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'locasix.day',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': "main",
                'res_id': next_days_sorted[0].id,
                'context': {'active_id': next_days_sorted[0].id},
            }
            

    @api.depends('day')
    def _compute_name(self):
        for day in self:
            if day.day:
                day.name = day.day.strftime('%d/%m/%Y')
            else:
                day.name = "En cours de création..."

class DayCron(models.Model):
    _name = "locasix.day.cron"
    _description = "Cron job to create days"

    def run_cron(self):
        _logger.info("CRON JOB Day")
        today = datetime.date.today()
        max_limit = today + datetime.timedelta(days=365)
        
        # Automated archiving
        #min_limit = today - datetime.timedelta(days=15)
        #days_to_archived = self.env["locasix.day"].search([("day", '<', min_limit)])
        #for day in days_to_archived:
        #    day.active = False

        days = self.env["locasix.day"].search([('day', '>=', today), ('day', '<', max_limit)])
        sorted_days = sorted(days, key=lambda day: day.day)
        new_day = today
        i = 0
        while new_day < max_limit and i < len(sorted_days):
            if sorted_days[i].day == new_day:
                i += 1
                new_day = new_day + datetime.timedelta(days=1)
            elif sorted_days[i].day < new_day:
                i += 1
            else:
                self.env["locasix.day"].create({
                    'day': new_day,
                })
                new_day = new_day + datetime.timedelta(days=1)
        while new_day < max_limit:
            self.env["locasix.day"].create({
                'day': new_day,
            })
            new_day = new_day + datetime.timedelta(days=1)

        return
