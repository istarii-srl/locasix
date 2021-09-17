from odoo import fields, api, models

class NoTransportPriceWarning(models.TransientModel):
    _name = "locasix.transport.warning"
    _description = "Warning pop-up lorsqu'il manque des prix pour les transports"