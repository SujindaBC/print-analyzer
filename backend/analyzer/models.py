from django.db import models

class PDFUpload(models.Model):
    file = models.FileField(upload_to='pdf/')
    uploaded_at = models.DateTimeField(auto_now_add=True) 