# Document Management System

## Overview
Complete PDF/document storage system for online exams and study materials. Teachers can upload documents organized by class, book, and chapter. Students can browse and download materials in both list and tree view.

## Features Implemented

### Backend (API Routes)
✅ **File:** `routes/documents.py`
- `POST /api/documents/upload` - Authenticated file upload
- `POST /api/documents/upload-noauth` - Debug upload (uses Sample Teacher)
- `GET /api/documents/` - List documents with optional filters (class, book, chapter)
- `GET /api/documents/structure` - Hierarchical class/book/chapter structure
- `GET /api/documents/<id>/download` - Download file (increments counter)
- `DELETE /api/documents/<id>` - Soft delete (authenticated)
- `POST /api/documents/<id>/delete-noauth` - Debug delete

### Database
✅ **File:** `models.py` (lines 597-649)
- **Document Model Fields:**
  - `id` - Primary key
  - `class_name` - Class name (e.g., "HSC Science")
  - `book_name` - Book name (e.g., "Physics")
  - `chapter_name` - Chapter name (e.g., "Chapter 1")
  - `file_name` - Original filename
  - `file_path` - Storage path
  - `file_size` - Size in bytes
  - `file_type` - MIME type
  - `description` - Optional description
  - `uploaded_by` - Foreign key to users table
  - `is_active` - Soft delete flag
  - `download_count` - Download tracking
  - `created_at` - Upload timestamp
  - `updated_at` - Last modified timestamp

✅ **Migration:** `migrate_add_documents.py`
- Creates documents table in SQLite
- Creates `/uploads/documents/` directory
- SQLAlchemy 2.0 compatible

### File Validation
- **Max file size:** 60 MB
- **Allowed types:** PDF, DOC, DOCX, PPT, PPTX, TXT
- **Security:** Uses `secure_filename()` for safe storage
- **Unique names:** Adds timestamp to prevent conflicts

### Teacher UI
✅ **File:** `templates/partials/document_management.html`
- **Upload Modal:**
  - Class name input
  - Book name input
  - Chapter name input
  - Description (optional)
  - File picker with drag-and-drop
  - Size validation (shows warning if > 60 MB)
  - Progress indicator
- **Document List:**
  - Tabular view with all metadata
  - Filter by class/book/chapter
  - Download and delete actions
  - Active/inactive status badges
  - Download count display
- **Real-time filtering:** Client-side search across all fields

### Student UI
✅ **File:** `templates/partials/student_documents.html`
- **Two View Modes:**
  1. **List View** (default):
     - Card-based layout
     - Shows all document details
     - File type icons (PDF, DOC, PPT)
     - Download button per document
     - File size and download count
     - Upload date
  2. **Tree View:**
     - Hierarchical structure: Class → Book → Chapter → Documents
     - Expandable/collapsible sections
     - Compact document list per chapter
- **Search:** Real-time search across class, book, chapter, and filename
- **Toggle:** Switch between list and tree view with one click

### Integration
✅ **Teacher Dashboard:** `templates/templates/dashboard_teacher.html`
- Added "Documents" menu item (icon: fa-file-pdf)
- Includes `partials/document_management.html`

✅ **Student Dashboard:** `templates/templates/dashboard_student.html`
- Added "Study Materials" menu item (icon: fa-file-pdf)
- Includes `partials/student_documents.html`

✅ **App Registration:** `app.py`
- Imported `documents_bp`
- Registered at `/api/documents`

## File Storage
- **Directory:** `/workspaces/saro/uploads/documents/`
- **Naming:** `{timestamp}_{secure_filename}`
- **Organization:** Flat storage, hierarchical metadata in database

## API Endpoints Summary

### Upload
```
POST /api/documents/upload
POST /api/documents/upload-noauth  (debug)

FormData:
- file: File object
- class_name: string
- book_name: string
- chapter_name: string
- description: string (optional)

Returns:
{
  "success": true,
  "message": "Document uploaded successfully",
  "document": { ...document object... }
}
```

