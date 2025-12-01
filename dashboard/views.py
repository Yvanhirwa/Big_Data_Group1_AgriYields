# dashboard/views.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .forms import UploadFilesForm, PredictForm, SignUpForm
from .models import DataSet, RegionStats, AnalysisResult
from .ml.model import run_analysis
from .ml.train_model import train_and_save, load_model
from .utils.pdf_generator import generate_report_pdf
import pandas as pd, os, tempfile
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm

@login_required
def dashboard_home(request):
    latest_analysis = AnalysisResult.objects.first()
    latest_dataset = DataSet.objects.first()

    
    show_login = request.GET.get("login", "false") == "true"
    
    stats = []
    yield_avg = {}

    if latest_dataset:
        stats = list(latest_dataset.stats.all())
        yield_avg = {s.region: s.yield_index for s in stats}

    yield_avg_values = list(yield_avg.values())
    yield_avg_first = yield_avg_values[0] if yield_avg_values else None

    context = {
        "latest_analysis": latest_analysis,
        "stats": stats,
        "yield_avg": yield_avg,
        "yield_avg_values": yield_avg_values,
        "yield_avg_first": yield_avg_first,
        "datasets_count": DataSet.objects.count(),
        "analyses_count": AnalysisResult.objects.count(),
        "show_login": show_login,    
    }

    return render(request, "dashboard/dashboard.html", context)



