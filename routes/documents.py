"""
Document Management Routes
Upload, download, and manage PDF files for online exams
"""
from flask import Blueprint, request, send_file, jsonify
from models import db, Document, User, UserRole
from utils.auth import login_required, require_role, get_current_user
from utils.response import success_response, error_response
from werkzeug.utils import secure_filename
import os
from datetime import datetime

documents_bp = Blueprint('documents', __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'documents')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'}
MAX_FILE_SIZE = 60 * 1024 * 1024  # 60 MB in bytes

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type(filename):
    """Get MIME type based on file extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    mime_types = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'txt': 'text/plain'
    }
    return mime_types.get(ext, 'application/octet-stream')


@documents_bp.route('/upload', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def upload_document():
    """Upload a document (PDF/DOC/etc.)"""
    try:
        current_user = get_current_user()
        
        # Check if file is in request
        if 'file' not in request.files:
            return error_response('No file provided', 400)
        
        file = request.files['file']
        
        if file.filename == '':
            return error_response('No file selected', 400)
        
        # Get form data
        class_name = request.form.get('class_name', '').strip()
        book_name = request.form.get('book_name', '').strip()
        chapter_name = request.form.get('chapter_name', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate required fields
        if not class_name or not book_name or not chapter_name:
            return error_response('Class name, book name, and chapter name are required', 400)
        
        # Check file type
        if not allowed_file(file.filename):
            return error_response(f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', 400)
        
        # Read file to check size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return error_response(f'File too large ({size_mb:.2f} MB). Maximum size is 60 MB', 400)
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{original_filename}"
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Create database record
        document = Document(
            class_name=class_name,
            book_name=book_name,
            chapter_name=chapter_name,
            file_name=original_filename,
            file_path=filename,  # Store relative path
            file_size=file_size,
            file_type=get_file_type(original_filename),
            description=description if description else None,
            uploaded_by=current_user.id
        )
        
        db.session.add(document)
        db.session.commit()
        
        return success_response('Document uploaded successfully', {
            'document': document.to_dict()
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)  # Clean up file if database insert fails
        return error_response(f'Failed to upload document: {str(e)}', 500)


@documents_bp.route('/upload-noauth', methods=['POST'])
def upload_document_noauth():
    """Upload document without authentication (for debugging)"""
    try:
        # Get Sample Teacher
        current_user = User.query.filter_by(first_name='Sample', last_name='Teacher', role=UserRole.TEACHER).first()
        if not current_user:
            return error_response('Sample Teacher not found', 404)
        
        # Check if file is in request
        if 'file' not in request.files:
            return error_response('No file provided', 400)
        
        file = request.files['file']
        
        if file.filename == '':
            return error_response('No file selected', 400)
        
        # Get form data
        class_name = request.form.get('class_name', '').strip()
        book_name = request.form.get('book_name', '').strip()
        chapter_name = request.form.get('chapter_name', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate required fields
        if not class_name or not book_name or not chapter_name:
            return error_response('Class name, book name, and chapter name are required', 400)
        
        # Check file type
        if not allowed_file(file.filename):
            return error_response(f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}', 400)
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return error_response(f'File too large ({size_mb:.2f} MB). Max: 60 MB', 400)
        
        # Generate filename
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{original_filename}"
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Create database record
        document = Document(
            class_name=class_name,
            book_name=book_name,
            chapter_name=chapter_name,
            file_name=original_filename,
            file_path=filename,
            file_size=file_size,
            file_type=get_file_type(original_filename),
            description=description if description else None,
            uploaded_by=current_user.id
        )
        
        db.session.add(document)
        db.session.commit()
        
        return success_response('Document uploaded successfully', {
            'document': document.to_dict()
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return error_response(f'Failed to upload document: {str(e)}', 500)


@documents_bp.route('/', methods=['GET'])
def get_documents():
    """Get all documents (with optional filters)"""
    try:
        class_name = request.args.get('class_name')
        book_name = request.args.get('book_name')
        chapter_name = request.args.get('chapter_name')
        
        query = Document.query.filter_by(is_active=True)
        
        if class_name:
            query = query.filter(Document.class_name.ilike(f'%{class_name}%'))
        if book_name:
            query = query.filter(Document.book_name.ilike(f'%{book_name}%'))
        if chapter_name:
            query = query.filter(Document.chapter_name.ilike(f'%{chapter_name}%'))
        
        documents = query.order_by(Document.created_at.desc()).all()
        
        return success_response('Documents retrieved successfully', {
            'documents': [doc.to_dict() for doc in documents],
            'total': len(documents)
        })
        
    except Exception as e:
        return error_response(f'Failed to retrieve documents: {str(e)}', 500)


@documents_bp.route('/structure', methods=['GET'])
def get_document_structure():
    """Get hierarchical structure of documents (classes -> books -> chapters)"""
    try:
        documents = Document.query.filter_by(is_active=True).all()
        
        # Build hierarchical structure
        structure = {}
        for doc in documents:
            if doc.class_name not in structure:
                structure[doc.class_name] = {}
            if doc.book_name not in structure[doc.class_name]:
                structure[doc.class_name][doc.book_name] = {}
            if doc.chapter_name not in structure[doc.class_name][doc.book_name]:
                structure[doc.class_name][doc.book_name][doc.chapter_name] = []
            structure[doc.class_name][doc.book_name][doc.chapter_name].append(doc.to_dict())
        
        return success_response('Document structure retrieved', {
            'structure': structure
        })
        
    except Exception as e:
        return error_response(f'Failed to retrieve structure: {str(e)}', 500)


@documents_bp.route('/<int:document_id>/download', methods=['GET'])
def download_document(document_id):
    """Download a document"""
    try:
        document = Document.query.get(document_id)
        
        if not document or not document.is_active:
            return error_response('Document not found', 404)
        
        file_path = os.path.join(UPLOAD_FOLDER, document.file_path)
        
        if not os.path.exists(file_path):
            return error_response('File not found on server', 404)
        
        # Increment download count
        document.download_count += 1
        db.session.commit()
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=document.file_name,
            mimetype=document.file_type
        )
        
    except Exception as e:
        return error_response(f'Failed to download document: {str(e)}', 500)


@documents_bp.route('/<int:document_id>', methods=['DELETE'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def delete_document(document_id):
    """Delete a document (soft delete)"""
    try:
        current_user = get_current_user()
        document = Document.query.get(document_id)
        
        if not document:
            return error_response('Document not found', 404)
        
        # Check if user has permission to delete
        if current_user.role != UserRole.SUPER_USER and document.uploaded_by != current_user.id:
            return error_response('You do not have permission to delete this document', 403)
        
        # Soft delete
        document.is_active = False
        db.session.commit()
        
        return success_response('Document deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete document: {str(e)}', 500)


@documents_bp.route('/<int:document_id>/delete-noauth', methods=['DELETE', 'POST'])
def delete_document_noauth(document_id):
    """Delete document without auth (for debugging)"""
    try:
        document = Document.query.get(document_id)
        
        if not document:
            return error_response('Document not found', 404)
        
        document.is_active = False
        db.session.commit()
        
        return success_response('Document deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete document: {str(e)}', 500)
