from django.db import models

# Create your models here.
    
class Login(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=20)

class Contribute(models.Model):
    ptype=models.CharField(max_length=122)
    psummary=models.CharField(max_length=122)
    pdescription=models.CharField(max_length=122)
    products=models.CharField(max_length=122)
    kanalysis=models.CharField(max_length=122)
    kinsisghts=models.CharField(max_length=122)
    tags=models.CharField(max_length=122)
    owner=models.CharField(max_length=122)
    # kNo=models.IntegerField()

    def __str__(self):
        return self.owner