from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q

from .models import College, Branch, Cutoff, Category, Cluster
from .serializers import (
    CollegeSerializer,
    CollegeDetailSerializer,
    BranchSerializer,
    CutoffSerializer,
    CategorySerializer,
    ClusterSerializer,
)
from .branch_insights_service import get_branch_insights


@api_view(['GET'])
@permission_classes([AllowAny])
def college_list(request):
    colleges = College.objects.all()
    serializer = CollegeSerializer(colleges, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def college_detail(request, public_id):
    try:
        college = College.objects.prefetch_related('branch_set').get(public_id=public_id)
        serializer = CollegeDetailSerializer(college)
        return Response(serializer.data)
    except College.DoesNotExist:
        return Response({'error': 'College not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def branch_detail(request, public_id):
    try:
        branch = Branch.objects.select_related('college', 'cluster').get(public_id=public_id)
        serializer = BranchSerializer(branch)
        return Response(serializer.data)
    except Branch.DoesNotExist:
        return Response({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def branches_by_college_code(request, college_code):
    """
    Return every branch for the supplied college_code.
    """
    branches = Branch.objects.select_related('college', 'cluster').filter(
        college__college_code=college_code
    ).order_by('branch_name')

    serializer = BranchSerializer(branches, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def college_cutoff(request, public_id):
    try:
        college = College.objects.get(public_id=public_id)
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
def branch_cutoff(request, public_id):
    try:
        branch = Branch.objects.get(public_id=public_id)
        cutoffs = Cutoff.objects.filter(unique_key=branch)

        # Get category filter from query params (optional)
        category_filter = request.GET.get('category', None)
        valid_categories = set()

        if category_filter:
            try:
                cat_obj = Category.objects.get(category=category_filter)
                # Parse fall_back: "1R,1G,GM" -> ["1R", "1G", "GM"]
                fall_back_list = [c.strip() for c in cat_obj.fall_back.split(',') if c.strip()]
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
    Unified search endpoint for colleges and branches.
    Returns:
      - colleges: serialized college objects (filtered by query & location if provided)
      - branches: serialized branch objects (filtered by query & location if provided)
      - locations: unique sorted list of locations from College table for dropdown
    """
    query = request.GET.get('query', '').strip()
    location = request.GET.get('location', '').strip()  # NEW: location param

    colleges_qs = College.objects.all()
    branches_qs = Branch.objects.select_related('college', 'cluster')

    # filter by query (if provided)
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

    # filter by location (if provided, exact or case-insensitive)
    if location:
        colleges_qs = colleges_qs.filter(location__iexact=location)
        # also filter branches by parent college location
        branches_qs = branches_qs.filter(college__location__iexact=location)

    # get unique locations for the dropdown (sorted)
    locations = list(
        College.objects
               .exclude(location__isnull=True)
               .exclude(location__exact='')
               .values_list('location', flat=True)
               .distinct()
               .order_by('location')
    )

    college_serializer = CollegeSerializer(colleges_qs, many=True)
    branch_serializer = BranchSerializer(branches_qs, many=True)

    return Response({
        'colleges': college_serializer.data,
        'branches': branch_serializer.data,
        'locations': locations,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def locations_list(request):
    """
    Lightweight endpoint that returns the unique list of non-empty locations.
    Frontend should call this to populate the location dropdown.
    """
    locations = list(
        College.objects
               .exclude(location__isnull=True)
               .exclude(location__exact='')
               .values_list('location', flat=True)
               .distinct()
               .order_by('location')
    )
    return Response({'locations': locations})


@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    """Get all categories"""
    categories = Category.objects.all().order_by('category')
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def cluster_list(request):
    """Get all clusters"""
    clusters = Cluster.objects.all().order_by('cluster_code')
    serializer = ClusterSerializer(clusters, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def branch_insights(request):
    """
    Return AI-generated, web-searched insights for a specific college + branch.

    Expected JSON body:
    {
        "college_name": "R. V. College of Engineering",
        "branch_name": "Computer Science and Engineering"
    }
    """
    data = request.data or {}
    college_name = (data.get('college_name') or '').strip()
    branch_name = (data.get('branch_name') or '').strip()

    if not college_name or not branch_name:
        return Response(
            {
                'error': 'college_name and branch_name are required.',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        insights = get_branch_insights(college_name=college_name, branch_name=branch_name)
    except RuntimeError as exc:
        return Response(
            {
                'error': str(exc),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception:
        # Avoid leaking internal errors to clients
        return Response(
            {
                'error': 'Unable to fetch branch insights at the moment. Please try again later.',
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(insights, status=status.HTTP_200_OK)