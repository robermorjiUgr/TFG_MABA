from datetime import datetime
from django.db import models

# Configuration of the Dataset
class DatasetConfiguration(models.Model):
    database = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    author = models.CharField(max_length=100)
    types_selected = models.TextField()         # Use '; ' as delimiter
    created_at = models.DateTimeField(default=datetime.now, blank=True)    # For Research counter

# Experiments information.
class Experiment(models.Model):
    algorithm_group = models.CharField(max_length=100)
    algorithm_specific = models.CharField(max_length=100)
    start_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    duration = models.TimeField()
    dataset = models.ForeignKey(DatasetConfiguration, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=datetime.now, blank=True)    # For Research counter


