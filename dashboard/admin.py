from django.contrib import admin
from .models import DataSet, RegionStats, AnalysisResult

@admin.register(DataSet)
class DataSetAdmin(admin.ModelAdmin):
    list_display = ['region', 'uploaded_at']
    search_fields = ['region']
    list_filter = ['uploaded_at']

@admin.register(RegionStats)
class RegionStatsAdmin(admin.ModelAdmin):
    list_display = ['region', 'dataset', 'mean_temp', 'yield_index', 'created_at']
    list_filter = ['region', 'created_at']
    search_fields = ['region']

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'dataset', 'num_regions', 'correlation_rain_moisture', 'created_at']
    list_filter = ['created_at', 'num_regions']
    readonly_fields = ['created_at']
