from odoo import fields, models
class StudentFormDetailsLink(models.TransientModel):
   _name = 'student.details.link'
   _description = "Student Details Link Wizard"

   student_id = fields.Many2one('student.student', string="Student")
   link = fields.Char(string="Link")
