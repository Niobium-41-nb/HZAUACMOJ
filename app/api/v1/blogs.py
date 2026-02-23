from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required, current_user
from app.extensions import db
from app.models.blog import Blog, BlogTag, BlogComment, BlogLike
from app.models.user import User


api = Namespace('blogs', description='Blog operations')

# Model definitions
blog_tag_model = api.model('BlogTag', {
    'id': fields.Integer(readonly=True, description='Tag ID'),
    'name': fields.String(required=True, description='Tag name'),
    'description': fields.String(description='Tag description')
})

blog_model = api.model('Blog', {
    'id': fields.Integer(readonly=True, description='Blog ID'),
    'title': fields.String(required=True, description='Blog title'),
    'content': fields.String(required=True, description='Blog content'),
    'summary': fields.String(description='Blog summary'),
    'user_id': fields.Integer(description='Author ID'),
    'views': fields.Integer(readonly=True, description='View count'),
    'likes_count': fields.Integer(readonly=True, description='Like count'),
    'comments_count': fields.Integer(readonly=True, description='Comment count'),
    'is_published': fields.Boolean(description='Is published'),
    'created_at': fields.DateTime(readonly=True, description='Created at'),
    'updated_at': fields.DateTime(readonly=True, description='Updated at'),
    'tags': fields.List(fields.Nested(blog_tag_model), description='Blog tags')
})

blog_comment_model = api.model('BlogComment', {
    'id': fields.Integer(readonly=True, description='Comment ID'),
    'content': fields.String(required=True, description='Comment content'),
    'user_id': fields.Integer(description='User ID'),
    'blog_id': fields.Integer(description='Blog ID'),
    'created_at': fields.DateTime(readonly=True, description='Created at')
})

@api.route('/')
class BlogList(Resource):
    """Blog list resource"""
    
    @api.marshal_list_with(blog_model)
    def get(self):
        """Get all published blogs"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        blogs = Blog.query.filter_by(is_published=True).order_by(Blog.created_at.desc()).paginate(page=page, per_page=per_page)
        return blogs.items, 200
    
    @login_required
    @api.expect(blog_model)
    @api.marshal_with(blog_model)
    def post(self):
        """Create a new blog"""
        data = request.get_json()
        
        new_blog = Blog(
            title=data['title'],
            content=data['content'],
            summary=data.get('summary'),
            user_id=current_user.id,
            is_published=data.get('is_published', False)
        )
        
        # Add tags if provided
        if 'tags' in data:
            for tag_data in data['tags']:
                tag = BlogTag.query.filter_by(name=tag_data['name']).first()
                if tag:
                    new_blog.tags.append(tag)
        
        db.session.add(new_blog)
        db.session.commit()
        
        return new_blog, 201


@api.route('/<int:blog_id>')
class BlogDetail(Resource):
    """Blog detail resource"""
    
    @api.marshal_with(blog_model)
    def get(self, blog_id):
        """Get a blog by ID"""
        blog = Blog.query.get_or_404(blog_id)
        
        # Increment view count
        blog.views += 1
        db.session.commit()
        
        return blog, 200
    
    @login_required
    @api.expect(blog_model)
    @api.marshal_with(blog_model)
    def put(self, blog_id):
        """Update a blog"""
        blog = Blog.query.get_or_404(blog_id)
        
        # Check if user is author or admin
        if blog.user_id != current_user.id and not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        data = request.get_json()
        
        # Update blog fields
        blog.title = data.get('title', blog.title)
        blog.content = data.get('content', blog.content)
        blog.summary = data.get('summary', blog.summary)
        blog.is_published = data.get('is_published', blog.is_published)
        
        # Update tags if provided
        if 'tags' in data:
            blog.tags.clear()
            for tag_data in data['tags']:
                tag = BlogTag.query.filter_by(name=tag_data['name']).first()
                if tag:
                    blog.tags.append(tag)
        
        db.session.commit()
        
        return blog, 200
    
    @login_required
    def delete(self, blog_id):
        """Delete a blog"""
        blog = Blog.query.get_or_404(blog_id)
        
        # Check if user is author or admin
        if blog.user_id != current_user.id and not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        db.session.delete(blog)
        db.session.commit()
        
        return {'message': 'Blog deleted successfully'}, 200


@api.route('/<int:blog_id>/comments')
class BlogCommentList(Resource):
    """Blog comment list resource"""
    
    @api.marshal_list_with(blog_comment_model)
    def get(self, blog_id):
        """Get all comments for a blog"""
        comments = BlogComment.query.filter_by(blog_id=blog_id).order_by(BlogComment.created_at.desc()).all()
        return comments, 200
    
    @login_required
    @api.expect(api.model('Comment', {
        'content': fields.String(required=True, description='Comment content')
    }))
    @api.marshal_with(blog_comment_model)
    def post(self, blog_id):
        """Add a comment to a blog"""
        data = request.get_json()
        
        new_comment = BlogComment(
            content=data['content'],
            user_id=current_user.id,
            blog_id=blog_id
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        return new_comment, 201


@api.route('/<int:blog_id>/like')
class BlogLikeResource(Resource):
    """Blog like resource"""
    
    @login_required
    def post(self, blog_id):
        """Like a blog"""
        like = BlogLike.query.filter_by(user_id=current_user.id, blog_id=blog_id).first()
        
        if like:
            # Unlike the blog
            db.session.delete(like)
            db.session.commit()
            return {'message': 'Blog unliked successfully'}, 200
        else:
            # Like the blog
            new_like = BlogLike(
                user_id=current_user.id,
                blog_id=blog_id
            )
            db.session.add(new_like)
            db.session.commit()
            return {'message': 'Blog liked successfully'}, 201


@api.route('/tags')
class BlogTagList(Resource):
    """Blog tag list resource"""
    
    @api.marshal_list_with(blog_tag_model)
    def get(self):
        """Get all blog tags"""
        tags = BlogTag.query.all()
        return tags, 200
    
    @login_required
    @api.expect(blog_tag_model)
    @api.marshal_with(blog_tag_model)
    def post(self):
        """Create a new blog tag"""
        data = request.get_json()
        
        # Check if tag already exists
        if BlogTag.query.filter_by(name=data['name']).first():
            api.abort(400, 'Tag already exists')
        
        new_tag = BlogTag(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(new_tag)
        db.session.commit()
        
        return new_tag, 201
