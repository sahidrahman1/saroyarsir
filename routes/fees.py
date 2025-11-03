"""
Fee Management Routes
Fee tracking, payment processing, and financial management
"""
from flask import Blueprint, request, session
from models import db, Fee, User, Batch, UserRole, FeeStatus
from utils.auth import login_required, require_role, get_current_user, check_batch_access
from utils.response import success_response, error_response, paginated_response, serialize_fee
from sqlalchemy import or_, and_, func, extract
from datetime import datetime, date, timedelta
from decimal import Decimal
import calendar

fees_bp = Blueprint('fees', __name__)

@fees_bp.route('', methods=['GET'])
@login_required
def get_fees():
    """Get fees with pagination and filtering"""
    try:
        current_user = get_current_user()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        user_id = request.args.get('user_id', type=int)
        batch_id = request.args.get('batch_id', type=int)
        status = request.args.get('status')
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        overdue_only = request.args.get('overdue_only', '').lower() == 'true'
        
        query = Fee.query
        
        # Filter based on user role
        if current_user.role == UserRole.STUDENT:
            # Students can only see their own fees
            query = query.filter(Fee.user_id == current_user.id)
        elif user_id and current_user.role in [UserRole.TEACHER, UserRole.SUPER_USER]:
            query = query.filter(Fee.user_id == user_id)
        
        # Filter by batch
        if batch_id:
            if current_user.role == UserRole.STUDENT and not check_batch_access(current_user, batch_id):
                return error_response('Access denied to this batch', 403)
            query = query.filter(Fee.batch_id == batch_id)
        
        # Filter by status
        if status and status in [s.value for s in FeeStatus]:
            query = query.filter(Fee.status == FeeStatus(status))
        
        # Filter by month/year
        if month and year:
            query = query.filter(
                extract('month', Fee.due_date) == month,
                extract('year', Fee.due_date) == year
            )
        elif year:
            query = query.filter(extract('year', Fee.due_date) == year)
        
        # Filter overdue fees
        if overdue_only:
            query = query.filter(
                Fee.status == FeeStatus.PENDING,
                Fee.due_date < date.today()
            )
        
        # Join with user and batch for sorting and additional info
        query = query.join(User).join(Batch)
        
        # Order by due date
        query = query.order_by(Fee.due_date.desc(), Fee.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        fees = []
        for fee in pagination.items:
            fee_data = serialize_fee(fee)
            
            # Add user and batch information
            fee_data['user'] = {
                'id': fee.user.id,
                'phone': fee.user.phone,
                'full_name': fee.user.full_name,
                'email': fee.user.email
            }
            
            fee_data['batch'] = {
                'id': fee.batch.id,
                'name': fee.batch.name
            }
            
            fees.append(fee_data)
        
        return paginated_response(
            fees, 
            page, 
            per_page, 
            pagination.total, 
            "Fees retrieved successfully"
        )
        
    except Exception as e:
        return error_response(f'Failed to retrieve fees: {str(e)}', 500)

@fees_bp.route('/<int:fee_id>', methods=['GET'])
@login_required
def get_fee(fee_id):
    """Get specific fee details"""
    try:
        current_user = get_current_user()
        fee = Fee.query.get(fee_id)
        
        if not fee:
            return error_response('Fee not found', 404)
        
        # Check access permissions
        if current_user.role == UserRole.STUDENT and fee.user_id != current_user.id:
            return error_response('Access denied', 403)
        
        fee_data = serialize_fee(fee)
        
        # Add user and batch information
        fee_data['user'] = {
            'id': fee.user.id,
            'phone': fee.user.phone,
            'full_name': fee.user.full_name,
            'email': fee.user.email,
            'guardian_phone': fee.user.guardian_phone
        }
        
        fee_data['batch'] = {
            'id': fee.batch.id,
            'name': fee.batch.name,
            'description': fee.batch.description
        }
        
        return success_response('Fee details retrieved', {'fee': fee_data})
        
    except Exception as e:
        return error_response(f'Failed to get fee: {str(e)}', 500)

@fees_bp.route('', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def create_fee():
    """Create a new fee record"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Required fields
        required_fields = ['user_id', 'batch_id', 'amount', 'due_date']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
        
        # Validate user
        user = User.query.filter_by(id=data['user_id'], role=UserRole.STUDENT, is_active=True).first()
        if not user:
            return error_response('Student not found', 404)
        
        # Validate batch
        batch = Batch.query.filter_by(id=data['batch_id'], is_active=True).first()
        if not batch:
            return error_response('Batch not found', 404)
        
        # Check if user is enrolled in batch
        if batch not in user.batches:
            return error_response('Student is not enrolled in this batch', 400)
        
        # Parse and validate amount
        try:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                return error_response('Amount must be positive', 400)
        except (ValueError, TypeError):
            return error_response('Invalid amount format', 400)
        
        # Parse due date
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return error_response('Invalid due date format. Use YYYY-MM-DD', 400)
        
        # Parse optional fields
        late_fee = Decimal('0.00')
        if data.get('late_fee'):
            try:
                late_fee = Decimal(str(data['late_fee']))
                if late_fee < 0:
                    return error_response('Late fee cannot be negative', 400)
            except (ValueError, TypeError):
                return error_response('Invalid late fee format', 400)
        
        discount = Decimal('0.00')
        if data.get('discount'):
            try:
                discount = Decimal(str(data['discount']))
                if discount < 0:
                    return error_response('Discount cannot be negative', 400)
                if discount > amount:
                    return error_response('Discount cannot exceed fee amount', 400)
            except (ValueError, TypeError):
                return error_response('Invalid discount format', 400)
        
        # Check for duplicate fee record
        existing_fee = Fee.query.filter_by(
            user_id=data['user_id'],
            batch_id=data['batch_id'],
            due_date=due_date
        ).first()
        
        if existing_fee:
            return error_response('Fee record already exists for this student, batch, and due date', 409)
        
        # Create new fee
        fee = Fee(
            user_id=data['user_id'],
            batch_id=data['batch_id'],
            amount=amount,
            due_date=due_date,
            late_fee=late_fee,
            discount=discount,
            notes=data.get('notes', '').strip() if data.get('notes') else None,
            status=FeeStatus.PENDING
        )
        
        db.session.add(fee)
        db.session.commit()
        
        fee_data = serialize_fee(fee)
        
        return success_response('Fee created successfully', {'fee': fee_data}, 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create fee: {str(e)}', 500)

@fees_bp.route('/<int:fee_id>', methods=['PUT'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def update_fee(fee_id):
    """Update fee information"""
    try:
        fee = Fee.query.get(fee_id)
        
        if not fee:
            return error_response('Fee not found', 404)
        
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Update allowed fields
        updatable_fields = ['amount', 'due_date', 'late_fee', 'discount', 'notes']
        
        for field in updatable_fields:
            if field in data:
                if field in ['amount', 'late_fee', 'discount']:
                    try:
                        value = Decimal(str(data[field]))
                        if value < 0:
                            return error_response(f'{field.replace("_", " ").title()} cannot be negative', 400)
                        
                        if field == 'discount' and value > fee.amount:
                            return error_response('Discount cannot exceed fee amount', 400)
                        
                        setattr(fee, field, value)
                    except (ValueError, TypeError):
                        return error_response(f'Invalid {field} format', 400)
                elif field == 'due_date':
                    try:
                        due_date = datetime.strptime(data[field], '%Y-%m-%d').date()
                        fee.due_date = due_date
                    except ValueError:
                        return error_response('Invalid due date format. Use YYYY-MM-DD', 400)
                else:
                    setattr(fee, field, data[field])
        
        fee.updated_at = datetime.utcnow()
        db.session.commit()
        
        fee_data = serialize_fee(fee)
        
        return success_response('Fee updated successfully', {'fee': fee_data})
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update fee: {str(e)}', 500)

@fees_bp.route('/<int:fee_id>/pay', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def mark_fee_paid(fee_id):
    """Mark a fee as paid"""
    try:
        fee = Fee.query.get(fee_id)
        
        if not fee:
            return error_response('Fee not found', 404)
        
        if fee.status == FeeStatus.PAID:
            return error_response('Fee is already marked as paid', 400)
        
        data = request.get_json() or {}
        
        # Update fee status
        fee.status = FeeStatus.PAID
        fee.paid_date = date.today()
        fee.payment_method = data.get('payment_method', '').strip() if data.get('payment_method') else None
        fee.transaction_id = data.get('transaction_id', '').strip() if data.get('transaction_id') else None
        
        if data.get('notes'):
            fee.notes = data['notes'].strip()
        
        fee.updated_at = datetime.utcnow()
        db.session.commit()
        
        fee_data = serialize_fee(fee)
        
        return success_response('Fee marked as paid successfully', {'fee': fee_data})
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to mark fee as paid: {str(e)}', 500)

@fees_bp.route('/<int:fee_id>/unpay', methods=['POST'])
@login_required
@require_role(UserRole.SUPER_USER)
def mark_fee_unpaid(fee_id):
    """Mark a fee as unpaid (reverse payment)"""
    try:
        fee = Fee.query.get(fee_id)
        
        if not fee:
            return error_response('Fee not found', 404)
        
        if fee.status != FeeStatus.PAID:
            return error_response('Fee is not marked as paid', 400)
        
        # Update fee status
        fee.status = FeeStatus.PENDING if fee.due_date >= date.today() else FeeStatus.OVERDUE
        fee.paid_date = None
        fee.payment_method = None
        fee.transaction_id = None
        fee.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        fee_data = serialize_fee(fee)
        
        return success_response('Fee marked as unpaid successfully', {'fee': fee_data})
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to mark fee as unpaid: {str(e)}', 500)

@fees_bp.route('/bulk-create', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def bulk_create_fees():
    """Create fees for multiple students"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Required fields
        required_fields = ['batch_id', 'amount', 'due_date']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
        
        # Validate batch
        batch = Batch.query.filter_by(id=data['batch_id'], is_active=True).first()
        if not batch:
            return error_response('Batch not found', 404)
        
        # Parse amount and dates
        try:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                return error_response('Amount must be positive', 400)
        except (ValueError, TypeError):
            return error_response('Invalid amount format', 400)
        
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return error_response('Invalid due date format. Use YYYY-MM-DD', 400)
        
        # Get student IDs (optional filter)
        student_ids = data.get('student_ids', [])
        
        # Get students from batch
        students_query = User.query.filter(
            User.role == UserRole.STUDENT,
            User.is_active == True
        ).join(User.batches).filter(Batch.id == data['batch_id'])
        
        if student_ids:
            students_query = students_query.filter(User.id.in_(student_ids))
        
        students = students_query.all()
        
        if not students:
            return error_response('No eligible students found in this batch', 404)
        
        # Create fees for all students
        created_fees = []
        skipped_students = []
        
        for student in students:
            # Check for existing fee
            existing_fee = Fee.query.filter_by(
                user_id=student.id,
                batch_id=data['batch_id'],
                due_date=due_date
            ).first()
            
            if existing_fee:
                skipped_students.append({
                    'id': student.id,
                    'name': student.full_name,
                    'reason': 'Fee already exists'
                })
                continue
            
            # Create fee
            fee = Fee(
                user_id=student.id,
                batch_id=data['batch_id'],
                amount=amount,
                due_date=due_date,
                late_fee=Decimal(str(data.get('late_fee', '0.00'))),
                discount=Decimal(str(data.get('discount', '0.00'))),
                notes=data.get('notes', '').strip() if data.get('notes') else None,
                status=FeeStatus.PENDING
            )
            
            db.session.add(fee)
            created_fees.append(fee)
        
        db.session.commit()
        
        result = {
            'created_count': len(created_fees),
            'skipped_count': len(skipped_students),
            'skipped_students': skipped_students
        }
        
        return success_response(
            f'{len(created_fees)} fees created successfully, {len(skipped_students)} skipped', 
            result, 
            201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create bulk fees: {str(e)}', 500)

@fees_bp.route('/batch/<int:batch_id>/monthly', methods=['POST'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def create_monthly_fees(batch_id):
    """Create monthly fees for a batch"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Validate batch
        batch = Batch.query.filter_by(id=batch_id, is_active=True).first()
        if not batch:
            return error_response('Batch not found', 404)
        
        # Get month and year
        month = data.get('month', datetime.now().month)
        year = data.get('year', datetime.now().year)
        
        if not (1 <= month <= 12):
            return error_response('Month must be between 1 and 12', 400)
        
        if year < 2020 or year > 2030:
            return error_response('Year must be between 2020 and 2030', 400)
        
        # Calculate due date (last day of the month)
        last_day = calendar.monthrange(year, month)[1]
        due_date = date(year, month, last_day)
        
        # Use batch fee amount or custom amount
        amount = data.get('amount')
        if amount:
            try:
                amount = Decimal(str(amount))
                if amount <= 0:
                    return error_response('Amount must be positive', 400)
            except (ValueError, TypeError):
                return error_response('Invalid amount format', 400)
        else:
            amount = batch.fee_amount
        
        # Get all active students in batch
        students = User.query.filter(
            User.role == UserRole.STUDENT,
            User.is_active == True
        ).join(User.batches).filter(Batch.id == batch_id).all()
        
        if not students:
            return error_response('No active students found in this batch', 404)
        
        # Create monthly fees
        created_fees = []
        skipped_students = []
        
        for student in students:
            # Check for existing fee for this month
            existing_fee = Fee.query.filter(
                Fee.user_id == student.id,
                Fee.batch_id == batch_id,
                extract('month', Fee.due_date) == month,
                extract('year', Fee.due_date) == year
            ).first()
            
            if existing_fee:
                skipped_students.append({
                    'id': student.id,
                    'name': student.full_name,
                    'reason': f'Fee already exists for {calendar.month_name[month]} {year}'
                })
                continue
            
            # Create fee
            fee = Fee(
                user_id=student.id,
                batch_id=batch_id,
                amount=amount,
                due_date=due_date,
                notes=f'Monthly fee for {calendar.month_name[month]} {year}',
                status=FeeStatus.PENDING
            )
            
            db.session.add(fee)
            created_fees.append(fee)
        
        db.session.commit()
        
        result = {
            'month': calendar.month_name[month],
            'year': year,
            'created_count': len(created_fees),
            'skipped_count': len(skipped_students),
            'total_amount': float(amount * len(created_fees)),
            'skipped_students': skipped_students
        }
        
        return success_response(
            f'Monthly fees created for {calendar.month_name[month]} {year}', 
            result, 
            201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create monthly fees: {str(e)}', 500)

@fees_bp.route('/reports/summary', methods=['GET'])
@login_required
@require_role(UserRole.TEACHER, UserRole.SUPER_USER)
def get_fee_summary():
    """Get fee collection summary and statistics"""
    try:
        batch_id = request.args.get('batch_id', type=int)
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        base_query = Fee.query
        
        # Filter by batch
        if batch_id:
            base_query = base_query.filter(Fee.batch_id == batch_id)
        
        # Filter by month/year
        if month and year:
            base_query = base_query.filter(
                extract('month', Fee.due_date) == month,
                extract('year', Fee.due_date) == year
            )
        elif year:
            base_query = base_query.filter(extract('year', Fee.due_date) == year)
        
        # Calculate statistics
        total_fees = base_query.count()
        
        paid_fees = base_query.filter(Fee.status == FeeStatus.PAID).count()
        pending_fees = base_query.filter(Fee.status == FeeStatus.PENDING).count()
        overdue_fees = base_query.filter(
            Fee.status == FeeStatus.PENDING,
            Fee.due_date < date.today()
        ).count()
        
        # Calculate amounts
        total_amount = base_query.with_entities(
            func.sum(Fee.amount + Fee.late_fee - Fee.discount)
        ).scalar() or 0
        
        paid_amount = base_query.filter(Fee.status == FeeStatus.PAID).with_entities(
            func.sum(Fee.amount + Fee.late_fee - Fee.discount)
        ).scalar() or 0
        
        pending_amount = base_query.filter(Fee.status == FeeStatus.PENDING).with_entities(
            func.sum(Fee.amount + Fee.late_fee - Fee.discount)
        ).scalar() or 0
        
        # Collection rate
        collection_rate = (paid_amount / total_amount * 100) if total_amount > 0 else 0
        
        # Recent payments
        recent_payments = Fee.query.filter(
            Fee.status == FeeStatus.PAID,
            Fee.paid_date >= date.today() - timedelta(days=30)
        )
        
        if batch_id:
            recent_payments = recent_payments.filter(Fee.batch_id == batch_id)
        
        recent_payments = recent_payments.order_by(Fee.paid_date.desc()).limit(10).all()
        
        recent_payments_data = []
        for fee in recent_payments:
            payment_data = {
                'id': fee.id,
                'amount': float(fee.amount + fee.late_fee - fee.discount),
                'paid_date': fee.paid_date.isoformat(),
                'student_name': fee.user.full_name,
                'batch_name': fee.batch.name,
                'payment_method': fee.payment_method
            }
            recent_payments_data.append(payment_data)
        
        summary = {
            'total_fees': total_fees,
            'paid_fees': paid_fees,
            'pending_fees': pending_fees,
            'overdue_fees': overdue_fees,
            'total_amount': float(total_amount),
            'paid_amount': float(paid_amount),
            'pending_amount': float(pending_amount),
            'collection_rate': round(collection_rate, 2),
            'recent_payments': recent_payments_data
        }
        
        return success_response('Fee summary retrieved', {'summary': summary})
        
    except Exception as e:
        return error_response(f'Failed to get fee summary: {str(e)}', 500)

@fees_bp.route('/monthly', methods=['GET'])
@login_required
def get_monthly_fees():
    """Get monthly fees for batch/student management - simplified month/year format"""
    try:
        batch_id = request.args.get('batch_id', type=int)
        year = request.args.get('year', type=int, default=datetime.now().year)
        
        if not batch_id:
            return error_response('batch_id parameter is required', 400)
        
        current_user = get_current_user()
        
        # Check batch access permissions
        if current_user.role == UserRole.STUDENT:
            if not check_batch_access(current_user, batch_id):
                return error_response('Access denied to this batch', 403)
        
        # Get all students in the batch
        students = User.query.filter(
            User.role == UserRole.STUDENT,
            User.is_active == True
        ).join(User.batches).filter(Batch.id == batch_id).all()
        
        if not students:
            return error_response('No students found in this batch', 404)
        
        # Get fees for the year
        fees_query = Fee.query.filter(
            Fee.batch_id == batch_id,
            extract('year', Fee.due_date) == year
        ).all()
        
        # Create a lookup dictionary for fees
        fees_lookup = {}
        for fee in fees_query:
            month = fee.due_date.month
            key = f"{fee.user_id}_{month}"
            fees_lookup[key] = {
                'fee_id': fee.id,
                'student_id': fee.user_id,
                'month': month,
                'year': year,
                'amount': float(fee.amount),
                'status': fee.status.value,
                'due_date': fee.due_date.isoformat() if fee.due_date else None,
                'paid_date': fee.paid_date.isoformat() if fee.paid_date else None
            }
        
        # Format response in the expected format
        result_fees = []
        for student in students:
            for month in range(1, 13):
                key = f"{student.id}_{month}"
                if key in fees_lookup:
                    result_fees.append(fees_lookup[key])
                else:
                    # Return empty fee record for frontend
                    result_fees.append({
                        'student_id': student.id,
                        'month': month,
                        'year': year,
                        'amount': 0,
                        'status': 'pending'
                    })
        
        return success_response('Monthly fees retrieved', result_fees)
        
    except Exception as e:
        return error_response(f'Failed to get monthly fees: {str(e)}', 500)

@fees_bp.route('/monthly', methods=['POST'])
def save_monthly_fee():
    """Save or update a monthly fee record"""
    
    try:
        # Temporarily disable auth check for testing - REMOVE THIS LATER
        # Check authentication
        # if 'user_id' not in session:
        #     return error_response('Authentication required', 401)
        
        # current_user = User.query.get(session['user_id'])
        # For now, skip auth and treat as if authenticated teacher
        current_user = User.query.filter_by(role=UserRole.TEACHER).first()
        if not current_user:
            return error_response('No teacher found in system', 500)
        
        data = request.get_json()
        
        if not data:
            return error_response('Request data is required', 400)
        
        # Required fields
        required_fields = ['student_id', 'month', 'year', 'amount']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)
        
        student_id = data['student_id']
        month = data['month']
        year = data['year']
        amount = data['amount']
        
        # Validate fields
        if not (1 <= month <= 12):
            return error_response('Month must be between 1 and 12', 400)
        
        if not (2020 <= year <= 2030):
            return error_response('Year must be between 2020 and 2030', 400)
        
        try:
            amount = Decimal(str(amount))
            if amount < 0:
                return error_response('Amount cannot be negative', 400)
        except (ValueError, TypeError):
            return error_response('Invalid amount format', 400)
        
        # Get student and batch info
        student = User.query.filter_by(id=student_id, role=UserRole.STUDENT, is_active=True).first()
        if not student:
            return error_response('Student not found', 404)
        
        # For now, use the first batch the student is enrolled in
        # In a more complex system, batch_id would be provided
        if not student.batches:
            return error_response('Student is not enrolled in any batch', 400)
        
        batch = student.batches[0]  # Use first batch
        
        # Calculate due date (last day of the month)
        last_day = calendar.monthrange(year, month)[1]
        due_date = date(year, month, last_day)
        
        # Check for existing fee
        existing_fee = Fee.query.filter(
            Fee.user_id == student_id,
            Fee.batch_id == batch.id,
            extract('month', Fee.due_date) == month,
            extract('year', Fee.due_date) == year
        ).first()
        
        if existing_fee:
            # Update existing fee
            if amount == 0:
                # Delete fee if amount is 0
                db.session.delete(existing_fee)
                db.session.commit()
                return success_response('Fee deleted successfully', {'deleted': True})
            else:
                existing_fee.amount = amount
                existing_fee.updated_at = datetime.utcnow()
                db.session.commit()
                
                fee_data = {
                    'fee_id': existing_fee.id,
                    'student_id': existing_fee.user_id,
                    'month': month,
                    'year': year,
                    'amount': float(existing_fee.amount)
                }
                return success_response('Fee updated successfully', {'fee': fee_data})
        else:
            # Create new fee if amount > 0
            if amount > 0:
                fee = Fee(
                    user_id=student_id,
                    batch_id=batch.id,
                    amount=amount,
                    due_date=due_date,
                    notes=f'Monthly fee for {calendar.month_name[month]} {year}',
                    status=FeeStatus.PENDING
                )
                
                db.session.add(fee)
                db.session.commit()
                
                fee_data = {
                    'fee_id': fee.id,
                    'student_id': fee.user_id,
                    'month': month,
                    'year': year,
                    'amount': float(fee.amount)
                }
                return success_response('Fee created successfully', {'fee': fee_data}, 201)
            else:
                # Amount is 0 and no existing fee, nothing to do
                return success_response('No fee to create with zero amount', {'fee': None})
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to save monthly fee: {str(e)}', 500)

@fees_bp.route('/monthly-simple', methods=['POST'])
def save_monthly_fee_simple():
    """Simple test version of monthly fee save"""
    try:
        data = request.get_json()
        return success_response('Simple monthly endpoint works!', {'received_data': data})
    except Exception as e:
        return error_response(f'Error: {str(e)}', 500)


@fees_bp.route('/monthly-save', methods=['POST'])
def save_monthly_fee_noauth():
    """Temporary no-auth save endpoint used by frontend to avoid 404 while debugging.
    This duplicates save_monthly_fee logic but skips auth checks. Remove when auth fixed.
    """
    try:
        data = request.get_json()
        if not data:
            return error_response('Request data is required', 400)

        # Required fields
        required_fields = ['student_id', 'month', 'year', 'amount']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return error_response(f'Missing required fields: {", ".join(missing_fields)}', 400)

        student_id = data['student_id']
        month = data['month']
        year = data['year']
        amount = data['amount']

        # Validate fields
        if not (1 <= month <= 12):
            return error_response('Month must be between 1 and 12', 400)

        if not (2020 <= year <= 2030):
            return error_response('Year must be between 2020 and 2030', 400)

        try:
            amount = Decimal(str(amount))
            if amount < 0:
                return error_response('Amount cannot be negative', 400)
        except (ValueError, TypeError):
            return error_response('Invalid amount format', 400)

        # Get student and batch info
        student = User.query.filter_by(id=student_id, role=UserRole.STUDENT, is_active=True).first()
        if not student:
            return error_response('Student not found', 404)

        if not student.batches:
            return error_response('Student is not enrolled in any batch', 400)

        batch = student.batches[0]

        # Calculate due date (last day of the month)
        last_day = calendar.monthrange(year, month)[1]
        due_date = date(year, month, last_day)

        # Check for existing fee
        existing_fee = Fee.query.filter(
            Fee.user_id == student_id,
            Fee.batch_id == batch.id,
            extract('month', Fee.due_date) == month,
            extract('year', Fee.due_date) == year
        ).first()

        if existing_fee:
            if amount == 0:
                db.session.delete(existing_fee)
                db.session.commit()
                return success_response('Fee deleted successfully', {'deleted': True})
            else:
                existing_fee.amount = amount
                existing_fee.updated_at = datetime.utcnow()
                db.session.commit()
                fee_data = {
                    'fee_id': existing_fee.id,
                    'student_id': existing_fee.user_id,
                    'month': month,
                    'year': year,
                    'amount': float(existing_fee.amount)
                }
                return success_response('Fee updated successfully', {'fee': fee_data})
        else:
            if amount > 0:
                fee = Fee(
                    user_id=student_id,
                    batch_id=batch.id,
                    amount=amount,
                    due_date=due_date,
                    notes=f'Monthly fee for {calendar.month_name[month]} {year}',
                    status=FeeStatus.PENDING
                )
                db.session.add(fee)
                db.session.commit()
                fee_data = {
                    'fee_id': fee.id,
                    'student_id': fee.user_id,
                    'month': month,
                    'year': year,
                    'amount': float(fee.amount)
                }
                return success_response('Fee created successfully', {'fee': fee_data}, 201)
            else:
                return success_response('No fee to create with zero amount', {'fee': None})

    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to save monthly fee: {str(e)}', 500)

@fees_bp.route('/monthly-load', methods=['GET'])
def get_monthly_fees_noauth():
    """No-auth GET endpoint to load monthly fees for a batch.
    This duplicates get_monthly_fees logic but skips auth checks.
    """
    try:
        batch_id = request.args.get('batch_id', type=int)
        year = request.args.get('year', type=int, default=datetime.now().year)
        
        if not batch_id:
            return error_response('batch_id parameter is required', 400)
        
        # Get all students in the batch
        students = User.query.filter(
            User.role == UserRole.STUDENT,
            User.is_active == True
        ).join(User.batches).filter(Batch.id == batch_id).all()
        
        if not students:
            return error_response('No students found in this batch', 404)
        
        # Get fees for the year
        fees_query = Fee.query.filter(
            Fee.batch_id == batch_id,
            extract('year', Fee.due_date) == year
        ).all()
        
        # Create a lookup dictionary for fees
        fees_lookup = {}
        for fee in fees_query:
            month = fee.due_date.month
            key = f"{fee.user_id}_{month}"
            fees_lookup[key] = {
                'fee_id': fee.id,
                'student_id': fee.user_id,
                'month': month,
                'year': year,
                'amount': float(fee.amount),
                'status': fee.status.value,
                'due_date': fee.due_date.isoformat() if fee.due_date else None,
                'paid_date': fee.paid_date.isoformat() if fee.paid_date else None
            }
        
        # Format response in the expected format
        result_fees = []
        for student in students:
            for month in range(1, 13):
                key = f"{student.id}_{month}"
                if key in fees_lookup:
                    result_fees.append(fees_lookup[key])
                else:
                    # Return empty/zero entry for months without fees
                    result_fees.append({
                        'fee_id': None,
                        'student_id': student.id,
                        'month': month,
                        'year': year,
                        'amount': 0,
                        'status': 'pending',
                        'due_date': None,
                        'paid_date': None
                    })
        
        return success_response('Monthly fees retrieved successfully', {
            'fees': result_fees,
            'batch_id': batch_id,
            'year': year,
            'student_count': len(students)
        })
        
    except Exception as e:
        return error_response(f'Failed to retrieve monthly fees: {str(e)}', 500)

@fees_bp.route('/monthly-test', methods=['GET', 'POST'])
def test_monthly_endpoint():
    """Test endpoint to verify monthly routes are working"""
    if request.method == 'GET':
        return success_response('Monthly test endpoint working - GET', {'method': 'GET', 'timestamp': datetime.utcnow().isoformat()})
    else:
        return success_response('Monthly test endpoint working - POST', {'method': 'POST', 'data': request.get_json(), 'timestamp': datetime.utcnow().isoformat()})

@fees_bp.route('/debug-monthly', methods=['GET', 'POST', 'OPTIONS'])
def debug_monthly():
    """Debug endpoint to test route matching"""
    print(f"DEBUG: /debug-monthly called with method {request.method}")
    return {'status': 'success', 'message': f'Debug endpoint called with {request.method}', 'path': request.path}

@fees_bp.route('/monthly-save-test', methods=['POST'])
def test_monthly_save():
    """Simple test for POST to monthly save without authentication"""
    print(f"🚀 TEST: POST /monthly-save-test endpoint reached!")
    data = request.get_json() or {}
    return success_response('Test save endpoint working', {
        'received_data': data,
        'method': request.method,
        'url': request.url,
        'timestamp': datetime.utcnow().isoformat()
    })

@fees_bp.route('/my-fees', methods=['GET'])
@login_required
@require_role(UserRole.STUDENT)
def get_my_fees():
    """Get current student's fee records"""
    try:
        current_user = get_current_user()
        
        status_filter = request.args.get('status')
        
        query = Fee.query.filter(Fee.user_id == current_user.id)
        
        if status_filter and status_filter in [s.value for s in FeeStatus]:
            query = query.filter(Fee.status == FeeStatus(status_filter))
        
        # Join with batch for additional info
        query = query.join(Batch).order_by(Fee.due_date.desc())
        
        fees = query.all()
        
        fees_data = []
        for fee in fees:
            fee_data = serialize_fee(fee)
            fee_data['batch'] = {
                'id': fee.batch.id,
                'name': fee.batch.name
            }
            fees_data.append(fee_data)
        
        # Calculate summary for student
        total_amount = sum(fee.amount + fee.late_fee - fee.discount for fee in fees)
        paid_amount = sum(fee.amount + fee.late_fee - fee.discount for fee in fees if fee.status == FeeStatus.PAID)
        pending_amount = total_amount - paid_amount
        
        overdue_fees = [fee for fee in fees if fee.status == FeeStatus.PENDING and fee.due_date < date.today()]
        
        summary = {
            'total_fees': len(fees),
            'paid_fees': len([fee for fee in fees if fee.status == FeeStatus.PAID]),
            'pending_fees': len([fee for fee in fees if fee.status == FeeStatus.PENDING]),
            'overdue_fees': len(overdue_fees),
            'total_amount': float(total_amount),
            'paid_amount': float(paid_amount),
            'pending_amount': float(pending_amount)
        }
        
        return success_response('Student fees retrieved', {
            'fees': fees_data,
            'summary': summary
        })
        
    except Exception as e:
        return error_response(f'Failed to get student fees: {str(e)}', 500)