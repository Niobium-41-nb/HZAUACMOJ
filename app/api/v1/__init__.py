from flask import Blueprint
from flask_restx import Api
from .auth import api as auth_ns
from .users import api as users_ns
from .problems import api as problems_ns
from .submissions import api as submissions_ns
from .contests import api as contests_ns
from .blogs import api as blogs_ns
from .resources import api as resources_ns


api_bp = Blueprint('api_v1', __name__)
api = Api(
    api_bp,
    version='1.0',
    title='HZAUACMOJ API',
    description='HZAUACMOJ RESTful API',
    doc='/api/v1/docs'
)

# Register namespaces
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(users_ns, path='/users')
api.add_namespace(problems_ns, path='/problems')
api.add_namespace(submissions_ns, path='/submissions')
api.add_namespace(contests_ns, path='/contests')
api.add_namespace(blogs_ns, path='/blogs')
api.add_namespace(resources_ns, path='/resources')