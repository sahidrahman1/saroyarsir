"""
Utilities package for SmartGardenHub
Exposes authentication helpers, response formatting, and password generation utilities.
"""
from .auth import (
    login_required,
    require_role,
    get_current_user,
    get_current_user_id,
    get_current_user_role,
    is_teacher_or_admin,
    is_admin,
    is_student,
    check_batch_access,
    check_user_access,
    generate_password_hash,
    check_password_hash,
)
from .response import (
    success_response,
    error_response,
    paginated_response,
    serialize_data,
)
from .password_generator import (
    generate_unique_student_password,
    generate_secure_student_password,
    generate_simple_unique_password,
    validate_student_password_strength,
)

__all__ = [
    'login_required', 'require_role', 'get_current_user', 'get_current_user_id', 'get_current_user_role',
    'is_teacher_or_admin', 'is_admin', 'is_student', 'check_batch_access', 'check_user_access',
    'generate_password_hash', 'check_password_hash',
    'success_response', 'error_response', 'paginated_response', 'serialize_data',
    'generate_unique_student_password', 'generate_secure_student_password', 'generate_simple_unique_password',
    'validate_student_password_strength'
]
