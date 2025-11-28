# dashboard/forms.py
from django import forms

class UploadFilesForm(forms.Form):
    temp_csv = forms.FileField(label="Temperature CSV")
    rain_csv = forms.FileField(label="Rainfall CSV")
    moisture_csv = forms.FileField(label="Soil Moisture CSV")
    crop_csv = forms.FileField(label="Crop Type CSV")
    num_regions = forms.IntegerField(initial=5, min_value=1, max_value=20)

    # weights
    w1 = forms.FloatField(initial=0.4)
    w2 = forms.FloatField(initial=0.5)
    w3 = forms.FloatField(initial=0.1)

class PredictForm(forms.Form):
    region = forms.ChoiceField(choices=[('Region A','Region A'),('Region B','Region B'),('Region C','Region C'),('Region D','Region D'),('Region E','Region E')])
    temperature = forms.FloatField()
    rainfall = forms.FloatField()
    soil = forms.FloatField()
