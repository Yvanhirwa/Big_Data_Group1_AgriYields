# dashboard/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UploadFilesForm, PredictForm
from .ml.model import run_analysis
from .ml.train_model import train_and_save, load_model
from .utils.pdf_generator import generate_report_pdf
import pandas as pd, os, tempfile

def dashboard_home(request):
    # show simple metrics if available; placeholder zeros otherwise
    context = {"avg_temperature": 0, "avg_rainfall": 0, "avg_soil": 0, "yield_chart_url": "" }
    return render(request, "dashboard/dashboard.html", context)

def upload_and_run(request):
    if request.method == "POST":
        form = UploadFilesForm(request.POST, request.FILES)
        if form.is_valid():
            # Save uploaded files to media/uploads
            media_dir = os.path.join("media", "uploads")
            os.makedirs(media_dir, exist_ok=True)
            temp_path = os.path.join(media_dir, "temperature.csv")
            rain_path = os.path.join(media_dir, "rainfall.csv")
            moist_path = os.path.join(media_dir, "soil_moisture.csv")
            crop_path = os.path.join(media_dir, "crop_type.csv")
            with open(temp_path, "wb") as f:
                for chunk in request.FILES['temp_csv'].chunks():
                    f.write(chunk)
            with open(rain_path, "wb") as f:
                for chunk in request.FILES['rain_csv'].chunks():
                    f.write(chunk)
            with open(moist_path, "wb") as f:
                for chunk in request.FILES['moisture_csv'].chunks():
                    f.write(chunk)
            with open(crop_path, "wb") as f:
                for chunk in request.FILES['crop_csv'].chunks():
                    f.write(chunk)

            # Run analysis
            res = run_analysis(temp_path, rain_path, moist_path, crop_path,
                               num_regions=form.cleaned_data['num_regions'],
                               w1=form.cleaned_data['w1'],
                               w2=form.cleaned_data['w2'],
                               w3=form.cleaned_data['w3'],
                               quarter_choice=1)

            # Train model on the generated training dataframe
            training_df = res['training_df'].rename(columns={'Yield':'YieldIndex'})
            model_path = train_and_save(training_df.rename(columns={'YieldIndex':'Yield'}))  # train_and_save expects 'Yield'
            # small hack: ensure correct column names expected by train_and_save

            # render results
            context = {
                "stats": res['stats'],
                "yield_avg": res['yield_avg'],
                "plots": res['plots'],
                "corr": res['corr_rain_moist'],
            }
            request.session['last_results'] = {
                "stats": res['stats'],
                "yield_avg": res['yield_avg'],
                "plots": res['plots']
            }
            return render(request, "dashboard/results.html", context)
    else:
        form = UploadFilesForm()
    return render(request, "dashboard/upload.html", {"form": form})

def predict_view(request):
    form = PredictForm(request.POST or None)
    result = None
    if request.method == "POST" and form.is_valid():
        model = load_model()
        if not model:
            result = "Model not trained yet. Upload data and run analysis first."
        else:
            X = [[form.cleaned_data['temperature'], form.cleaned_data['rainfall'], form.cleaned_data['soil']]]
            pred = model.predict(X)[0]
            result = round(float(pred), 3)
    return render(request, "dashboard/predict.html", {"form": form, "result": result})

def export_pdf(request):
    last = request.session.get('last_results')
    if not last:
        return HttpResponse("No results available. Please run analysis first.")
    output_path = os.path.join("media", "AgriYield_Report.pdf")
    logo_path = os.path.join("dashboard", "static", "dashboard", "images", "logo.png")
    generate_report_pdf(output_path, last['stats'], last['yield_avg'], last['plots'], logo_path=logo_path)
    with open(output_path, "rb") as f:
        data = f.read()
    response = HttpResponse(data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="AgriYield_Report.pdf"'
    return response
