from odoo import models, fields, api, _

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_create_student(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window',
                'name': _('Student Profile'),
                'res_model': 'add.student.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_lead_id': self.id}, }

    def action_get_student_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Student',
            'view_mode': 'tree,form',
            'res_model': 'student.student',
            'domain': [('lead_id', '=', self.id)],
            'context': "{'create': False}"
        }

    student_count = fields.Integer(string="Student",
                                   compute='compute_student_count',
                                   default=0)
    student_profile_created = fields.Boolean(string="Student Profile Created")
    is_won_stage = fields.Boolean(string="Is Won Stage", default=False)

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id:
            print('stage')
            if self.stage_id.is_won:
                self.is_won_stage = True
            else:
                self.is_won_stage = False

    def compute_student_count(self):
        for record in self:
            record.student_count = self.env['student.student'].search_count(
                [('lead_id', '=', self.id)])

class StudentCreationWizard(models.TransientModel):
   """This model is used for sending WhatsApp messages through Odoo."""
   _name = 'add.student.wizard'
   _description = "Student Creation Wizard"

   lead_id = fields.Many2one('crm.lead', string="Lead")
   first_name = fields.Char(string="First Name", required=1)
   last_name = fields.Char(string="Last Name", required=1)
   name = fields.Char(string="Name")
   mobile = fields.Char(required=True)
   email = fields.Char(required=True)
   branch_id = fields.Many2one('student.branch', string='Branch', required=True)
   course_id = fields.Many2one('product.product', required=1)
   payment_plan = fields.Selection([
        ('full', 'Full Payment'),
        ('installment', 'Installment')
    ], string='Payment Scheme', required=True, default='full')

   @api.onchange('lead_id')
   def _onchange_lead_id(self):
       if self.lead_id:
           self.mobile = self.lead_id.mobile
           self.email = self.lead_id.email_from


   @api.onchange('first_name', 'last_name')
   def _onchange_name(self):
       self.name = str(self.first_name) + " " + str(self.last_name)

   def action_create_student(self):
       for i in self:
           self.env['student.student'].sudo().create({
               'first_name': i.first_name,
               'last_name': i.last_name,
               'name': i.name,
               'payment_scheme': i.payment_plan,
               'mobile': i.mobile,
               'email': i.email,
               'course_id': i.course_id.id,
               'lead_id': i.lead_id.id,
               'branch': i.branch_id.id,
           })
           i.lead_id.student_profile_created = True
