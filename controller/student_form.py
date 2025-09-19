
from odoo import http
from odoo.http import request
import base64

class StudentFormController(http.Controller):

    @http.route('/student_form/<string:token>', type='http', auth='public', website=True, csrf=False)
    def student_form(self, token, **kw):
        student = request.env['student.student'].sudo().search([('form_token', '=', token)], limit=1)
        if not student:
            return request.not_found()
        return request.render('student_management.student_form_template', {'student': student})

    @http.route('/student_form/submit', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def student_form_submit(self, **post):
        print("POST DATA:", post)  # Debugging
        student = request.env['student.student'].sudo().search([('form_token', '=', post.get('token'))], limit=1)
        if student:
            photo = post.get('photo')

            vals = {

                # 'photo': base64.b64encode(photo.read()),
                'mobile': post.get('mobile'),
                'email': post.get('email'),
                'enrollment_date': post.get('enrollment_date') or False,
                'academic_year': post.get('academic_year'),
                'mode_of_study': post.get('mode_of_study'),
                # 'course_id': int(post.get('course_id')) if post.get('course_id') else False,
                # 'branch': post.get('branch'),
                'second_language': post.get('second_language'),
                'batch_no': post.get('batch_no'),
                'university': post.get('university'),
                'comm_flat_no': post.get('comm_flat_no'),
                'comm_street': post.get('comm_street'),
                'comm_post_office': post.get('comm_post_office'),
                'comm_district': post.get('comm_district'),
                'comm_state': post.get('comm_state'),
                'comm_pincode': post.get('comm_pincode'),
                # Father's Details
                'father_name': post.get('father_name'),
                'father_mail': post.get('father_mail'),
                'father_occupation': post.get('father_occupation'),
                'father_occupation_location': post.get('father_occupation_location'),
                'father_contact': post.get('father_contact'),
                # Mother's Details
                'mother_name': post.get('mother_name'),
                'mother_mail': post.get('mother_mail'),
                'mother_occupation': post.get('mother_occupation'),
                'mother_occupation_location': post.get('mother_occupation_location'),
                'mother_contact': post.get('mother_contact'),
                'state': 'confirmed'
            }
            file = request.httprequest.files.get('photo')
            if file and file.filename:
                vals['photo'] = base64.b64encode(file.read())
            sslc_file = request.httprequest.files.get('sslc_certificate')
            if sslc_file and sslc_file.filename:
                vals['sslc_certificate'] = base64.b64encode(sslc_file.read())
            student.sudo().write(vals)

            student.form_token = False  # Optional: prevent reuse
            return request.render('student_management.student_form_success')
        return request.not_found()
