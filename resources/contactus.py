from flask_restful import Resource
from flask import render_template, make_response

class ContactUs(Resource):

    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('contactus.html'),200,headers)

