from rest_framework import serializers
from .models import User, Document, Sentence, MLModel


class UserSerializer(serializers.ModelSerializer):
    documents = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ["username", "documents"]


class ListDocumentSerializer(serializers.ModelSerializer):
    # sentences = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def create(self, validated_data):
        document = Document(**validated_data)
        document.save()
        return document.id, document

    class Meta:
        model = Document
        fields = ["id", "path", "url", "name", "file_type",
                "user", "pre_processing",
                'language', 'is_vi_encode',
                'is_en_encode',
                'is_cross_encode',]

class DocumentSerializer(serializers.ModelSerializer):
    sentences = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def create(self, validated_data):
        document = Document(**validated_data)
        document.save()
        return document.id, document

    class Meta:
        model = Document
        fields = ["id", "path", "url", "name", "file_type",
                "user", "pre_processing",
                'language', 'is_vi_encode', 'vi_encode',
                'is_en_encode', 'en_encode',
                'is_cross_encode', 'cross_encode', 'sentences']


class SentenceSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):
        sentence = Sentence(**validated_data)
        sentence.save()
        return sentence.id

    class Meta:
        model = Sentence
        fields = ["id", "document", "content",
                "is_tokenized", "content_tokenized"]


class MLModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = MLModel
        fields = '__all__'
