from odoo import fields, api, models
from datetime import timedelta
import logging
from xlsxwriter.workbook import Workbook
from odoo.exceptions import ValidationError
from io import BytesIO
import base64

_logger = logging.getLogger(__name__)

class ExportProducts(models.TransientModel):
    _name = "locasix.product.export"
    _description = "Assistance pour l'exportation de produits"

    from_button = fields.Boolean(default=True)
    product_ids = fields.Many2many(comodel_name="product.template", compute="_get_default_products")

    @api.depends('from_button')
    def _get_default_products(self):
        if self.from_button:
            self.product_ids = self.env["product.template"].search([("active", "=", True), ("is_temporary_product", "=", False), ("name", "!=", "Date aller"), ("name", '!=', "Date retour"), ("name", "!=", 'Adresse de transport')])
        else:
            self.product_ids = self.env['product.template'].browse(self._context.get('active_ids'))

    def export_products(self):
        _logger.info("Export products")
        for wizard in self:
            filename = "products.xlsx"
            self.env['ir.attachment'].search([('name' , '=', filename)]).unlink()
            fp = BytesIO()
            workbook = Workbook(fp, {'in_memory': True})
            mono_product_sheet = workbook.add_worksheet("mono products")
            multi_product_sheet = workbook.add_worksheet("multi products")
            link_sheet = workbook.add_worksheet("link sheet")
            wizard.create_mono_products_sheet(mono_product_sheet)
            wizard.create_multi_products_sheet(multi_product_sheet)
            wizard.create_links_sheet(link_sheet)

            workbook.close()
            fp.seek(0)

            record_id = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.encodebytes(fp.read()),
            })
            fp.close()
            _logger.info(record_id.name)
            return {
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=ir.attachment&id=" + str(record_id.id) + "&filename_field=name&field=datas&download=true&name=" + record_id.name,
                'target': 'self',
            }
    
    def create_mono_products_sheet(self, worksheet):
        _logger.info("create mono products sheet")
        for wizard in self:
            worksheet.set_column(0, 0, 25)
            worksheet.set_column(1, 1, 10)
            worksheet.set_column(2, 2, 35)
            worksheet.set_column(3, 3, 20)
            worksheet.set_column(4, 4, 10)
            worksheet.set_column(5, 5, 20)
            worksheet.set_column(6, 6, 15)
            worksheet.set_column(7, 7, 15)
            worksheet.set_column(8, 8, 15)
            worksheet.set_column(9, 9, 15)
            worksheet.set_column(10, 10, 15)
            worksheet.set_column(11, 11, 15)
            worksheet.set_column(12, 12, 15)
            worksheet.write(0, 0, "Nom")
            worksheet.write(0, 1, "Ref")
            worksheet.write(0, 2, "Description")
            worksheet.write(0, 3, "Plus de détails")
            worksheet.write(0, 4, "24 H ?")
            worksheet.write(0, 5, "Catégorie")
            worksheet.write(0, 6, "Prix")
            worksheet.write(0, 7, "Unité de mesure")
            worksheet.write(0, 8, "Prix weekend")
            worksheet.write(0, 9, "Ref condi add. ?")
            worksheet.write(0, 10, "Assemblage ?")
            worksheet.write(0, 11, "Visible agenda ?")
            worksheet.write(0, 12, "Notifier assembleur ?")
            row = 1
            for product in wizard.product_ids:
                if not product.has_multi_price:
                    worksheet.write(row, 0, product.name)
                    worksheet.write(row, 1, product.default_code if product.default_code else "")
                    worksheet.write(row, 2, product.product_description if product.product_description else "")
                    worksheet.write(row, 3, product.more_details_link if product.more_details_link else "")
                    worksheet.write(row, 4, product.has_24_price)
                    worksheet.write(row, 5, product.categ_id.name)
                    worksheet.write(row, 6, product.list_price)
                    worksheet.write(row, 7, product.uom_id.name)
                    worksheet.write(row, 8, product.weekend_price)
                    worksheet.write(row, 9, product.has_ref_to_condi)
                    worksheet.write(row, 10, product.is_assemblage_product)
                    worksheet.write(row, 11, product.is_agenda_visible)
                    worksheet.write(row, 12, product.should_notify_assembler)

                    row +=1

    
    def create_multi_products_sheet(self, worksheet):
        _logger.info("create multi products sheet")
        for wizard in self:
            worksheet.set_column(0, 0, 25)
            worksheet.set_column(1, 1, 10)
            worksheet.set_column(2, 2, 35)
            worksheet.set_column(3, 3, 20)
            worksheet.set_column(4, 4, 10)
            worksheet.set_column(5, 5, 20)
            worksheet.set_column(6, 6, 15)
            worksheet.set_column(7, 7, 15)
            worksheet.set_column(8, 8, 15)
            worksheet.set_column(9, 9, 15)
            worksheet.set_column(10, 10, 20)
            worksheet.set_column(11, 11, 15)
            worksheet.set_column(12, 12, 15)
            worksheet.set_column(13, 13, 15)
            worksheet.write(0, 0, "Nom")
            worksheet.write(0, 1, "Ref")
            worksheet.write(0, 2, "Description")
            worksheet.write(0, 3, "Plus de détails")
            worksheet.write(0, 4, "24 H ?")
            worksheet.write(0, 5, "Catégorie")
            worksheet.write(0, 6, "Prix jour")
            worksheet.write(0, 7, "Prix semaine")
            worksheet.write(0, 8, "Prix mois")
            worksheet.write(0, 9, "Prix weekend")
            worksheet.write(0, 10, "Ref condi add. ?")
            worksheet.write(0, 11, "Assemblage ?")
            worksheet.write(0, 12, "Visible agenda ?")
            worksheet.write(0, 13, "Notifier assembleur ?")

            row = 1
            for product in wizard.product_ids:
                if product.has_multi_price:
                    worksheet.write(row, 0, product.name)
                    worksheet.write(row, 1, product.default_code if product.default_code else "")
                    worksheet.write(row, 2, product.product_description if product.product_description else "")
                    worksheet.write(row, 3, product.more_details_link if product.more_details_link else "")
                    worksheet.write(row, 4, product.has_24_price)
                    worksheet.write(row, 5, product.categ_id.name)
                    worksheet.write(row, 6, product.day_price)
                    worksheet.write(row, 7, product.week_price)
                    worksheet.write(row, 8, product.month_price)
                    worksheet.write(row, 9, product.weekend_price)
                    worksheet.write(row, 10, product.has_ref_to_condi)
                    worksheet.write(row, 11, product.is_assemblage_product)
                    worksheet.write(row, 12, product.is_agenda_visible)
                    worksheet.write(row, 13, product.should_notify_assembler)
                    row +=1
    

    def link_to_hash(self, link):
        for wizard in self:
            hash_link = ""
            if link.is_on_classic:
                hash_link += "1"
            else:
                hash_link += "0"
            if link.is_on_weekend:
                hash_link += "1"
            else:
                hash_link += "0"
            if link.is_on_sale:
                hash_link += "1"
            else:
                hash_link += "0"
            return hash_link

    def is_hash_on_classic(self, hash_link):
        for wizard in self:
            if hash_link[0]  == "1":
                return True
            else:
                return False

    def is_hash_on_weeekend(self, hash_link):
        for wizard in self:
            if hash_link[1] == "1":
                return True
            else:
                return False

    def is_hash_on_sale(self, hash_link):
        for wizard in self:
            if hash_link[2] == "1":
                return True
            else:
                return False

    def create_links_sheet(self, worksheet):
        _logger.info("create links sheet")
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 4, 20)
        worksheet.write(0, 0, "Ref produit actifs")
        worksheet.write(0, 1, "Ref produits passifs")
        worksheet.write(0, 2, "Offre location")
        worksheet.write(0, 3, "Offre weekend")
        worksheet.write(0, 4, "Offre vente")
        for wizard in self:
            row = 1
            links = {}
            links["000"] = {}
            links["001"] = {}
            links["010"] = {}
            links["011"] = {}
            links["100"] = {}
            links["101"] = {}
            links["110"] = {}
            links["111"] = {}
            # link structure 
            # - row
            # - set actives
            # - 1 passive
            for product in wizard.product_ids:
                for link in product.product_master_ids:
                    if link.product_master_id.default_code and link.product_linked_id.default_code:
                        hash_link = self.link_to_hash(link)
                        if not link.product_linked_id.id in links[hash_link]:
                            links[hash_link][link.product_linked_id.id] = {
                                "actives": {link.product_master_id.default_code},
                                "passive": link.product_linked_id.default_code,
                                "row": row
                            }
                            row +=1
                        else:
                            links[hash_link][link.product_linked_id.id]["actives"].add(link.product_master_id.default_code)
            
            # stringify actives & passive
            for hash_link in links:
                for link in links[hash_link].values():
                    actives = ";".join(link["actives"])
                    worksheet.write(link["row"], 0, actives)
                    worksheet.write(link["row"], 1, link["passive"])
                    worksheet.write(link["row"], 2, self.is_hash_on_classic(hash_link))
                    worksheet.write(link["row"], 3, self.is_hash_on_weeekend(hash_link))
                    worksheet.write(link["row"], 4, self.is_hash_on_sale(hash_link))
