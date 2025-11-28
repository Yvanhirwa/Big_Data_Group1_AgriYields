# dashboard/utils/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from datetime import datetime

def generate_report_pdf(output_path, stats, yield_avg, plots_b64, logo_path=None):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = []

    # Header with logo
    if logo_path and os.path.exists(logo_path):
        elems.append(Image(logo_path, width=120, height=60))
    elems.append(Paragraph("AgriYield - Model Report", styles["Title"]))
    elems.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elems.append(Spacer(1,12))

    # Stats table
    data = [["Region", "Mean Temp (°C)", "Mean Rain (mm/day)", "Mean Moisture (%)"]]
    for row in stats:
        data.append([row['region'], f"{row['mean_temp']:.2f}", f"{row['mean_rain']:.2f}", f"{row['mean_moisture']:.2f}"])
    t = Table(data, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0), colors.lightgrey),
        ('GRID',(0,0),(-1,-1), 0.5, colors.grey),
    ]))
    elems.append(t)
    elems.append(Spacer(1,12))

    # Yield table
    yield_data = [["Region","Avg Yield Index"]]
    for k,v in yield_avg.items():
        yield_data.append([k, f"{v:.3f}"])
    t2 = Table(yield_data, hAlign='LEFT')
    t2.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
    elems.append(t2)
    elems.append(Spacer(1,12))

    # Add images: convert base64 to Image by writing to temp files (ReportLab Image expects a filename)
    import base64, tempfile
    for key, b64 in plots_b64.items():
        imgdata = base64.b64decode(b64)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(imgdata)
        tmp.flush()
        tmp.close()
        elems.append(Image(tmp.name, width=400, height=250))
        elems.append(Spacer(1,12))

    # Footer (simple)
    elems.append(Paragraph("RAB-style AgriYield - generated report", styles["Normal"]))

    doc.build(elems)
    return output_path
