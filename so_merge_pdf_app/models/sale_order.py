# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
	_inherit = 'sale.order'


	so_merge_report = fields.Boolean(string="Report To Merge" , compute='_compute_so_merge_report' , store=True)
	so_merge_report_attachment = fields.Boolean(string="Afficher la pub SixUnits ?"  , store=True, default=True)
	attachment_ids = fields.Many2many('ir.attachment', string='Merge Attachments' )

	
	@api.depends('company_id.so_merge_report_with_attachments')
	def _compute_so_merge_report(self):
		for order in self:
			order.so_merge_report = order.company_id.so_merge_report_with_attachments