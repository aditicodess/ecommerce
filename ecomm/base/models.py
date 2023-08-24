from django.db import models
import uuid



class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True , editable=False , default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now= True)
    updated_at = models.DateTimeField(auto_now_add= True)

    class Meta:
        abstract = True 


## if we give models.Model within in a class in djangi then it is taken a db table in django so 
## if we use meta tag absttract = true then django dont take it as model intead take it as a class.