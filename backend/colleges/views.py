from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import College, Branch, Cutoff
from .serializers import (
    CollegeSerializer, CollegeDetailSerializer,
    BranchSerializer, CutoffSerializer
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
        
        cutoff_data = {
            'branch': BranchSerializer(branch).data,
            'categories': {}
        }
        
        for cutoff in cutoffs:
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
    query = request.GET.get('query', '').strip()
    
    if not query:
        return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Search in colleges
    colleges = College.objects.filter(
        Q(college_name__icontains=query) |
        Q(college_code__icontains=query) |
        Q(location__icontains=query)
    )
    
    # Search in branches
    branches = Branch.objects.filter(
        Q(branch_name__icontains=query) |
        Q(college__college_name__icontains=query) |
        Q(college__college_code__icontains=query) |
        Q(college__location__icontains=query)
    ).select_related('college', 'cluster')
    
    college_serializer = CollegeSerializer(colleges, many=True)
    branch_serializer = BranchSerializer(branches, many=True)
    
    return Response({
        'colleges': college_serializer.data,
        'branches': branch_serializer.data,
    })

