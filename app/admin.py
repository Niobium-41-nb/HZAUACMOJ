from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app.extensions import admin, db
from app.models import User, Role, Problem, ProblemTag, ProblemTestcase, Submission, Contest, ContestProblem, ContestParticipant, Blog, BlogTag, BlogComment, BlogLike, Resource, ResourceTag, ResourceComment, ResourceLike


class AdminModelView(ModelView):
    """Base model view for admin panel with authentication"""
    
    def is_accessible(self):
        """Check if user is authenticated and has admin access"""
        return current_user.is_authenticated and current_user.is_admin()


class UserAdmin(AdminModelView):
    """Admin view for users"""
    column_list = ['id', 'username', 'email', 'role', 'real_name', 'student_id', 'is_active', 'created_at', 'last_login']
    column_searchable_list = ['username', 'email', 'real_name', 'student_id']
    column_filters = ['role', 'is_active', 'created_at']
    form_columns = ['username', 'email', 'password_hash', 'role', 'real_name', 'student_id', 'school', 'college', 'bio', 'github', 'avatar', 'is_active']
    form_args = {
        'password_hash': {
            'label': 'Password',
            'description': 'Leave blank if you don\'t want to change the password',
        }
    }
    endpoint = 'admin_user'


class RoleAdmin(AdminModelView):
    """Admin view for roles"""
    column_list = ['id', 'name', 'description']
    column_searchable_list = ['name']
    endpoint = 'admin_role'
    name = 'role_admin'


class ProblemAdmin(AdminModelView):
    """Admin view for problems"""
    column_list = ['id', 'title', 'total_submissions', 'accepted_submissions', 'time_limit', 'memory_limit', 'is_public', 'created_at']
    column_searchable_list = ['title', 'description']
    column_filters = ['is_public', 'created_at', 'tags']
    form_columns = ['title', 'description', 'input_description', 'output_description', 'sample_input', 'sample_output', 'hint', 'source', 'time_limit', 'memory_limit', 'is_public', 'tags']
    endpoint = 'admin_problem'
    name = 'problem_admin'


class ProblemTagAdmin(AdminModelView):
    """Admin view for problem tags"""
    column_list = ['id', 'name', 'description']
    column_searchable_list = ['name']
    endpoint = 'admin_problem_tag'
    name = 'problem_tag_admin'


class SubmissionAdmin(AdminModelView):
    """Admin view for submissions"""
    column_list = ['id', 'problem', 'user', 'language', 'status', 'execution_time', 'memory_used', 'created_at']
    column_searchable_list = ['problem.title', 'user.username']
    column_filters = ['status', 'language', 'created_at']
    endpoint = 'admin_submission'
    name = 'submission_admin'


class ContestAdmin(AdminModelView):
    """Admin view for contests"""
    column_list = ['id', 'title', 'start_time', 'end_time', 'is_public', 'created_at']
    column_searchable_list = ['title', 'description']
    column_filters = ['is_public', 'created_at']
    form_columns = ['title', 'description', 'start_time', 'end_time', 'is_public', 'problems']
    endpoint = 'admin_contest'
    name = 'contest_admin'


class BlogAdmin(AdminModelView):
    """Admin view for blogs"""
    column_list = ['id', 'title', 'user', 'views', 'likes_count', 'is_published', 'created_at']
    column_searchable_list = ['title', 'content']
    column_filters = ['is_published', 'created_at', 'tags']
    form_columns = ['title', 'content', 'summary', 'is_published', 'tags']
    endpoint = 'admin_blog'
    name = 'blog_admin'


class ResourceAdmin(AdminModelView):
    """Admin view for resources"""
    column_list = ['id', 'title', 'user', 'views', 'likes_count', 'is_public', 'created_at']
    column_searchable_list = ['title', 'content']
    column_filters = ['is_public', 'created_at', 'tags']
    form_columns = ['title', 'content', 'file_path', 'is_public', 'tags']
    endpoint = 'admin_resource'
    name = 'resource_admin'


def init_admin(app):
    """Initialize admin panel"""
    # Register models
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(RoleAdmin(Role, db.session))
    admin.add_view(ProblemAdmin(Problem, db.session))
    admin.add_view(ProblemTagAdmin(ProblemTag, db.session))
    admin.add_view(SubmissionAdmin(Submission, db.session))
    admin.add_view(ContestAdmin(Contest, db.session))
    admin.add_view(BlogAdmin(Blog, db.session))
    admin.add_view(ResourceAdmin(Resource, db.session))
