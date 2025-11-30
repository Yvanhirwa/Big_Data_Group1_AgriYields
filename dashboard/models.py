from django.db import models

class DataSet(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    region = models.CharField(max_length=100)
    temp_csv = models.FileField(upload_to="datasets/", null=True, blank=True)
    rainfall_csv = models.FileField(upload_to="datasets/", null=True, blank=True)
    soil_moisture_csv = models.FileField(upload_to="datasets/", null=True, blank=True)
    crop_csv = models.FileField(upload_to="datasets/", null=True, blank=True)

    def __str__(self):
        return f"{self.region} - {self.uploaded_at}"


class RegionStats(models.Model):
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name='stats', null=True, blank=True)
    region = models.CharField(max_length=100)
    mean_temp = models.FloatField()
    mean_rain = models.FloatField()
    mean_moisture = models.FloatField()
    yield_index = models.FloatField()
    correlation = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Stats for {self.region} - {self.created_at.date() if self.created_at else 'N/A'}"


class AnalysisResult(models.Model):
    dataset = models.OneToOneField(DataSet, on_delete=models.CASCADE, related_name='analysis')
    num_regions = models.IntegerField(default=5)
    w1 = models.FloatField(default=0.4)
    w2 = models.FloatField(default=0.5)
    w3 = models.FloatField(default=0.1)
    
    # Store base64 encoded plots
    yield_chart = models.TextField(null=True, blank=True)
    rain_trend = models.TextField(null=True, blank=True)
    temp_trend = models.TextField(null=True, blank=True)
    scatter_plot = models.TextField(null=True, blank=True)
    heatmap = models.TextField(null=True, blank=True)
    
    correlation_rain_moisture = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Analysis - {self.created_at.date()}"
