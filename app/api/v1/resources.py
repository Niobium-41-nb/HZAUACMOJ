from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required, current_user
from app.extensions import db
from app.models.resource import Resource, ResourceTag, ResourceComment, ResourceLike


api = Namespace('resources', description='Resource operations')

# Model definitions
resource_tag_model = api.model('ResourceTag', {
    'id': fields.Integer(readonly=True, description='Tag ID'),
    'name': fields.String(required=True, description='Tag name'),
    'description': fields.String(description='Tag description')
})

resource_model = api.model('Resource', {
    'id': fields.Integer(readonly=True, description='Resource ID'),
    'title': fields.String(required=True, description='Resource title'),
    'content': fields.String(required=True, description='Resource content'),
    'file_path': fields.String(description='File path'),
    'user_id': fields.Integer(description='Uploader ID'),
    'views': fields.Integer(readonly=True, description='View count'),
    'likes_count': fields.Integer(readonly=True, description='Like count'),
    'comments_count': fields.Integer(readonly=True, description='Comment count'),
    'is_public': fields.Boolean(description='Is public'),
    'created_at': fields.DateTime(readonly=True, description='Created at'),
    'updated_at': fields.DateTime(readonly=True, description='Updated at'),
    'tags': fields.List(fields.Nested(resource_tag_model), description='Resource tags')
})

resource_comment_model = api.model('ResourceComment', {
    'id': fields.Integer(readonly=True, description='Comment ID'),
    'content': fields.String(required=True, description='Comment content'),
    'user_id': fields.Integer(description='User ID'),
    'resource_id': fields.Integer(description='Resource ID'),
    'created_at': fields.DateTime(readonly=True, description='Created at')
})

@api.route('/')
class ResourceList(Resource):
    """Resource list resource"""
    
    @api.marshal_list_with(resource_model)
    def get(self):
        """Get all public resources"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        resources = Resource.query.filter_by(is_public=True).order_by(Resource.created_at.desc()).paginate(page=page, per_page=per_page)
        return resources.items, 200
    
    @login_required
    @api.expect(resource_model)
    @api.marshal_with(resource_model)
    def post(self):
        """Create a new resource"""
        data = request.get_json()
        
        new_resource = Resource(
            title=data['title'],
            content=data['content'],
            file_path=data.get('file_path'),
            user_id=current_user.id,
            is_public=data.get('is_public', False)
        )
        
        # Add tags if provided
        if 'tags' in data:
            for tag_data in data['tags']:
                tag = ResourceTag.query.filter_by(name=tag_data['name']).first()
                if tag:
                    new_resource.tags.append(tag)
        
        db.session.add(new_resource)
        db.session.commit()
        
        return new_resource, 201


@api.route('/<int:resource_id>')
class ResourceDetail(Resource):
    """Resource detail resource"""
    
    @api.marshal_with(resource_model)
    def get(self, resource_id):
        """Get a resource by ID"""
        resource = Resource.query.get_or_404(resource_id)
        
        # Check if resource is public or user is admin
        if not resource.is_public and (not current_user.is_authenticated or not current_user.is_admin()):
            api.abort(403, 'Permission denied')
        
        # Increment view count
        resource.views += 1
        db.session.commit()
        
        return resource, 200
    
    @login_required
    @api.expect(resource_model)
    @api.marshal_with(resource_model)
    def put(self, resource_id):
        """Update a resource"""
        resource = Resource.query.get_or_404(resource_id)
        
        # Check if user is uploader or admin
        if resource.user_id != current_user.id and not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        data = request.get_json()
        
        # Update resource fields
        resource.title = data.get('title', resource.title)
        resource.content = data.get('content', resource.content)
        resource.file_path = data.get('file_path', resource.file_path)
        resource.is_public = data.get('is_public', resource.is_public)
        
        # Update tags if provided
        if 'tags' in data:
            resource.tags.clear()
            for tag_data in data['tags']:
                tag = ResourceTag.query.filter_by(name=tag_data['name']).first()
                if tag:
                    resource.tags.append(tag)
        
        db.session.commit()
        
        return resource, 200
    
    @login_required
    def delete(self, resource_id):
        """Delete a resource"""
        resource = Resource.query.get_or_404(resource_id)
        
        # Check if user is uploader or admin
        if resource.user_id != current_user.id and not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        db.session.delete(resource)
        db.session.commit()
        
        return {'message': 'Resource deleted successfully'}, 200


@api.route('/<int:resource_id>/comments')
class ResourceCommentList(Resource):
    """Resource comment list resource"""
    
    @api.marshal_list_with(resource_comment_model)
    def get(self, resource_id):
        """Get all comments for a resource"""
        comments = ResourceComment.query.filter_by(resource_id=resource_id).order_by(ResourceComment.created_at.desc()).all()
        return comments, 200
    
    @login_required
    @api.expect(api.model('Comment', {
        'content': fields.String(required=True, description='Comment content')
    }))
    @api.marshal_with(resource_comment_model)
    def post(self, resource_id):
        """Add a comment to a resource"""
        data = request.get_json()
        
        new_comment = ResourceComment(
            content=data['content'],
            user_id=current_user.id,
            resource_id=resource_id
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        return new_comment, 201


@api.route('/<int:resource_id>/like')
class ResourceLikeResource(Resource):
    """Resource like resource"""
    
    @login_required
    def post(self, resource_id):
        """Like a resource"""
        like = ResourceLike.query.filter_by(user_id=current_user.id, resource_id=resource_id).first()
        
        if like:
            # Unlike the resource
            db.session.delete(like)
            db.session.commit()
            return {'message': 'Resource unliked successfully'}, 200
        else:
            # Like the resource
            new_like = ResourceLike(
                user_id=current_user.id,
                resource_id=resource_id
            )
            db.session.add(new_like)
            db.session.commit()
            return {'message': 'Resource liked successfully'}, 201


@api.route('/tags')
class ResourceTagList(Resource):
    """Resource tag list resource"""
    
    @api.marshal_list_with(resource_tag_model)
    def get(self):
        """Get all resource tags"""
        tags = ResourceTag.query.all()
        return tags, 200
    
    @login_required
    @api.expect(resource_tag_model)
    @api.marshal_with(resource_tag_model)
    def post(self):
        """Create a new resource tag"""
        data = request.get_json()
        
        # Check if tag already exists
        if ResourceTag.query.filter_by(name=data['name']).first():
            api.abort(400, 'Tag already exists')
        
        new_tag = ResourceTag(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(new_tag)
        db.session.commit()
        
        return new_tag, 201
