from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_create_student(self):
        self.ensure_one()
        return {
            'name': 'Create Student',
            'type': 'ir.actions.act_window',
            'res_model': 'student.student',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': self.contact_name or self.partner_id.name,
                'default_phone': self.phone or self.partner_id.phone,
                'default_email': self.email_from or self.partner_id.email,
            }
        }
