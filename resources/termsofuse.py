from flask_restful import Resource
from flask import render_template, make_response

class TermsOfUse(Resource):

    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('terms_of_use.html'),200,headers)

