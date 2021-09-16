from odoo import api, fields, models


class ImportClients(models.TransientModel):
    _name = "locasix.client.import"
    _description = "Assitant pour l'importation de la base de donnée externe de client"

    file = fields.Binary(string="File", required=True, attachment=False)


    def import_clients(self):
        for wizard in self:
            return