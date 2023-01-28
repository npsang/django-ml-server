from rest_framework import serializers
from .models import User, Document, Sentence, MLModel


class UserSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        # validated_data['documents'] = set(validated_data['documents'])
        documents = validated_data.pop('documents')
        user = User(**validated_data)
        
        user.set_password(validated_data['password'])
        user.save()
        return user
        # return super().create(validated_data)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username",
                "password", "email", "date_joined", "documents"]
        extra_kwargs = {
            'password': {'write_only': 'true'}
        }


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = '__all__'


class MLModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = MLModel
        fields = '__all__'
