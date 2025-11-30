# dashboard/utils/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from datetime import datetime
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def _to_imagereader(source):
    """
    Accepts:
      - filesystem path (str)
      - base64 string (str)
      - bytes or BytesIO
    Returns an ImageReader or raises an informative error.
    """
    if source is None:
        return None

    # filesystem path
    if isinstance(source, str) and os.path.exists(source):
        return ImageReader(source)

    # base64 string (data URL or plain base64)
    if isinstance(source, str):
        # strip data URL prefix if present
        if source.startswith('data:'):
            source = source.split(',', 1)[1]
        try:
            decoded = base64.b64decode(source)
            return ImageReader(io.BytesIO(decoded))
        except Exception as e:
            raise ValueError(f"Invalid base64 image data: {e}")

    # bytes or file-like
    if isinstance(source, (bytes, bytearray)):
        return ImageReader(io.BytesIO(source))
    if hasattr(source, 'read'):
        # file-like object
        data = source.read()
        if isinstance(data, str):
            data = data.encode()
        return ImageReader(io.BytesIO(data))

    raise ValueError("Unsupported image source type for PDF generator")

def generate_report_pdf(output_path, stats, yield_avg, plots_b64, logo_path=None):
    """
    Simple PDF writer that places logo, a table of stats and embedded plots.
    - output_path: full path where PDF will be written
    - stats: list/dict of stats (used for text)
    - yield_avg: dict or mapping of yield averages
    - plots_b64: dict with keys like 'yield_chart','rain_trend','temp_trend' containing base64 strings or paths
    - logo_path: optional filesystem path or base64 string
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin

    # Logo
    try:
        logo_ir = _to_imagereader(logo_path)
        if logo_ir:
            iw, ih = logo_ir.getSize()
            max_w = 120
            ratio = ih / iw if iw else 1
            c.drawImage(logo_ir, margin, y - 40, width=max_w, height=max_w * ratio, preserveAspectRatio=True, mask='auto')
    except Exception:
        # don't fail PDF generation on logo problems
        pass

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin + 140, y - 10, "AgriYield — Analysis Report")
    c.setFont("Helvetica", 10)
    c.drawString(margin + 140, y - 30, "")

    y = y - 120

    # Stats text
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Region statistics:")
    c.setFont("Helvetica", 10)
    y -= 18
    for s in stats:
        line = f"{s.get('region','N/A')}: Temp={s.get('mean_temp','N/A')}, Rain={s.get('mean_rain','N/A')}, Soil={s.get('mean_moisture','N/A')}, Yield={s.get('yield_index','N/A')}"
        c.drawString(margin, y, line)
        y -= 14
        if y < 150:
            c.showPage()
            y = height - margin

    # Plots
    y -= 10
    for key in ('yield_chart', 'temp_trend', 'rain_trend', 'scatter', 'heatmap'):
        img_data = plots_b64.get(key) if plots_b64 else None
        if not img_data:
            continue
        try:
            ir = _to_imagereader(img_data)
            # place image full-width with max height
            img_w = width - 2 * margin
            img_h = img_w * 0.45
            if y - img_h < margin:
                c.showPage()
                y = height - margin
            c.drawImage(ir, margin, y - img_h, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')
            y -= img_h + 12
        except Exception:
            # skip invalid images
            continue

    c.showPage()
    c.save()
    return output_path
