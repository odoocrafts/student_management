from odoo import api, fields, models, tools

class Branch(models.Model):
    _name = 'student.branch'
    _description = 'Student Branch'

    name = fields.Char(string='Branch Name', required=1)
    code = fields.Char(string='Branch Code', required=1)
    manager_id = fields.Many2one('res.users', string='Manager')
    active = fields.Boolean(string="Active", default=True)