### List
```
GET /api/documents/?class_name=HSC&book_name=Physics&chapter_name=Chapter1&include_inactive=false

Returns:
{
  "success": true,
  "documents": [ ...array of documents... ],
  "total": 10
}
```

### Structure
```
GET /api/documents/structure

Returns:
{
  "success": true,
  "structure": {
    "HSC Science": {
      "Physics": {
        "Chapter 1": [ ...documents... ],
        "Chapter 2": [ ...documents... ]
      },
      "Chemistry": { ... }
    },
    "SSC": { ... }
  }
}
```

### Download
```
GET /api/documents/<id>/download

Returns: File stream with proper MIME type
Side effect: Increments download_count
```

### Delete
```
DELETE /api/documents/<id>
POST /api/documents/<id>/delete-noauth  (debug)

Returns:
{
  "success": true,
  "message": "Document deleted successfully"
}
```

## Testing Checklist
- ✅ Migration run successfully
- ✅ Upload directory created
- ✅ Documents blueprint registered
- ✅ Server started on port 3001
- ⏳ Test teacher upload (60MB validation)
- ⏳ Test student list view
- ⏳ Test student tree view
- ⏳ Test search functionality
- ⏳ Test download
- ⏳ Test delete

## Usage Instructions

### For Teachers:
1. Log in to teacher dashboard
2. Click "Documents" in sidebar
3. Click "Upload Document" button
4. Fill in class, book, chapter names
5. Select file (max 60 MB)
6. Add optional description
7. Click "Upload"
8. View uploaded documents in table
9. Use filters to find specific documents
10. Download or delete as needed

### For Students:
1. Log in to student dashboard
2. Click "Study Materials" in sidebar
3. **List View:**
   - Scroll through all documents
   - Use search bar to filter
   - Click "Download" on any document
4. **Tree View:**
   - Click "Switch to Tree View"
   - Expand class → book → chapter
   - Click download link on documents

## Future Enhancements (Optional)
- [ ] File preview (PDF viewer)
- [ ] Bulk upload
- [ ] Tags/categories
- [ ] Student bookmarks/favorites
- [ ] Download statistics dashboard
- [ ] File version control
- [ ] Compression for large files
- [ ] Cloud storage integration (S3)
- [ ] OCR for text search
- [ ] Thumbnail generation

## Security Notes
- Uses `secure_filename()` to prevent directory traversal
- File size validation on client and server
- File type validation by extension and MIME type
- Soft delete (preserves data, just marks inactive)
- Authentication required for upload/delete (noauth versions for testing only)

## Troubleshooting
- **Upload fails:** Check file size < 60 MB and file type is allowed
- **Documents not showing:** Check `is_active=True` in database
- **Download fails:** Verify file exists in `/uploads/documents/`
- **Tree view empty:** Run `/api/documents/structure` to check hierarchy

## Database Schema
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name VARCHAR(200) NOT NULL,
    book_name VARCHAR(200) NOT NULL,
    chapter_name VARCHAR(200) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50) NOT NULL DEFAULT 'application/pdf',
    description TEXT,
    uploaded_by INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    download_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users (id)
);
```

## Files Modified/Created
1. ✅ `models.py` - Added Document model
2. ✅ `migrate_add_documents.py` - Migration script
3. ✅ `routes/documents.py` - Complete API (360+ lines)
4. ✅ `templates/partials/document_management.html` - Teacher UI
5. ✅ `templates/partials/student_documents.html` - Student UI
6. ✅ `templates/templates/dashboard_teacher.html` - Menu + integration
7. ✅ `templates/templates/dashboard_student.html` - Menu + integration
8. ✅ `app.py` - Blueprint registration

---
**Status:** ✅ Complete and ready for testing
**Server:** Running on port 3001
**Next:** Test upload/download functionality
