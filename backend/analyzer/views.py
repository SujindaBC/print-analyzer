from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from .models import PDFUpload
from .serializers import PDFUploadSerializer
import fitz
from PIL import Image
import io
import os

class PDFUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = PDFUploadSerializer(data=request.data)
        if file_serializer.is_valid():
            try:
                file_instance = file_serializer.save()
                file_path = os.path.join(settings.MEDIA_ROOT, str(file_instance.file.name))
                results = analyze_pdf(file_path)
                os.remove(file_path)
                return Response({"results": results}, status=200)
            except Exception as e:
                return Response({"error": str(e)}, status=500)
        else:
            return Response(file_serializer.errors, status=400)

def analyze_pdf(file_path):
    doc = fitz.open(file_path)
    results = {}

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))

        black_ink_usage, color_ink_usage = calculate_ink_usage(img)
        price = calculate_price(black_ink_usage, color_ink_usage)
        results[page_num + 1] = {"black_ink_usage": black_ink_usage, "color_ink_usage": color_ink_usage, "price": price}
    return results

def is_grayscale(img):
    img = img.convert("RGB")
    width, height = img.size
    for x in range(width):
        for y in range(height):
            r, g, b = img.getpixel((x, y))
            if r != g or g != b:
                return False
    return True

def calculate_ink_usage(img):
    img = img.convert("RGB")
    width, height = img.size
    total_pixels = width * height
    black_pixels = 0
    color_pixels = 0

    for x in range(width):
        for y in range(height):
            r, g, b = img.getpixel((x, y))
            if r == g == b:
                if r != 255:  # Ignore white pixels
                    black_pixels += 1
            else:
                color_pixels += 1

    black_ink_usage = (black_pixels / total_pixels) * 100
    color_ink_usage = (color_pixels / total_pixels) * 100
    return black_ink_usage, color_ink_usage

def calculate_price(black_ink, color_ink):
    if black_ink > 0:
        if black_ink < 25:
            black_price = 2
        elif black_ink < 50:
            black_price = 3
        elif black_ink < 75:
            black_price = 4
        else:
            black_price = 5
    else:
        black_price = 0

    if color_ink > 0:
        if color_ink < 20:
            color_price = 2
        elif color_ink < 50:
            color_price = 3
        else:
            color_price = 4
    else:
        color_price = 0

    return black_price + color_price