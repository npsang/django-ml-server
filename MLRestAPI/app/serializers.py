from rest_framework import serializers
from .models import User, Document, Sentence, MLModel


class UserSerializer(serializers.ModelSerializer):
    documents = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    def create(self, validated_data):
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
    sentences = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def create(self, validated_data):
        document = Document(**validated_data)
        document.save()
        return document.id, document

    class Meta:
        model = Document
        fields = ["id", "document", "url", "name", "file_type",
                "user", "pre_processing", "content", "sentences"]


class SentenceSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        sentence = Sentence(**validated_data)
        sentence.save()
        return sentence.id

    class Meta:
        model = Sentence
        fields = '__all__'


class MLModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = MLModel
        fields = '__all__'
