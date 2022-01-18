from flask_restful import Resource,reqparse
from models.category import CategoryModel
from flask_jwt_extended import jwt_required


class Category(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('category_name', type=str, required=True, help="Name is missing")

    @jwt_required
    def post(self, localization):
        data = Category.parser.parse_args()

        category = CategoryModel(data['category_name'], localization)

        try:
            category.save_to_db()
        except AssertionError as error:
            return {'error': error}, 500

        return category.json()


class CategoryList(Resource):

    def get(self, localization):
        return {'categories': [category.json() for category in CategoryModel.filter_by_localization(localization)]}


class CategorySearch(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('search_context', type=str, required=True, help='search context is required')

    def get(self, localization):
        data = CategorySearch.parser.parse_args()

        categories = CategoryModel.filter_by_context_and_localization(data['search_context'], localization)

        if categories:
            return {'categories': [category.json() for category in categories]}
        else:
            return {'categories': []}
