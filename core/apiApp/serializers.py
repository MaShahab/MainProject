from rest_framework import serializers
from apiApp.models import White_IPs
from rest_framework.serializers import (CharField)
from rest_framework.response import Response


class WhiteIpSerializer(serializers.ModelSerializer):

    # snippet = serializers.ReadOnlyField(source='get_snippet')
    # owner = serializers.ReadOnlyField(source='get_owner')

    class Meta:
        model = White_IPs
        fields = ['id', 'ip', 'created_at', 'updated_at']


    def create(self,validated_data):
        try:
            return White_IPs.objects.create(**validated_data)

        except Exception as e:
            pass

    def update(self,instance,validated_data):
        instance.ip = validated_data.get('ip', instance.ip)
        instance.save()
        return instance
    

class MyQueryParamSerializer(serializers.Serializer):
    link_url = serializers.CharField()
    tag_address = serializers.CharField(help_text="Please specify full tag address")
