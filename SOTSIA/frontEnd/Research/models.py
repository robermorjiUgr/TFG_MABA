from django.db import models

# Experiments information.
class Experiment(models.Model):
    database = models.CharField(max_length=100)
    algorithm_group = models.CharField(max_length=100)
    algorithm_specific = models.CharField(max_length=100)
    start_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    duration = models.TimeField()
    author = models.CharField(max_length=100)

# Configuration of the Dataset
class DatasetConfiguration(models.Model):
    database = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    author = models.CharField(max_length=100)
    types_selected = models.TextField()         # Use ';' as delimiter

