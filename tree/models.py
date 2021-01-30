from django.db import models

class ProjectParts(models.Model):
    part = models.TextField(unique=True)
    prt_class = models.TextField(null=True)
    mat_desc = models.TextField(null=True)