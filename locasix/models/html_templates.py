from odoo import fields, api, models

class CondiAddTemplate(models.Model):
    _name = "locasix.template.condi"
    _description = "Template pour les conditions additionnelles"

    name = fields.Char(string="Nom", default="Template des conditions additionnelles")
    template = fields.Html()
