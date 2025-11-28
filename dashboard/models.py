from django.db import models

class DataSet(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    region = models.CharField(max_length=100)
    temp_csv = models.FileField(upload_to="datasets/", null=True, blank=True)
    rainfall_csv = models.FileField(upload_to="datasets/", null=True, blank=True)
    soil_moisture_csv = models.FileField(upload_to="datasets/", null=True, blank=True)

    def __str__(self):
        return f"{self.region} - {self.uploaded_at}"


class RegionStats(models.Model):
    region = models.CharField(max_length=100)
    mean_temp = models.FloatField()
    mean_rain = models.FloatField()
    mean_moisture = models.FloatField()
    yield_index = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Stats for {self.region}"
