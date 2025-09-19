from email.policy import default
import uuid
from datetime import date
from odoo import models, fields, api, _


class Student(models.Model):
    _name = 'student.student'
    _description = 'Student Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    photo = fields.Binary(string='Student Photo', max_width=1024, max_height=1024)
    name = fields.Char(string='Student Name', required=True)
    first_name = fields.Char('First Name', )
    last_name = fields.Char('Last Name', )
    mobile = fields.Char(string='Phone No.', widget='phone', required=True)
    email = fields.Char(string='Email Id', required=True)
    enrollment_date = fields.Date(string='Date of Enrollment', default=fields.Date.today())
    academic_year = fields.Selection(
        selection=[
            ('2025', '2025'),
            ('2026', '2026'),
            ('2027', '2027'),
        ],
        string='Academic Year'
    )
    fee_type = fields.Selection([
        ('course_fee', 'Course Fee'),
        ('contracted_fee', 'Contracted Fee'),
        ('discount', 'Discount'),
        ('other', 'Other'),
    ], string="Fee Type", required=True, default='course_fee')
    discount_type = fields.Selection([
        ('scholarship_exam', 'Scholarship Exam'),
        ('waiver', 'Waiver'),
        ('sibling', 'Sibling Students'),
        ('single_parent', 'Single Parents'),
        ('others', 'Others'),
    ], string="Discount Type")
    mode_of_study = fields.Selection([
        ('regular', 'Regular'),
        ('distance', 'Distance')
    ], string='Mode of Study')
    sslc_certificate = fields.Binary(string='SSLC Certificate')
    course_id = fields.Many2one('product.product', string='Course Applied For',
                                domain=[('type', '=', 'service')], required=True)
    course_code = fields.Char(string='Course Code', related='course_id.course_code')
    branch = fields.Many2one('student.branch', string='Branch', domain=[('active', '=', 1)], required=True)
    branch_code = fields.Char(string='Branch Code', related='branch.code')
    second_language = fields.Char(string='Second Language')
    batch_no = fields.Char(string='Batch No')
    university = fields.Char(string='University')
    is_it_required_university = fields.Boolean(string='University Required',
                                               related='course_id.is_it_required_university')
    is_it_required_second_language = fields.Boolean(string='Second Language Required',
                                                    related='course_id.is_it_required_second_language')

    # Communication Address
    comm_flat_no = fields.Char(string='Flat/House No.')
    comm_street = fields.Char(string='Street Name')
    comm_post_office = fields.Char(string='Post Office')
    comm_district = fields.Char(string='District')
    comm_state = fields.Char(string='State')
    comm_pincode = fields.Char(string='Pin Code')

    # Permanent Address
    same_as_community = fields.Boolean(string='Same As Communication Address')
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
    father_mail = fields.Char(string="Father's Mail")
    father_age = fields.Integer(string="Father's Age")
    father_occupation = fields.Char(string="Father's Occupation")
    father_occupation_location = fields.Char(string="Father Occupation Location")
    father_contact = fields.Char(string="Father's Contact No.")
    mother_name = fields.Char(string="Mother's Name")
    mother_mail = fields.Char(string="Mother's Mail")
    mother_age = fields.Integer(string="Mother's Age")
    mother_occupation = fields.Char(string="Mother's Occupation")
    mother_occupation_location = fields.Char(string="Mother Occupation Location")
    mother_contact = fields.Char(string="Mother's Contact No.")

    # Additional Details
    admission_no = fields.Char(string="Admission No", readonly=True, copy=False)

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
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], string='Status', default='draft',
                             track_visibility=True)
    installment_count = fields.Integer(string='Number of Installments', default=1)
    next_payment_date = fields.Date(string='Next Payment Date')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    course_type = fields.Selection(
        [
            ("degree", "Degree"),
            ("diploma", "Diploma"),
            ("certificate", "Certificate"),

        ],
        string="Course Type", related='course_id.course_type',
    )
    semester_records_ids = fields.One2many('semester.fee.details', 'student_id', string='Semester Details',
                                           compute='_compute_generate_semester_fees', store=1)
    semester_count = fields.Integer(string='Semester Count', related='course_id.semester_count', )

    @api.depends('course_id', 'total_fee', 'semester_count')
    def _compute_generate_semester_fees(self):

        for student in self:
            student.semester_records_ids = [(5, 0, 0)]
            if student.semester_count and student.total_fee:
                fee_per_semester = student.total_fee / student.semester_count
                semester_lines = []

                for i in range(1, student.semester_count + 1):
                    semester_lines.append((0, 0, {
                        'name': f"Semester {i}",
                        'semester': str(i),  # match selection or char field
                        'fee_amount': fee_per_semester,
                        'balance_amount': fee_per_semester,
                    }))

                student.semester_records_ids = semester_lines
            else:
                student.semester_records_ids = [(5, 0, 0)]

    @api.model_create_multi
    def create(self, vals_list):
        current_year = str(date.today().year)[-2:]  # e.g. "25" for 2025

        for vals in vals_list:
            if not vals.get("admission_no"):
                # Check branch & course codes (must be available)
                branch_code = ""
                course_code = ""

                if vals.get("branch"):
                    branch = self.env["student.branch"].browse(vals["branch"])
                    branch_code = branch.code or ""

                if vals.get("course_id"):
                    course = self.env["product.product"].browse(vals["course_id"])
                    course_code = course.course_code or ""

                # Get last admission number for same year
                last_student = self.search(
                    [("admission_no", "like", f"/{current_year}")],
                    order="id desc",
                    limit=1
                )

                if last_student and last_student.admission_no:
                    try:
                        last_count = int(last_student.admission_no.split("/")[0])
                    except Exception:
                        last_count = 0
                else:
                    last_count = 0

                new_count = str(last_count + 1).zfill(2)  # always 2 digits
                vals["admission_no"] = f"{new_count}/{branch_code}/{course_code}/{current_year}"

        students = super(Student, self).create(vals_list)
        for student in students:
            if student.semester_count and student.total_fee:
                fee_per_semester = student.total_fee / student.semester_count
                semester_lines = []

                for i in range(1, student.semester_count + 1):
                    semester_lines.append((0, 0, {
                        'name': f"Semester {i}",
                        'semester': str(i),  # must match selection field type
                        'fee_amount': fee_per_semester,
                        'balance_amount': fee_per_semester,
                    }))

                student.write({'semester_records_ids': semester_lines})

        for student in students:
            if student.lead_id:
                student.lead_id.student_profile_created = True

        return students

    discount_requested_by = fields.Many2one('res.users', string='Discount Requested By', readonly=1)
    discount_approved_by = fields.Many2one('res.users', string='Discount Approved By', readonly=1)

    def act_discount_request(self):
        self.discount_requested_by = self.env.user.id
        return {'type': 'ir.actions.act_window',
                'name': _('Discount request'),
                'res_model': 'fee.discount',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_student_id': self.id, 'default_discount_type': self.discount_type}, }

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

    @api.depends('course_fee', 'discount_fee', 'fee_type')
    def _compute_total_fee(self):
        for rec in self:
            if rec.fee_type:
                if rec.fee_type != 'discount':
                    rec.discount_fee = 0.0
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

    discount_count = fields.Integer(string="Discount",
                                    compute='compute_discount_count',
                                    default=0)

    def compute_discount_count(self):
        for record in self:
            record.discount_count = self.env['fee.discount'].search_count(
                [('student_id', '=', self.id)])

    def action_get_discount_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Discounts',
            'view_mode': 'tree',
            'res_model': 'fee.discount',
            'domain': [('student_id', '=', self.id)],
            'context': "{'create': False}"
        }


class StudentAcademicRecord(models.Model):
    _name = 'student.academic.record'
    _description = 'Student Academic Record'

    student_id = fields.Many2one('student.student', string='Student')
    exam_passed = fields.Selection(
        [('sslc', 'SSLC'), ('plus_one', 'Plus One'), ('plus_two', 'Plus Two'), ('degree', 'Degree')],
        string='Qualifying Exam Passed')
    institution = fields.Char(string='Institution')
    year = fields.Integer(string='Year')
    location = fields.Char(string='Location')
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
