from email.policy import default
import uuid
from odoo import models, fields, api, _


class Student(models.Model):
    _name = 'student.student'
    _description = 'Student Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    photo = fields.Image(string='Student Photo', max_width=1024, max_height=1024)
    name = fields.Char(string='Student Name', required=True)
    first_name = fields.Char('First Name', )
    last_name = fields.Char('Last Name', )
    mobile = fields.Char(string='Phone No.', widget='phone', required=True)
    email = fields.Char(string='Email Id', required=True)
    enrollment_date = fields.Date(string='Date of Enrollment', default=fields.Date.today())
    academic_year = fields.Char(string='Academic Year')
    mode_of_study = fields.Selection([
        ('regular', 'Regular'),
        ('distance', 'Distance')
    ], string='Mode of Study')
    course_id = fields.Many2one('product.product', string='Course Applied For',
                                domain=[('type', '=', 'service')], required=True)
    branch = fields.Char(string='Branch')
    second_language = fields.Char(string='Second Language')
    batch_no = fields.Char(string='Batch No')
    university = fields.Char(string='University')

    # Communication Address
    comm_flat_no = fields.Char(string='Flat/House No.')
    comm_street = fields.Char(string='Street Name')
    comm_post_office = fields.Char(string='Post Office')
    comm_district = fields.Char(string='District')
    comm_state = fields.Char(string='State')
    comm_pincode = fields.Char(string='Pin Code')

    # Permanent Address
    same_as_community = fields.Boolean(string='Same As Community')
    perm_flat_no = fields.Char(string='Permanent Flat/House No.')
    perm_street = fields.Char(string='Permanent Street Name')
    perm_post_office = fields.Char(string='Permanent Post Office')
    perm_district = fields.Char(string='Permanent District')
    perm_state = fields.Char(string='Permanent State')
    perm_pincode = fields.Char(string='Permanent Pin Code')

    # Contact Details
    phone = fields.Char(string='Phone No.')
    whatsapp = fields.Char(string='Whatsapp No.')
    # Academic Records
    academic_records_ids = fields.One2many('student.academic.record', 'student_id', string='Academic Records')

    # Parent Details
    father_name = fields.Char(string="Father's Name")
    father_age = fields.Integer(string="Father's Age")
    father_occupation = fields.Char(string="Father's Occupation")
    father_occupation_location = fields.Char(string="Father Occupation Location")
    father_contact = fields.Char(string="Father's Contact No.")
    mother_name = fields.Char(string="Mother's Name")
    mother_age = fields.Integer(string="Mother's Age")
    mother_occupation = fields.Char(string="Mother's Occupation")
    mother_occupation_location = fields.Char(string="Mother Occupation Location")
    mother_contact = fields.Char(string="Mother's Contact No.")

    # Additional Details
    admission_no = fields.Char(string='Admission No.', default=lambda self: self.env[
        'ir.sequence'].next_by_code('student.student'))
    university_enrollment_no = fields.Char(string='University Enrollment No.')
    student_email = fields.Char(string='Student Email')

    # Fee Management Fields
    course_fee = fields.Float(related='course_id.list_price', string='Total Fee', store=True)
    discount_fee = fields.Float(string='Discount Fee')
    paid_amount = fields.Float(string='Paid Amount', compute='_compute_paid_amount', store=True)
    pending_amount = fields.Float(string='Pending Amount', compute='_compute_pending_amount', store=True)
    fee_payment_ids = fields.One2many('student.fee.payment', 'student_id', string='Fee Payments')
    total_fee = fields.Float(string='Total Fee', compute='_compute_total_fee', store=True)
    payment_scheme = fields.Selection([
        ('full', 'Full Payment'),
        ('installment', 'Installment')
    ], string='Payment Scheme', required=True, default='full')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], string='Status', default='draft', track_visibility=True)
    installment_count = fields.Integer(string='Number of Installments', default=1)
    next_payment_date = fields.Date(string='Next Payment Date')
    lead_id = fields.Many2one('crm.lead', string='Lead')

    @api.model_create_multi
    def create(self, vals_list):
        """Create a sequence for the student model and update lead"""
        for vals in vals_list:
            if vals.get('admission_no', _('New')) == _('New'):
                vals['admission_no'] = self.env['ir.sequence'].next_by_code('student.student')

        students = super().create(vals_list)

        for student in students:
            if student.lead_id:
                student.lead_id.student_profile_created = True

        return students

    @api.onchange(
        'comm_flat_no', 'comm_street', 'comm_post_office',
        'comm_district', 'comm_state', 'comm_pincode', 'same_as_community'
    )
    def _onchange_communication_address(self):
        """Auto-fill permanent address with communication address"""
        self.perm_flat_no = self.comm_flat_no
        self.perm_street = self.comm_street
        self.perm_post_office = self.comm_post_office
        self.perm_district = self.comm_district
        self.perm_state = self.comm_state
        self.perm_pincode = self.comm_pincode

    @api.depends('course_fee', 'discount_fee')
    def _compute_total_fee(self):
        for rec in self:
            rec.total_fee = rec.course_fee - rec.discount_fee if rec.course_fee else 0.0

    @api.onchange('first_name', 'last_name')
    def _onchange_name(self):
        self.name = str(self.first_name) + " " + str(self.last_name)

    def act_give_names(self):
        students = self.env['student.student'].search([])

        for student in students:
            name = (student.name or '').strip()
            if ' ' in name:
                first, last = name.split(' ', 1)
            else:
                first = name
                last = ''
            student.first_name = first
            student.last_name = last

    @api.depends('fee_payment_ids.amount')
    def _compute_paid_amount(self):
        for student in self:
            student.paid_amount = sum(student.fee_payment_ids.mapped('amount'))

    @api.depends('total_fee', 'paid_amount')
    def _compute_pending_amount(self):
        for student in self:
            student.pending_amount = student.total_fee - student.paid_amount

    def act_send_welcome_email(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Welcome Mail'),
                'res_model': 'student.welcome.mail',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_student_id': self.id}, }

    def act_confirm(self):
        for i in self:
            i.state = 'confirmed'
    form_token = fields.Char(string="Form Token", readonly=True)
    def action_generate_form_link(self):
        for rec in self:
            # Generate a unique token
            rec.form_token = str(uuid.uuid4())

            # Build URL
            link = f"/student_form/{rec.form_token}"
            full_url = rec.get_base_url() + link
            if rec.email:
                mail_values = {
                    'subject': _('Your Details Form Link'),
                    'body_html': f"""
                                    <p>Dear {rec.name},</p>
                                    <p>Please fill in your student form by clicking the link below:</p>
                                    <p><a href="{full_url}" target="_blank">{full_url}</a></p>
                                    <p>Thank you!</p>
                                """,
                    'email_to': rec.email,
                    'author_id': self.env.user.id,
                }
                self.env['mail.mail'].create(mail_values).send()

            print(full_url, 'full url')
            return {'type': 'ir.actions.act_window',
                    'name': _('Student Details Link'),
                    'res_model': 'student.details.link',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {'default_student_id': self.id, 'default_link': full_url}, }



class StudentAcademicRecord(models.Model):
    _name = 'student.academic.record'
    _description = 'Student Academic Record'

    student_id = fields.Many2one('student.student', string='Student')
    exam_passed = fields.Char(string='Qualifying Exam Passed')
    institution = fields.Char(string='Institution')
    year = fields.Integer(string='Year')
    percentage = fields.Float(string='Percentage')


class StudentFeePayment(models.Model):
    _name = 'student.fee.payment'
    _description = 'Student Fee Payment'
    _order = 'payment_date desc'

    student_id = fields.Many2one('student.student', string='Student', required=True)
    payment_date = fields.Date(string='Payment Date', required=True, default=fields.Date.context_today)
    amount = fields.Float(string='Amount', required=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI')
    ], string='Payment Method', required=True)
    reference = fields.Char(string='Reference Number')
    installment_number = fields.Integer(string='Installment Number')
    notes = fields.Text(string='Notes')