@login_required
def upload_and_run(request):
    """Upload CSVs and run analysis"""
    if request.method == "POST":
        form = UploadFilesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save uploaded files to media/uploads
                media_dir = os.path.join("media", "uploads")
                os.makedirs(media_dir, exist_ok=True)
                
                temp_path = os.path.join(media_dir, "temperature.csv")
                rain_path = os.path.join(media_dir, "rainfall.csv")
                moist_path = os.path.join(media_dir, "soil_moisture.csv")
                crop_path = os.path.join(media_dir, "crop_type.csv")
                
                # Write files
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
                res = run_analysis(
                    temp_path, rain_path, moist_path, crop_path,
                    num_regions=form.cleaned_data['num_regions'],
                    w1=form.cleaned_data['w1'],
                    w2=form.cleaned_data['w2'],
                    w3=form.cleaned_data['w3'],
                    quarter_choice=1
                )

                # Create DataSet record
                dataset = DataSet.objects.create(
                    region=f"Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )

                # Save individual region stats
                for stat in res['stats']:
                    RegionStats.objects.create(
                        dataset=dataset,
                        region=stat['region'],
                        mean_temp=stat['mean_temp'],
                        mean_rain=stat['mean_rain'],
                        mean_moisture=stat['mean_moisture'],
                        yield_index=float(res['yield_avg'].get(stat['region'], 0)),
                        correlation=res['corr_rain_moist']
                    )

                # Save analysis result with plots
                analysis = AnalysisResult.objects.create(
                    dataset=dataset,
                    num_regions=form.cleaned_data['num_regions'],
                    w1=form.cleaned_data['w1'],
                    w2=form.cleaned_data['w2'],
                    w3=form.cleaned_data['w3'],
                    yield_chart=res['plots'].get('yield_chart', ''),
                    rain_trend=res['plots'].get('rain_trend', ''),
                    temp_trend=res['plots'].get('temp_trend', ''),
                    scatter_plot=res['plots'].get('scatter', ''),
                    heatmap=res['plots'].get('heatmap', ''),
                    correlation_rain_moisture=res['corr_rain_moist']
                )

                # Train model
                training_df = res['training_df'].copy()
                if 'Yield' not in training_df.columns:
                    training_df.rename(columns={'YieldIndex': 'Yield'}, inplace=True)
                train_and_save(training_df)

                messages.success(request, "Analysis completed successfully!")
                return redirect('results', analysis_id=analysis.id)

            except Exception as e:
                messages.error(request, f"Error during analysis: {str(e)}")
                return render(request, "dashboard/upload.html", {"form": form})
    else:
        form = UploadFilesForm()
    
    return render(request, "dashboard/upload.html", {"form": form})


@login_required
def results_view(request, analysis_id=None):
    """Display analysis results"""
    if analysis_id:
        analysis = get_object_or_404(AnalysisResult, id=analysis_id)
    else:
        analysis = AnalysisResult.objects.first()
        if not analysis:
            messages.warning(request, "No analysis results found. Please run analysis first.")
            return redirect('upload_and_run')
    
    stats = analysis.dataset.stats.all()
    
    context = {
        "analysis": analysis,
        "stats": list(stats),
        "plots": {
            "yield_chart": analysis.yield_chart,
            "rain_trend": analysis.rain_trend,
            "temp_trend": analysis.temp_trend,
            "scatter": analysis.scatter_plot,
            "heatmap": analysis.heatmap,
        },
        "yield_avg": {s.region: s.yield_index for s in stats},
        "correlation": analysis.correlation_rain_moisture,
    }
    return render(request, "dashboard/results.html", context)


@login_required
def predict_view(request):
    """AI Yield Prediction"""
    form = PredictForm(request.POST or None)
    result = None
    error = None
    
    if request.method == "POST" and form.is_valid():
        model = load_model()
        if not model:
            error = "Model not trained yet. Please upload data and run analysis first."
        else:
            try:
                X = [[
                    form.cleaned_data['temperature'],
                    form.cleaned_data['rainfall'],
                    form.cleaned_data['soil']
                ]]
                pred = model.predict(X)[0]
                result = round(float(pred), 3)
            except Exception as e:
                error = f"Prediction error: {str(e)}"
    
    return render(request, "dashboard/predict.html", {
        "form": form,
        "result": result,
        "error": error
    })


@login_required
def export_pdf(request, analysis_id=None):
    """Export analysis as PDF"""
    if analysis_id:
        analysis = get_object_or_404(AnalysisResult, id=analysis_id)
    else:
        analysis = AnalysisResult.objects.first()
        if not analysis:
            return HttpResponse("No analysis found.")
    
    stats = list(analysis.dataset.stats.all().values('region', 'mean_temp', 'mean_rain', 'mean_moisture'))
    yield_avg = {s.region: s.yield_index for s in analysis.dataset.stats.all()}
    
    plots_b64 = {
        'yield_chart': analysis.yield_chart,
        'rain_trend': analysis.rain_trend,
        'temp_trend': analysis.temp_trend,
        'scatter': analysis.scatter_plot,
        'heatmap': analysis.heatmap,
    }
    
    output_path = os.path.join("media", f"AgriYield_Report_{analysis.id}.pdf")
    logo_path = os.path.join("dashboard", "static", "dashboard", "images", "logo.png")
    
    generate_report_pdf(output_path, stats, yield_avg, plots_b64, logo_path=logo_path)
    
    with open(output_path, "rb") as f:
        data = f.read()
    
    response = HttpResponse(data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="AgriYield_Report_{analysis.id}.pdf"'
    return response


@login_required
def dataset_history(request):
    """View all datasets and analyses"""
    datasets = DataSet.objects.prefetch_related('stats', 'analysis').all()
    
    context = {
        "datasets": datasets,
        "total_datasets": datasets.count(),
    }
    return render(request, "dashboard/history.html", context)


@login_required
def delete_analysis(request, analysis_id):
    """Delete an analysis and associated data"""
    analysis = get_object_or_404(AnalysisResult, id=analysis_id)
    dataset = analysis.dataset
    dataset.delete()
    messages.success(request, "Analysis deleted successfully.")
    return redirect('dashboard_home')


def signup_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect("dashboard_home")

    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Account created successfully for {user.username}. You are now logged in.")
        return redirect("dashboard_home")
    
    return render(request, "dashboard/signup.html", {"form": form})




def login_view(request):
    """Handle login form submission and display login page."""
    
    # If the user is already authenticated, redirect to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard_home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # On successful login, redirect to the main dashboard
            return redirect('dashboard_home')
        else:
            # On failed login, show an error and re-render the login page
            messages.error(request, 'Invalid username or password. Please try again.')
            # Redirecting back to the login page ensures the URL is clean
            return redirect('login')
    
    # For a GET request, just render the page that contains the login form.
    return render(request, 'dashboard/login.html')


def logout_view(request):
    """Custom logout that handles both GET and POST"""
    logout(request)
    return redirect('dashboard_home')  # redirect to dashboard, modal shows for anonymous
