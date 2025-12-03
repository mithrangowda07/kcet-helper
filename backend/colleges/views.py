from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import College, Branch, Cutoff, Category
from .serializers import (
    CollegeSerializer, CollegeDetailSerializer,
    BranchSerializer, CutoffSerializer, CategorySerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def college_list(request):
    colleges = College.objects.all()
    serializer = CollegeSerializer(colleges, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def college_detail(request, college_id):
    try:
        college = College.objects.prefetch_related('branch_set').get(college_id=college_id)
        serializer = CollegeDetailSerializer(college)
        return Response(serializer.data)
    except College.DoesNotExist:
        return Response({'error': 'College not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def branch_detail(request, unique_key):
    try:
        branch = Branch.objects.select_related('college', 'cluster').get(unique_key=unique_key)
        serializer = BranchSerializer(branch)
        return Response(serializer.data)
    except Branch.DoesNotExist:
        return Response({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def branches_by_college_code(request, college_code):
    """
    Return every branch for the supplied college_code. This is intended for
    the studying-student registration flow where users pick the college
    first (by code) and then need the corresponding branch list.
    """
    branches = Branch.objects.select_related('college', 'cluster').filter(
        college__college_code=college_code
    ).order_by('branch_name')
    
    serializer = BranchSerializer(branches, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def college_cutoff(request, college_id):
    try:
        college = College.objects.get(college_id=college_id)
        branches = Branch.objects.filter(college=college)
        cutoffs = Cutoff.objects.filter(unique_key__in=branches).select_related('unique_key')
        
        # Structure data for charts
        cutoff_data = {}
        for cutoff in cutoffs:
            branch_key = cutoff.unique_key.unique_key
            if branch_key not in cutoff_data:
                cutoff_data[branch_key] = {
                    'branch': BranchSerializer(cutoff.unique_key).data,
                    'categories': {}
                }
            
            category_data = {
                '2022': {
                    'r1': cutoff.cutoff_2022_r1,
                    'r2': cutoff.cutoff_2022_r2,
                    'r3': cutoff.cutoff_2022_r3,
                },
                '2023': {
                    'r1': cutoff.cutoff_2023_r1,
                    'r2': cutoff.cutoff_2023_r2,
                    'r3': cutoff.cutoff_2023_r3,
                },
                '2024': {
                    'r1': cutoff.cutoff_2024_r1,
                    'r2': cutoff.cutoff_2024_r2,
                    'r3': cutoff.cutoff_2024_r3,
                },
                '2025': {
                    'r1': cutoff.cutoff_2025_r1,
                    'r2': cutoff.cutoff_2025_r2,
                    'r3': cutoff.cutoff_2025_r3,
                },
            }
            cutoff_data[branch_key]['categories'][cutoff.category] = category_data
        
        return Response(cutoff_data)
    except College.DoesNotExist:
        return Response({'error': 'College not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def branch_cutoff(request, unique_key):
    try:
        branch = Branch.objects.get(unique_key=unique_key)
        cutoffs = Cutoff.objects.filter(unique_key=branch)
        
        # Get category filter from query params (optional)
        category_filter = request.GET.get('category', None)
        valid_categories = set()
        
        if category_filter:
            try:
                from .models import Category
                cat_obj = Category.objects.get(category=category_filter)
                # Parse fall_back: "1R,1G,GM" -> ["1R", "1G", "GM"]
                fall_back_list = [c.strip() for c in cat_obj.fall_back.split(',')]
                valid_categories = set(fall_back_list)
            except Category.DoesNotExist:
                valid_categories = {category_filter}
        
        cutoff_data = {
            'branch': BranchSerializer(branch).data,
            'categories': {}
        }
        
        for cutoff in cutoffs:
            # Filter by category if provided
            if category_filter and cutoff.category not in valid_categories:
                continue
            
            category_data = {
                '2022': {
                    'r1': cutoff.cutoff_2022_r1,
                    'r2': cutoff.cutoff_2022_r2,
                    'r3': cutoff.cutoff_2022_r3,
                },
                '2023': {
                    'r1': cutoff.cutoff_2023_r1,
                    'r2': cutoff.cutoff_2023_r2,
                    'r3': cutoff.cutoff_2023_r3,
                },
                '2024': {
                    'r1': cutoff.cutoff_2024_r1,
                    'r2': cutoff.cutoff_2024_r2,
                    'r3': cutoff.cutoff_2024_r3,
                },
                '2025': {
                    'r1': cutoff.cutoff_2025_r1,
                    'r2': cutoff.cutoff_2025_r2,
                    'r3': cutoff.cutoff_2025_r3,
                },
            }
            cutoff_data['categories'][cutoff.category] = category_data
        
        return Response(cutoff_data)
    except Branch.DoesNotExist:
        return Response({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    """
    Unified search endpoint for colleges and branches. When no query is
    provided we return the complete branch catalogue (with related college
    and cluster info) so the UI can bootstrap its search page without
    depending on the cutoff table.
    """
    query = request.GET.get('query', '').strip()
    
    colleges_qs = College.objects.all()
    branches_qs = Branch.objects.select_related('college', 'cluster')
    
    if query:
        college_filter = (
            Q(college_name__icontains=query) |
            Q(college_code__icontains=query) |
            Q(location__icontains=query)
        )
        branch_filter = (
            Q(branch_name__icontains=query) |
            Q(college__college_name__icontains=query) |
            Q(college__college_code__icontains=query) |
            Q(college__location__icontains=query)
        )
        colleges_qs = colleges_qs.filter(college_filter)
        branches_qs = branches_qs.filter(branch_filter)
    
    college_serializer = CollegeSerializer(colleges_qs, many=True)
    branch_serializer = BranchSerializer(branches_qs, many=True)
    
    return Response({
        'colleges': college_serializer.data,
        'branches': branch_serializer.data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    """Get all categories"""
    categories = Category.objects.all().order_by('category')
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

