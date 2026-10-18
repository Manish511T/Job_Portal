from rest_framework import serializers
from .models import Company

class CompanyMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'location']
