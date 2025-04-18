import json
import base64
import fitz
from PIL import Image
import io
import traceback
import os
from tempfile import NamedTemporaryFile
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

def convert_pdf_to_gif(pdf_data, frame_rate=1, quality='medium'):
    try:
        # Decode base64 PDF data
        pdf_base64 = pdf_data.split(',')[1] if ',' in pdf_data else pdf_data
        pdf_bytes = base64.b64decode(pdf_base64)
        
        # Quality settings
        quality_settings = {
            'low': (800, 72),
            'medium': (1200, 150),
            'high': (2000, 300)
        }
        max_size, dpi = quality_settings.get(quality, quality_settings['medium'])
        
        # Create a temporary file for the PDF
        tmp_pdf_path = None
        try:
            with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                tmp_pdf.write(pdf_bytes)
                tmp_pdf_path = tmp_pdf.name

            # Open the PDF
            pdf_document = fitz.open(tmp_pdf_path)
            if pdf_document.page_count == 0:
                raise ValueError("PDF has no pages")
                
            # Convert pages to images
            images = []
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))  # Reduced scale
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Resize if needed
                if img.size[0] > max_size or img.size[1] > max_size:
                    ratio = min(max_size/img.size[0], max_size/img.size[1])
                    new_size = (int(img.size[0]*ratio), int(img.size[1]*ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                images.append(img)
                del pix  # Free up memory
                
            # Save as GIF with optimization
            output = io.BytesIO()
            if images:
                duration = int(1000 / frame_rate)
                images[0].save(
                    output,
                    format='GIF',
                    append_images=images[1:],
                    save_all=True,
                    duration=duration,
                    loop=0,
                    optimize=True,
                    quality=quality_settings[quality][1]  # Use DPI as quality
                )
            
            # Clean up images to free memory
            for img in images:
                img.close()
            images.clear()
            
            # Return base64 encoded GIF
            return base64.b64encode(output.getvalue()).decode('utf-8')
        finally:
            # Clean up
            if 'pdf_document' in locals():
                pdf_document.close()
            if tmp_pdf_path and os.path.exists(tmp_pdf_path):
                try:
                    os.unlink(tmp_pdf_path)
                except:
                    pass
            
    except Exception as e:
        raise Exception(f"Error converting PDF to GIF: {str(e)}")

def handle_request(request):
    """Vercel serverless function handler"""
    # Add CORS headers for all responses
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }

    # Handle OPTIONS request
    if request.get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    # Handle POST request
    if request.get('method') == 'POST':
        try:
            # Parse the request body
            body = json.loads(request.get('body', '{}'))
            
            # Get parameters
            pdf_data = body.get('pdfData')
            frame_rate = int(body.get('frameRate', 1))
            quality = body.get('quality', 'medium')
            
            if not pdf_data:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'error': 'No PDF data provided'
                    })
                }
            
            # Convert PDF to GIF
            gif_base64 = convert_pdf_to_gif(pdf_data, frame_rate, quality)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'gif': gif_base64
                })
            }
            
        except Exception as e:
            traceback_str = traceback.format_exc()
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': str(e),
                    'traceback': traceback_str
                })
            }
    
    # Handle unsupported methods
    return {
        'statusCode': 405,
        'headers': headers,
        'body': json.dumps({
            'success': False,
            'error': 'Method not allowed'
        })
    }

# Vercel requires a function named 'handler'
def handler(request):
    return handle_request(request) 