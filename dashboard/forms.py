# dashboard/forms.py
from django import forms
from .models import DataSet

class UploadFilesForm(forms.Form):
    num_regions = forms.IntegerField(min_value=1, max_value=10, initial=5, label="Number of Regions")
    w1 = forms.FloatField(min_value=0, max_value=1, initial=0.4, label="Weight 1 (Temperature)")
    w2 = forms.FloatField(min_value=0, max_value=1, initial=0.5, label="Weight 2 (Rainfall)")
    w3 = forms.FloatField(min_value=0, max_value=1, initial=0.1, label="Weight 3 (Soil Moisture)")
    
    temp_csv = forms.FileField(label="Temperature CSV")
    rain_csv = forms.FileField(label="Rainfall CSV")
    moisture_csv = forms.FileField(label="Soil Moisture CSV")
    crop_csv = forms.FileField(label="Crop Type CSV")


class PredictForm(forms.Form):
    temperature = forms.FloatField(label="Temperature (°C)", min_value=-50, max_value=60)
    rainfall = forms.FloatField(label="Rainfall (mm/day)", min_value=0, max_value=500)
    soil = forms.FloatField(label="Soil Moisture (%)", min_value=0, max_value=100)
