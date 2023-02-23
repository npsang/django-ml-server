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
    en = 'en'
    vi = 'vi'
    LANGUAGE_TYPE_CHOICES = [
        (en, 'English'),
        (vi, 'Vietnamese')
    ]

    path = models.CharField(max_length=1000, null=True)
    url = models.URLField(max_length=1000,null=True,default='')

    name = models.CharField(max_length=1000)
    file_type = models.CharField(max_length=4, choices= FILE_TYPE_CHOICES, default=pdf)    
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='documents', default=None)
    language =models.CharField(max_length=16, choices=LANGUAGE_TYPE_CHOICES, null=True)
    pre_processing = models.BooleanField(default=False)
    
    is_vi_encode = models.BooleanField(default=False)
    vi_encode = models.BinaryField(editable=True, null=True) #np.array

    is_en_encode = models.BooleanField(default=False)
    en_encode = models.BinaryField(editable=True, null=True)

    is_cross_encode = models.BooleanField(default=False)
    cross_encode = models.BinaryField(editable=True, null=True)

class Sentence(ItemBase):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='sentences', null=True, default=None)
    content = models.CharField(max_length=5000)
    is_tokenized = models.BooleanField(default=False)
    content_tokenized = models.CharField(max_length=5000,null=True)

class MLModel(ItemBase):
    name = models.CharField(max_length=128)
    acronym = models.CharField(max_length=32, null=True)
    description = models.CharField(max_length=1000)
    version = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    