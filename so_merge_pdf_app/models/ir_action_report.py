# -*- coding: utf-8 -*-

from PyPDF2 import utils
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import base64
import io
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas


class IrActionsReport(models.Model):
	_inherit = 'ir.actions.report'


	def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
		res = super(IrActionsReport, self)._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
		result = res[0]
		report_sudo = self.sudo()._get_report(report_ref)
		if report_sudo.model == 'sale.order':
			streams = [io.BytesIO(res[0])]
			record_ids = self.env[report_sudo.model].browse([res_id for res_id in res_ids if res_id])
			if record_ids.so_merge_report_attachment == True:
				attachment_id = self.env.company.pub_six_units_attachment_id
				if attachment_id:
					packet = io.BytesIO()
					can = canvas.Canvas(packet)
					if attachment_id.mimetype.endswith('application/pdf'):
						try:
							merge_attachment_file = base64.b64decode(attachment_id.datas)
							merge_attachment = io.BytesIO(merge_attachment_file)
						except Exception:
							continue
						streams.append(merge_attachment)

				if len(streams) == 1:
					result = streams[0].getvalue()
				else:
					with self._merge_pdfs(streams) as pdf_merged_stream:
						result = pdf_merged_stream.getvalue()
		return [result, res[1]]
