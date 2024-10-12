# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	sale_merge_report = fields.Boolean(string="Sale Order Merge Reports PDF" , related="company_id.sale_merge_report" , readonly=False)
	so_report_template_ids = fields.Many2many('ir.actions.report' , domain=[('model','=','sale.order')] ,
						 related="company_id.so_report_template_ids" , readonly=False , required=True)
	so_merge_report_with_attachments = fields.Boolean(string="Sale Order Merge Reports PDF with attachments" , 
							related="company_id.so_merge_report_with_attachments" , readonly=False)



class ResCompany(models.Model):
	_inherit = 'res.company'

	sale_merge_report = fields.Boolean(string="Sale Order Merge Reports PDF")
	so_report_template_ids = fields.Many2many('ir.actions.report', 'so_merge_report_ids' , domain=[('model','=','sale.order')])
	so_merge_report_with_attachments = fields.Boolean(string="Sale Order Merge Reports PDF with attachments")
