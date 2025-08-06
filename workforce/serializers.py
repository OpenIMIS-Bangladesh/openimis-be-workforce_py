from rest_framework import serializers
from workforce.models import WorkforceDocumentType


class WorkforceDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkforceDocumentType
        fields = '__all__'
