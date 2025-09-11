from odoo import fields, models, api, _

class ProductInheritance(models.Model):
    _inherit = "product.product"

    is_it_required_university = fields.Boolean(string='University Required ')
    is_it_required_second_language = fields.Boolean(string='Second Language Required')