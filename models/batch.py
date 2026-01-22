from odoo import models, fields, api


class StudentBatch(models.Model):
    """Model to manage student batches with course, mode, and commencement date."""
    _name = 'student.batch'
    _description = 'Student Batch'
    _order = 'commencement_date desc, name'
    _rec_name = 'display_name'

    name = fields.Char(
        string='Batch Name',
        required=True,
        help='Name of the batch'
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help='Formatted display name with mode and date'
    )
    course_id = fields.Many2one(
        'product.product',
        string='Course',
        required=True,
        help='Course associated with this batch'
    )
    mode = fields.Selection(
        [('online', 'Online'), ('offline', 'Offline')],
        string='Mode',
        required=True,
        default='offline',
        help='Delivery mode of the batch'
    )
    commencement_date = fields.Date(
        string='Commencement Date',
        required=True,
        help='Date when the batch commences'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to false to archive the batch'
    )
    student_count = fields.Integer(
        string='Students',
        compute='_compute_student_count',
        help='Number of students in this batch'
    )

    def _compute_student_count(self):
        """Compute the number of students in each batch."""
        for batch in self:
            batch.student_count = self.env['crm.lead'].search_count(
                [('batch_id', '=', batch.id)]
            )

    @api.depends('name', 'mode', 'commencement_date')
    def _compute_display_name(self):
        """Compute formatted display name with mode and date in brackets."""
        for batch in self:
            mode_label = ''
            date_str = ''
            
            if batch.mode:
                mode_label = dict(self._fields['mode'].selection).get(batch.mode, '')
            
            if batch.commencement_date:
                try:
                    date_str = batch.commencement_date.strftime('%d-%b-%y')
                except:
                    date_str = ''
            
            # Format: "[Mode | Date] Batch Name"
            prefix_parts = []
            if mode_label:
                prefix_parts.append(mode_label)
            if date_str:
                prefix_parts.append(date_str)
            
            if prefix_parts:
                batch.display_name = f"[{' | '.join(prefix_parts)}] {batch.name}"
            else:
                batch.display_name = batch.name or 'Unnamed Batch'

    def action_view_students(self):
        """Open a view showing all leads/students associated with this batch."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Leads - {self.name}',
            'res_model': 'crm.lead',
            'view_mode': 'tree,form',
            'domain': [('batch_id', '=', self.id)],
            'context': {'default_batch_id': self.id},
        }

    @api.onchange('course_id', 'mode', 'commencement_date')
    def _onchange_batch_details(self):
        """Auto-suggest batch name based on course, mode, and date."""
        if self.course_id and self.mode and self.commencement_date:
            mode_label = dict(self._fields['mode'].selection).get(self.mode, '')
            date_str = self.commencement_date.strftime('%b-%Y')
            suggested_name = f"{self.course_id.name} - {mode_label} - {date_str}"
            if not self.name or self.name == '':
                self.name = suggested_name

    def name_get(self):
        """Customize batch display to include mode and date for better clarity in dropdowns."""
        result = []
        for batch in self:
            # Get mode and date if they exist
            mode_label = ''
            date_str = ''
            
            if batch.mode:
                mode_label = dict(self._fields['mode'].selection).get(batch.mode, '')
            
            if batch.commencement_date:
                try:
                    date_str = batch.commencement_date.strftime('%d-%b-%y')
                except:
                    date_str = ''
            
            # Format: "[Mode | Date] Batch Name" - similar to course code display
            prefix_parts = []
            if mode_label:
                prefix_parts.append(mode_label)
            if date_str:
                prefix_parts.append(date_str)
            
            if prefix_parts:
                display_name = f"[{' | '.join(prefix_parts)}] {batch.name}"
            else:
                display_name = batch.name or 'Unnamed Batch'
            
            result.append((batch.id, display_name))
        return result

    _sql_constraints = [
        ('unique_batch', 
         'UNIQUE(course_id, mode, commencement_date)',
         'A batch with this course, mode, and commencement date already exists!')
    ]
