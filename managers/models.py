from django.db import models

MAX_NAME_LENGTH = 128


class Project(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    start_date = models.DateTimeField(auto_now_add=True)
    stop_date = models.DateTimeField(null=True, blank=True, )
    terminated = models.BooleanField(default=False)
    # managers = models.ManyToManyField(CustomUser, on_delete=models.CASCADE)
    # members = models.ManyToManyField(CustomUser, on_delete=models.CASCADE)
