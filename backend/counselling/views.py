from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from students.models import Student
from colleges.models import Cutoff, Category, Branch
from .models import CounsellingChoice
from .serializers import CounsellingChoiceSerializer, CounsellingChoiceCreateSerializer
from .utils import get_recommendations


def _get_cutoff_rank(student, branch, year='2025', round_name='r1'):
    """
    Resolve cutoff rank for a branch using student's category with fallbacks.
    Returns an integer rank if available, else None.
    """
    cutoff_field = f'cutoff_{year}_{round_name}'

    categories_to_try = []
    if student.category:
        try:
            cat_obj = Category.objects.get(category=student.category)
            categories_to_try = [student.category] + [
                c.strip() for c in cat_obj.fall_back.split(',') if c.strip()
            ]
        except Category.DoesNotExist:
            categories_to_try = [student.category]

    if 'GM' not in categories_to_try:
        categories_to_try.append('GM')

    for cat in categories_to_try:
        cutoff_obj = Cutoff.objects.filter(unique_key=branch, category=cat).first()
        if not cutoff_obj:
            continue
        value = getattr(cutoff_obj, cutoff_field, None)
        if value in [None, '', 'NA', '-', 'nan']:
            continue
        try:
            return int(value)
        except (ValueError, TypeError):
            continue
    return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommendations(request):
    """
    Get rank-based recommendations for counselling students.
    Body: { kcet_rank, category?, year?, opening_rank?, closing_rank? }
    """
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can access recommendations'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    kcet_rank = request.data.get('kcet_rank')
    if not kcet_rank:
        # Use student's saved rank
        kcet_rank = student.kcet_rank
    
    if not kcet_rank:
        return Response(
            {'error': 'kcet_rank is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    category = request.data.get('category')
    year = request.data.get('year', '2025')
    opening_rank = request.data.get('opening_rank')
    closing_rank = request.data.get('closing_rank')
    
    # Convert to integers if provided
    if opening_rank is not None:
        try:
            opening_rank = int(opening_rank)
        except (ValueError, TypeError):
            opening_rank = None
    if closing_rank is not None:
        try:
            closing_rank = int(closing_rank)
        except (ValueError, TypeError):
            closing_rank = None
    
    recommendations_list = get_recommendations(kcet_rank, category, year, opening_rank, closing_rank)
    
    return Response({
        'kcet_rank': kcet_rank,
        'category': category,
        'year': year,
        'opening_rank': opening_rank,
        'closing_rank': closing_rank,
        'recommendations': recommendations_list,
        'count': len(recommendations_list),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def choices_list(request):
    """Get all counselling choices for the logged-in student with cutoff information"""
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can access choices'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    choices = CounsellingChoice.objects.filter(
        student_user_id=student
    ).order_by('order_of_list').select_related('unique_key__college', 'unique_key__cluster')
    
    serializer = CounsellingChoiceSerializer(choices, many=True)
    choices_data = serializer.data
    
    # Get user's category and fallback categories
    user_category = student.category
    valid_categories = set()
    if user_category:
        try:
            cat_obj = Category.objects.get(category=user_category)
            fall_back_list = [c.strip() for c in cat_obj.fall_back.split(',')]
            valid_categories = set(fall_back_list)
        except Category.DoesNotExist:
            valid_categories = {user_category} if user_category else set()
    
    # Add cutoff information for each choice
    year = request.GET.get('year', '2025')
    round_name = request.GET.get('round', 'r1')
    cutoff_field = f'cutoff_{year}_{round_name}'
    
    for choice_data in choices_data:
        unique_key_str = choice_data['unique_key']  # This is a string
        cutoff_value = None
        
        # Get the Branch object
        try:
            branch = Branch.objects.get(unique_key=unique_key_str)
        except Branch.DoesNotExist:
            choice_data['cutoff'] = None
            continue
        
        # Try to find cutoff for user's category or fallback categories
        if valid_categories:
            for cat in valid_categories:
                try:
                    cutoff = Cutoff.objects.get(unique_key=branch, category=cat)
                    cutoff_value = getattr(cutoff, cutoff_field, None)
                    if cutoff_value:
                        break
                except Cutoff.DoesNotExist:
                    continue
        
        # If no cutoff found, try GM as fallback
        if not cutoff_value:
            try:
                cutoff = Cutoff.objects.get(unique_key=branch, category='GM')
                cutoff_value = getattr(cutoff, cutoff_field, None)
            except Cutoff.DoesNotExist:
                pass
        
        choice_data['cutoff'] = cutoff_value
    
    return Response(choices_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def choices_create(request):
    """Add a new counselling choice"""
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can create choices'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = CounsellingChoiceCreateSerializer(data=request.data)
    if serializer.is_valid():
        unique_key = serializer.validated_data['unique_key']

        # avoid duplicates
        if CounsellingChoice.objects.filter(student_user_id=student, unique_key=unique_key).exists():
            return Response(
                {'error': 'This branch is already in your choices'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # fetch existing choices ordered
            existing_choices = list(
                CounsellingChoice.objects.filter(student_user_id=student)
                .order_by('order_of_list')
                .select_related('unique_key')
            )

            new_rank = _get_cutoff_rank(student, unique_key, '2025', 'r1')
            insert_position = len(existing_choices) + 1

            for idx, choice in enumerate(existing_choices, start=1):
                existing_rank = _get_cutoff_rank(student, choice.unique_key, '2025', 'r1')

                if new_rank is None:
                    # If we don't have rank info, place after ranked items but before other unknowns
                    if existing_rank is None:
                        insert_position = idx
                        break
                    continue

                if existing_rank is None or new_rank <= existing_rank:
                    insert_position = idx
                    break

            # shift orders to make room
            for choice in reversed(existing_choices):
                if choice.order_of_list >= insert_position:
                    choice.order_of_list += 1
                    choice.save(update_fields=['order_of_list'])

            choice = CounsellingChoice.objects.create(
                student_user_id=student,
                unique_key=unique_key,
                order_of_list=insert_position
            )

        return Response(CounsellingChoiceSerializer(choice).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def choices_update(request, choice_id):
    """Update order_of_list for a counselling choice"""
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can update choices'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        choice = CounsellingChoice.objects.get(choice_id=choice_id, student_user_id=student)
    except CounsellingChoice.DoesNotExist:
        return Response(
            {'error': 'Choice not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    new_order = request.data.get('order_of_list')
    if new_order is None:
        return Response(
            {'error': 'order_of_list is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if new order is already taken
    existing = CounsellingChoice.objects.filter(
        student_user_id=student,
        order_of_list=new_order
    ).exclude(choice_id=choice_id).first()
    
    if existing:
        return Response(
            {'error': f'Order {new_order} is already taken'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    choice.order_of_list = new_order
    choice.save()
    
    return Response(CounsellingChoiceSerializer(choice).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def choices_delete(request, choice_id):
    """Delete a counselling choice"""
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can delete choices'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        choice = CounsellingChoice.objects.get(choice_id=choice_id, student_user_id=student)
        choice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except CounsellingChoice.DoesNotExist:
        return Response(
            {'error': 'Choice not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def choices_bulk_update(request):
    """Bulk update order_of_list for multiple choices"""
    from django.db import transaction
    
    student = request.user
    
    if student.type_of_student != 'counselling':
        return Response(
            {'error': 'Only counselling students can update choices'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Expecting: { "choices": [{"choice_id": 1, "order_of_list": 1}, ...] }
    # Handle both dict and list formats
    if isinstance(request.data, list):
        choices_data = request.data
    else:
        choices_data = request.data.get('choices', [])
    
    if not choices_data or not isinstance(choices_data, list):
        return Response(
            {'error': 'choices array is required', 'received': type(request.data).__name__},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            # First, set all orders to negative values to avoid conflicts
            for item in choices_data:
                choice_id = item.get('choice_id')
                if choice_id is None:
                    continue
                try:
                    choice = CounsellingChoice.objects.get(
                        choice_id=choice_id,
                        student_user_id=student
                    )
                    choice.order_of_list = -(abs(choice.order_of_list))
                    choice.save()
                except CounsellingChoice.DoesNotExist:
                    continue
            
            # Now update to the new orders
            for item in choices_data:
                choice_id = item.get('choice_id')
                new_order = item.get('order_of_list')
                
                if choice_id is None or new_order is None:
                    continue
                
                try:
                    choice = CounsellingChoice.objects.get(
                        choice_id=choice_id,
                        student_user_id=student
                    )
                    choice.order_of_list = new_order
                    choice.save()
                except CounsellingChoice.DoesNotExist:
                    continue
        
        # Return updated choices with cutoff info
        choices = CounsellingChoice.objects.filter(
            student_user_id=student
        ).order_by('order_of_list').select_related('unique_key__college', 'unique_key__cluster')
        
        serializer = CounsellingChoiceSerializer(choices, many=True)
        choices_data = serializer.data
        
        # Add cutoff information (same logic as choices_list)
        user_category = student.category
        valid_categories = set()
        if user_category:
            try:
                cat_obj = Category.objects.get(category=user_category)
                fall_back_list = [c.strip() for c in cat_obj.fall_back.split(',')]
                valid_categories = set(fall_back_list)
            except Category.DoesNotExist:
                valid_categories = {user_category} if user_category else set()
        
        year = request.data.get('year', '2025')
        round_name = request.data.get('round', 'r1')
        cutoff_field = f'cutoff_{year}_{round_name}'
        
        for choice_data in choices_data:
            unique_key_str = choice_data['unique_key']
            cutoff_value = None
            
            try:
                branch = Branch.objects.get(unique_key=unique_key_str)
            except Branch.DoesNotExist:
                choice_data['cutoff'] = None
                continue
            
            if valid_categories:
                for cat in valid_categories:
                    try:
                        cutoff = Cutoff.objects.get(unique_key=branch, category=cat)
                        cutoff_value = getattr(cutoff, cutoff_field, None)
                        if cutoff_value:
                            break
                    except Cutoff.DoesNotExist:
                        continue
            
            if not cutoff_value:
                try:
                    cutoff = Cutoff.objects.get(unique_key=branch, category='GM')
                    cutoff_value = getattr(cutoff, cutoff_field, None)
                except Cutoff.DoesNotExist:
                    pass
            
            choice_data['cutoff'] = cutoff_value
        
        return Response(choices_data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
