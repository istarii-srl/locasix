from odoo import api, fields, models
import xlrd
import tempfile
import binascii
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)



class ImportClients(models.TransientModel):
    _name = "locasix.client.import"
    _description = "Assitant pour l'importation de la base de donnée externe de client"

    file = fields.Binary(string="File", required=True, attachment=False)


    def import_clients(self):
        _logger.info("Import clients")
        #try:
        for wizard in self:
            fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fp.write(binascii.a2b_base64(wizard.file))
            fp.seek(0)
            book = xlrd.open_workbook(fp.name)
            sheet = book.sheet_by_index(0)
            lines = []
            for i in range(10, sheet.nrows):
                data_line = {
                    "compte": sheet.cell_value(i, 0),
                    "company_name": sheet.cell_value(i, 1), 
                    "street": sheet.cell_value(i, 3), 
                    "country/code": sheet.cell_value(i, 4),
                    "municipality": sheet.cell_value(i, 5),
                    "contact_name": sheet.cell_value(i, 6),
                    "TVA": sheet.cell_value(i, 8),
                    "company_title": sheet.cell_value(i, 13),
                    "phone": sheet.cell_value(i, 14),
                    "mobile": sheet.cell_value(i, 16),
                    "email": sheet.cell_value(i, 17),
                    "notes": sheet.cell_value(i, 18),
                    "email_compta": sheet.cell_value(i, 25),
                    "condi_payment": sheet.cell_value(i, 56),
                }
                lines.append(data_line)
                _logger.info(data_line)

            for line in lines:
                real_company_name = line["company_name"] + line["company_title"] if line["company_title"] else ""
                company = self.env["res.partner"].search([("name", "=", real_company_name)], limit=1)
                if not company:
                    company = self.env["res.partner"].create({
                        "name": real_company_name,
                        "compte": line["compte"],
                        "street": line["street"],
                        "zip": line["country/code"].split("-")[1],
                        "city": line["municipality"],
                        "vat": line["TVA"],
                        "phone": line["phone"],
                        "mobile": line["mobile"],
                        "email": line["email"],
                        "comment": line["notes"]
                    })
                if line["contact_name"]:
                    company_contact = self.env["res.partner"].search([("parent_id", "=", company.id), ("name", "=", line["contact_name"])], limit=1)
                    if not company_contact:
                        company_contact = self.env["res.partner"].create({"name": line["contact_name"], "parent_id": company.id})
                if line["email_compta"]:
                    compta_contact = self.env["res.partner"].search([("parent_id", "=", company.id), ("email", "=", line["email_compta"])], limit=1)
                    if not compta_contact:
                        compta_contact = self.env["res.partner"].create({
                            "parent_id": company.id,
                            "email": line["email_compta"]
                        })
                                
        #except Exception as e:
        #    _logger.error(e)
        #    raise ValidationError('Le fichier xls est incorrect')