from odoo import models, fields, api

class SemesterFeeDetails(models.Model):
    _name = 'semester.fee.details'
    _description = 'Semester Fee Details'

    name = fields.Char(string="Name", required=True)
    student_id = fields.Many2one('student.student', string="Student", ondelete="cascade")
    semester = fields.Char(string="Semester")
    fee_amount = fields.Float(string="Fee Amount", required=True)
    paid_amount = fields.Float(string="Paid Amount", compute='_compute_allocate_paid_amount', store=True)
    balance_amount = fields.Float(string="Balance Amount", compute="_compute_balance", store=True)

    due_date = fields.Date(string="Due Date")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('overdue', 'Overdue'),
    ], string="Status", default='draft')

    # Compute balance
    def _compute_balance(self):
        for rec in self:
            rec.balance_amount = rec.fee_amount - rec.paid_amount

    @api.depends('student_id.paid_amount')
    def _compute_allocate_paid_amount(self):
        for student in self:
            if student.student_id.course_type == 'degree':
                remaining_payment = student.student_id.paid_amount

                for sem in student.student_id.semester_records_ids:
                    if remaining_payment <= 0:
                        break

                    # full or partial payment for this semester
                    if remaining_payment >= sem.fee_amount:
                        sem.paid_amount = sem.fee_amount
                        sem.balance_amount = 0.0
                        sem.status = 'paid'  # assuming selection: draft/paid/partial
                        remaining_payment -= sem.fee_amount
                    else:
                        sem.paid_amount = remaining_payment
                        sem.balance_amount = sem.fee_amount - remaining_payment
                        sem.status = 'partial'
                        remaining_payment = 0
