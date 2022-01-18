from flask_restful import Resource
from flask import render_template, make_response

class PrivacyPolicy(Resource):

    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('privacy_policy.html'),200,headers)

