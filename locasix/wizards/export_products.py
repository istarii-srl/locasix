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

    from_button = fields.Boolean(default=False)
    product_ids = fields.Many2many(comodel_name="product.template", default=lambda self : self._get_default_products())

    def _get_default_products(self):
        return self.env["product.template"].search([("active", "=", True)]) if self.from_button else self.env['product.template'].browse(self._context.get('active_ids'))

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

                    row +=1
    
    def create_links_sheet(self, worksheet):
        _logger.info("create links sheet")
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 1, 20)
        worksheet.write(0, 0, "Ref produit actifs")
        worksheet.write(0, 1, "Ref produits passifs")
        for wizard in self:
            row = 1
            links = {}
            # link structure 
            # - row
            # - set actives
            # - 1 passive
            for product in wizard.product_ids:
                for link in product.product_master_ids:
                    if link.product_master_id.default_code and link.product_linked_id.default_code:
                        if not link.product_linked_id.id in links:
                            links[link.product_linked_id.id] = {
                                "actives": {link.product_master_id.default_code},
                                "passive": link.product_linked_id.default_code,
                                "row": row
                            }
                            row +=1
                        else:
                            links[link.product_linked_id.id]["actives"].add(link.product_master_id.default_code)
            
            # stringify actives & passive
            for link in links.values():
                actives = ";".join(link["actives"])
                worksheet.write(link["row"], 0, actives)
                worksheet.write(link["row"], 1, link["passive"])
