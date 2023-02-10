from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    pass


class ItemBase(models.Model):
    class Meta:
        abstract = True
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)


class Document(ItemBase):
    pdf = 'pdf'
    docx = 'docx'
    txt = 'txt'
    FILE_TYPE_CHOICES = [
        (pdf, 'PDF'),
        (docx, 'Docx'),
        (txt, 'Txt')
    ]

    document = models.CharField(max_length=255, null=True)
    url = models.URLField()
    name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=4, choices= FILE_TYPE_CHOICES, default=pdf)
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='documents', default=None)
    pre_processing = models.BooleanField(default=False)


class Sentence(ItemBase):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='sentences', null=True, default=None)
    content = models.CharField(max_length=1000)
    is_tokenized = models.BooleanField(default=False)
    content_tokenized = models.CharField(max_length=1000,null=True)
    is_encode = models.BooleanField(default=False)
    encode = models.BinaryField(editable=True) #np.array


class MLModel(ItemBase):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1000)
    version = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    