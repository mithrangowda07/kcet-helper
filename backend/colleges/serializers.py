from rest_framework import serializers
from .models import College, Cluster, Branch, Cutoff, Category


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ['cluster_code', 'cluster_name']


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ['public_id', 'college_code', 'college_name', 'location','college_link']


class BranchSerializer(serializers.ModelSerializer):
    college = CollegeSerializer(read_only=True)
    cluster = ClusterSerializer(read_only=True)
    
    class Meta:
        model = Branch
        fields = ['public_id', 'college', 'cluster', 'branch_id', 'branch_name']


class CutoffSerializer(serializers.ModelSerializer):
    unique_key = BranchSerializer(read_only=True)
    
    class Meta:
        model = Cutoff
        fields = [
            'unique_key', 'category',
            'cutoff_2022_r1', 'cutoff_2022_r2', 'cutoff_2022_r3',
            'cutoff_2023_r1', 'cutoff_2023_r2', 'cutoff_2023_r3',
            'cutoff_2024_r1', 'cutoff_2024_r2', 'cutoff_2024_r3',
            'cutoff_2025_r1', 'cutoff_2025_r2', 'cutoff_2025_r3',
        ]


class CollegeDetailSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True, source='branch_set')
    
    class Meta:
        model = College
        fields = ['public_id', 'college_code', 'college_name', 'location', 'branches','college_link']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category', 'fall_back']

