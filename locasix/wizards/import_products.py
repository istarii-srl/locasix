from odoo import fields, api, models
import xlrd
import tempfile
import binascii
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ImportProducts(models.TransientModel):
    _name = "locasix.product.import"
    _description = "Assistant pour l'importation de nouveaux produits"

    file = fields.Binary(string="File", required=True, attachment=False)


    def import_products(self):
        _logger.info("Import products")

        try:
            for wizard in self:
                fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
                fp.write(binascii.a2b_base64(wizard.file))
                fp.seek(0)
                book = xlrd.open_workbook(fp.name)
                mono_product_sheet = book.sheet_by_index(0)
                multi_product_sheet = book.sheet_by_index(1)
                link_sheet = book.sheet_by_index(2)
                wizard.create_mono_tarif_products(mono_product_sheet)
                wizard.create_multi_tarif_products(multi_product_sheet)
                wizard.create_links(link_sheet)
                                   
        except Exception as e:
            _logger.error(e)
            raise ValidationError('Le fichier xls est incorrect')

    def create_mono_tarif_products(self, sheet):
        lines = []
        for i in range(1, sheet.nrows):
            lines.append({
                "name": sheet.cell_value(i, 0), 
                "ref": sheet.cell_value(i, 1), 
                "description": sheet.cell_value(i, 2),
                "details": sheet.cell_value(i, 3),
                "24h": sheet.cell_value(i, 4),
                "cat": sheet.cell_value(i, 5),
                "price": sheet.cell_value(i, 6),
                "uom": sheet.cell_value(i, 7),
                "weekend_price": sheet.cell_value(i, 8),
                "condi": sheet.cell_value(i, 9),
                "assemblage": sheet.cell_value(i, 10),
                "visible_agenda": sheet.cell_value(i, 11),
                "should_notify_assembler": sheet.cell_value(i, 12),
            })
        for line in lines:
            product = self.env["product.template"].search([("default_code", "=", line["ref"])], limit=1)
            #if not product:
            #    product = self.env["product.template"].search([("name", "=", line["name"])], limit=1)
            uom_id = self.env["uom.uom"].search([("name", "=", line["uom"])], limit=1)

            categ_id = self.env["product.category"].search([("name", "=", line["cat"])], limit=1)
            if not categ_id:
                categ_id = self.env["product.category"].create({
                    "name": line["cat"],
                    "show_section_order": True,
                })
            if not product and line["ref"]:
                product = self.env["product.template"].create({
                    "name": line["name"],
                    "default_code": line["ref"],
                })
            else:
                product.name = line["name"]

            if product:
                _logger.info(str(product.name) + " " + str(product.should_notify_assembler))

                product.uom_id = uom_id
                product.uom_po_id = uom_id
                product.product_description = line["description"]
                product.has_24_price = line["24h"]
                product.categ_id = categ_id
                product.should_notify_assembler = line["should_notify_assembler"]
                product.is_temporary_product = False
                product.is_assemblage_product = line["assemblage"]
                product.has_multi_price = False
                product.is_agenda_visible = line["visible_agenda"]
                product.has_ref_to_condi = line["condi"]
                
                product.list_price = line["price"]
                product.weekend_price = line["weekend_price"]
                product.more_details_link = line["details"]
            
    def create_multi_tarif_products(self, sheet):
        lines = []
        for i in range(1, sheet.nrows):
            lines.append({
                "name": sheet.cell_value(i, 0), 
                "ref": sheet.cell_value(i, 1), 
                "description": sheet.cell_value(i, 2),
                "details": sheet.cell_value(i, 3),
                "24h": sheet.cell_value(i, 4),
                "cat": sheet.cell_value(i, 5),
                "day_price": sheet.cell_value(i, 6),
                "week_price": sheet.cell_value(i, 7),
                "month_price": sheet.cell_value(i, 8),
                "weekend_price": sheet.cell_value(i, 9),
                "condi": sheet.cell_value(i, 10),
                "assemblage": sheet.cell_value(i, 11),
                "visible_agenda": sheet.cell_value(i, 12),
                "should_notify_assembler": sheet.cell_value(i, 13),
            })
        for line in lines:
            product = self.env["product.template"].search([("default_code", "=", line["ref"])], limit=1)
            #if not product:
            #    product = self.env["product.template"].search([("name", "=", line["name"])], limit=1)            
            
            categ_id = self.env["product.category"].search([("name", "=", line["cat"])], limit=1)
            if not categ_id:
                categ_id = self.env["product.category"].create({
                    "name": line["cat"],
                    "show_section_order": True,
                })

            if not product and line["ref"]:
                product = self.env["product.template"].create({
                    "name": line["name"],
                    "default_code": line["ref"],
                })
            else:
                product.name = line["name"]
                
            uom_id = self.env["uom.uom"].search([("name", "=", "Unité(s)")], limit=1)
            if product:
                product.uom_id = uom_id
                product.uom_po_id = uom_id  
                product.product_description = line["description"]
                product.has_24_price = line["24h"]
                product.has_multi_price = True
                product.should_notify_assembler = line["should_notify_assembler"]
                product.is_agenda_visible = line["visible_agenda"]
                product.categ_id = categ_id
                product.is_temporary_product = False
                product.is_assemblage_product = line["assemblage"]
                product.has_ref_to_condi = line["condi"]
                product.weekend_price = line["weekend_price"]
                product.more_details_link = line["details"]
                product.day_price = line["day_price"]
                product.week_price = line["week_price"]
                product.month_price = line["month_price"]

    def create_links(self, sheet):
        lines = []
        for i in range(1, sheet.nrows):
            lines.append({
                "actives": sheet.cell_value(i, 0), 
                "passive": sheet.cell_value(i, 1),
                "is_on_classic": sheet.cell_value(i, 2),
                "is_on_weekend": sheet.cell_value(i, 3),
                "is_on_sale": sheet.cell_value(i, 4),
            })
        for line in lines:
            actives = line["actives"].split(";")
            passive = self.env["product.template"].search([("default_code", "=", line["passive"])], limit=1)
            if passive:
                for active in actives:
                    active_product = self.env["product.template"].search([("default_code", "=", active)], limit=1)
                    if active_product:
                        link = self.env["locasix.product.link"].search([("product_master_id", "=", active_product.id), ("product_linked_id", "=", passive.id)], limit=1)
                        if not link:
                            link = self.env["locasix.product.link"].create({
                                "product_master_id": active_product.id,
                                "product_linked_id": passive.id
                            })
                        link.is_on_classic = line["is_on_classic"]
                        link.is_on_weekend = line["is_on_weekend"]
                        link.is_on_sale = line["is_on_sale"]