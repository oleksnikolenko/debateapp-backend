from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.debatereport import DebateReportModel
from models.user import UserModel


class DebateReport(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('debate_id', type=str)

    @jwt_required
    def post(self):
        data = DebateReport.parser.parse_args()
        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        report = DebateReportModel.find_by_debate_and_user_id(data['debate_id'], user.id)

        if report:
            return {'message': 'Report already exists'}, 200
        else:
            report = DebateReportModel(data['debate_id'], user.id)
            report.save_to_db()
        return {'message': 'Report added successfully'}, 200
