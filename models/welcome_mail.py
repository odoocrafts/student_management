from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StudentWelcomeMail(models.TransientModel):
    _name = 'student.welcome.mail'
    _description = "Welcome Mail Wizard"

    student_id = fields.Many2one('student.student', string="Student")
    email = fields.Char(related='student_id.email', required=True, string="Email")
    mail_type = fields.Selection([('welcome_mail', 'Welcome Email'), ('reminder_mail', 'Reminder Email')],
                                 string="Mail Type", default='welcome_mail', required=1)
    start_date = fields.Datetime(string="Start Date", )
    payment_date = fields.Datetime(string="Payment Date",)
    amount = fields.Float(string="Amount",)
    course_id = fields.Many2one('product.product', string="Course", related='student_id.course_id')
    campus_location = fields.Char(string="Campus Location")
    student_id_code = fields.Char(string="Student ID",)
    message = fields.Text(string="message",)

    @api.onchange('student_id', 'amount', 'payment_date', 'course_id', 'start_date', 'campus_location',
                  'student_id_code')
    def _onchange_generate_message(self):
        """Auto-generate the welcome message whenever fields change."""
        student_name = self.student_id.name or ""
        amount = self.amount or 0
        payment_date = self.payment_date.strftime('%d-%m-%Y') if self.payment_date else ""
        course_name = self.course_id.name or ""
        start_date = self.start_date.strftime('%d-%m-%Y') if self.start_date else ""
        campus_location = self.campus_location or ""
        student_id_code = self.student_id_code or ""

        self.message = f"""
           Dear {student_name}

           Welcome to the vibrant community of creators at Cindrebay School of Design! We’re thrilled to have you join us and begin your journey into the world of design.

           This email is to confirm that your admission has been successfully completed. We have received your admission fee of ₹{amount} on {payment_date}. Thank you!

           📌 Here are a few important details to get you started:
           
               Course enrolled: {course_name}
               Batch start date: {start_date}
               Campus: {campus_location}
               Student ID: {student_id_code}
           

           You will receive your login credentials for the Cindrebay student portal shortly via a separate email. Please ensure your contact details are up to date.

           Should you have any questions or need help settling in, feel free to contact the administrative team.

           We look forward to seeing you thrive and explore your creative potential with us! 🌈

           Warm regards,
           Admissions Office
           Cindrebay School of Design
           """

    def action_send_mail(self):
        for wizard in self:
            student = wizard.student_id
            if not self.email:
                raise UserError("The student does not have an email address.")

            # Collect details
            student_name = student.name or ""
            amount = self.amount or 0
            payment_date = self.payment_date or ""
            course_name = self.course_id.name or ""
            start_date = self.start_date
            campus_location = self.campus_location or ""
            student_id_code = self.student_id_code or ""

            # Create email body
            email_body = f"""
           <p>Dear {student_name},</p>

           <p>Welcome to the vibrant community of creators at <b>Cindrebay School of Design</b>! We’re thrilled to have you join us and begin your journey into the world of design.</p>

           <p>This email is to confirm that your admission has been successfully completed. We have received your <b>admission fee of ₹{amount}</b> on <b>{payment_date}</b>. Thank you!</p>

           <p>📌 Here are a few important details to get you started:</p>
           <ul>
               <li><b>Course enrolled</b>: {course_name}</li>
               <li><b>Batch start date</b>: {start_date}</li>
               <li><b>Campus</b>: {campus_location}</li>
               <li><b>Student ID</b>: {student_id_code}</li>
           </ul>

           <p>You will receive your login credentials for the Cindrebay student portal shortly via a separate email. Please ensure your contact details are up to date.</p>

           <p>Should you have any questions or need help settling in, feel free to contact the administrative team.</p>

           <p>We look forward to seeing you thrive and explore your creative potential with us! 🌈</p>

           <p>Warm regards,<br/>
           <b>Admissions Office</b><br/>
           Cindrebay School of Design</p>
           """

            # Send mail
            self.env['mail.mail'].create({
                'subject': 'Welcome to Cindrebay School of Design',
                'body_html': email_body,
                'email_to': student.email,
            }).send()

    due_amount = fields.Float(string="Due Amount")
    due_date = fields.Date(string="Due Date")
    accounts_email = fields.Char(string="Accounts Email")
    phone_number = fields.Char(string="Phone Number")
    remainder_mail = fields.Text(string="Reminder Mail", sanitize=False)

    @api.onchange('student_id', 'due_amount', 'due_date', 'accounts_email', 'phone_number')
    def _onchange_generate_remainder_mail(self):
        """Generate the fee reminder email message dynamically."""
        student_name = self.student_id.name or ""
        amount = self.due_amount or 0
        due_date = self.due_date.strftime('%d-%m-%Y') if self.due_date else ""
        accounts_email = self.accounts_email or ""
        phone_number = self.phone_number or ""

        self.remainder_mail = f"""
        Dear {student_name},

        We hope you are enjoying your learning journey with Cindrebay School of Design

        This is a gentle reminder that your upcoming fee installment is due as per your payment schedule:

        ✅ Due Amount: ₹{amount}
        📆 Due Date: {due_date}

        Kindly make the payment by the due date to avoid any late fees or interruptions in your classes.

        You can make the payment via the Cindrebay student portal or visit the Accounts Office at your campus.

        👉 For any queries regarding fees or payment options, feel free to contact us at {accounts_email} or call {phone_number}.
        Thank you for your cooperation!

        Best regards,
        Accounts Department
        Cindrebay School of Design
        """

    def action_send_remainder_mail(self):
        for wizard in self:
            student = wizard.student_id
            if not self.email:
                raise UserError("The student does not have an email address.")

            # Collect details
            student_name = self.student_id.name or ""
            amount = self.due_amount or 0
            due_date = self.due_date.strftime('%d-%m-%Y') if self.due_date else ""
            accounts_email = self.accounts_email or ""
            phone_number = self.phone_number or ""

            email_body = f"""
                    <p>Dear {student_name},</p>

                    <p>We hope you are enjoying your learning journey with <b>Cindrebay School of Design</b>.</p>

                    <p>This is a gentle reminder that your upcoming fee installment is due as per your payment schedule:</p>

                    <p>✅ <b>Due Amount:</b> ₹{amount}<br/>
                    📆 <b>Due Date:</b> {due_date}</p>

                    <p>Kindly make the payment by the due date to avoid any late fees or interruptions in your classes.</p>

                    <p>You can make the payment via the Cindrebay student portal or visit the Accounts Office at your campus.</p>

                    <p>👉 For any queries regarding fees or payment options, feel free to contact us at {accounts_email} or call {phone_number}.</p>

                    <p>Thank you for your cooperation!</p>

                    <p>Best regards,<br/>
                    <b>Accounts Department</b><br/>
                    Cindrebay School of Design</p>
                    """
            # Send mail
            self.env['mail.mail'].create({
                'subject': 'Reminder Mail',
                'body_html': email_body,
                'email_to': student.email,
            }).send()
