from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class FeeDiscount(models.Model):
    _name = "fee.discount"
    _description = "Fee Discount / Waiver"
    _rec_name = "discount_amount"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    number = fields.Char(string="Discount Number", readonly=True, copy=False, default="New")
    course_id = fields.Many2one('product.product', string="Course", related='student_id.course_id')
    course_fee = fields.Float(string="Course Fee", related="course_id.lst_price")
    discount_amount = fields.Float(string="Discount Amount")
    currency_id = fields.Many2one(
        'res.currency', string="Currency",
        default=lambda self: self.env.company.currency_id.id
    )
    discount_type = fields.Selection([
        ('scholarship_exam', 'Scholarship Exam'),
        ('waiver', 'Waiver'),
        ('sibling', 'Sibling Students'),
        ('single_parent', 'Single Parents'),
        ('others', 'Others'),
    ], string="Discount Type", required=True)
    student_id = fields.Many2one('student.student', string="Student")
    request_to = fields.Many2one('res.users', string="Request To", required=1)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string="Status", default="draft")
    note = fields.Text(string="Remarks", required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('number', 'New') == 'New':
                # Find the last record
                last_record = self.search([], order="id desc", limit=1)
                if last_record and last_record.number and last_record.number.startswith("DISC"):
                    # Extract numeric part after DISC
                    last_num = int(last_record.number.replace("DISC", ""))
                    next_number = "DISC" + str(last_num + 1).zfill(4)  # DISC0001, DISC0002...
                else:
                    next_number = "DISC0001"
                vals['number'] = next_number
        return super(FeeDiscount, self).create(vals_list)

    def act_request(self):
        self.state = 'requested'
        self.student_id.discount_type = self.discount_type
        self.activity_schedule('student_management.activity_student_discount_request', user_id=self.request_to.id,
                               note=f'A new discount request has been submitted by {self.create_uid.name} '
                                    f'for student {self.student_id.name}. Please review and take action.')

    def act_return_to_draft(self):
        self.state = 'draft'

    def act_approve(self):
        if self.request_to:
            if self.request_to.id == self.env.user.id:
                self.state = 'approved'
                self.student_id.discount_fee += self.discount_amount
                self.student_id.discount_approved_by = self.env.user.id
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                        'activity_type_id', '=', self.env.ref('student_management.activity_student_discount_request').id)])
                activity_id.action_feedback(feedback='Discount Approved')
            else:
                raise UserError(
                    _("You are not authorized to approve this request. Only '%s' can approve.") % self.request_to.name)

    def act_reject(self):
        if self.request_to:
            if self.request_to.id == self.env.user.id:
                self.state = 'rejected'
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                        'activity_type_id', '=', self.env.ref('student_management.activity_student_discount_request').id)])
                activity_id.action_feedback(feedback='Discount Rejected')
            else:
                raise UserError(
                    _("You are not authorized to reject this request. Only '%s' can reject.") % self.request_to.name)
