from odoo import models, fields

class AdmissionReportWizard(models.TransientModel):
    _inherit = 'institute.admission.report.wizard'

    branch_id = fields.Many2one('student.branch', string='Campus')
