from odoo import fields, models, api, _

class ProductInheritance(models.Model):
    _inherit = "product.product"

    is_it_required_university = fields.Boolean(string='University Required ')
    is_it_required_second_language = fields.Boolean(string='Second Language Required')
    course_code = fields.Char(string='Course Code')
    branch_id = fields.Many2one('student.branch', string='Branch')
    course_type = fields.Selection(
        [
            ("degree", "Degree"),
            ("diploma", "Diploma"),
            ("certificate", "Certificate"),

        ],
        string="Course Type",
    )
    semester_count = fields.Integer(string='Semester Count')
