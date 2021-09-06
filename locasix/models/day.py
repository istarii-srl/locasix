from odoo import fields, api, models
import datetime

import logging
_logger = logging.getLogger(__name__)

class Day(models.Model):
    _name = "locasix.day"
    _description = "Gestion des allers et retours pour une journée"

    name = fields.Char(string="Jour", compute="_compute_name")
    day = fields.Date(string="Date", required=True)

    _sql_constraints = [
        ('day_uniq', 'unique (day)', "Cette date a déjà été utilisée. Veuillez en choisir une autre !"),
    ]
    # UNIQUE CONSTRAINTS


    @api.depends('day')
    def _compute_name(self):
        for day in self:
            if day.day:
                day.name = day.day.strftime('%m/%d/%Y')
            else:
                day.name = "En cours de création..."

class DayCron(models.Model):
    _name = "locasix.day.cron"
    _description = "Cron job to create days"

    def run_cron(self):
        _logger.info("CRON JOB Day")
        # ARCHIVE OLD DATES OR SOMETHING LIKE THAT
        today = datetime.date.today()
        max_limit = today + datetime.timedelta(days=180)
        days = self.env["locasix.day"].search([('date', '>=', today), ('date', '<', max_limit)])
        sorted_days = sorted(days, key=lambda day: day.day)
        new_day = today
        i = 0
        while new_day < max_limit:
            if sorted_days[i].day == new_day:
                i += 1
                new_day = new_day + datetime.timedelta(days=1)
            elif sorted_days[i.day].day < new_day:
                i += 1
            else:
                self.env["locasix.day"].create({
                    'day': new_day,
                })
                new_day = new_day + datetime.timedelta(days=1)

        return
