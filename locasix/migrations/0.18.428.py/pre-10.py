from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    allers = env["locasix.aller"].search([])
    for aller in allers:
        if aller.state =="progress":
            aller.state = "aprogress"