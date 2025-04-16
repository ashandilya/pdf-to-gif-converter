from http.server import BaseHTTPRequestHandler
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
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            tmp_pdf_path = tmp_pdf.name
        
        try:
            # Open the PDF
            pdf_document = fitz.open(tmp_pdf_path)
            if pdf_document.page_count == 0:
                raise ValueError("PDF has no pages")
                
            # Convert pages to images
            images = []
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Resize if needed
                if img.size[0] > max_size or img.size[1] > max_size:
                    ratio = min(max_size/img.size[0], max_size/img.size[1])
                    new_size = (int(img.size[0]*ratio), int(img.size[1]*ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                images.append(img)
                
            # Save as GIF
            output = io.BytesIO()
            if images:
                duration = int(1000 / frame_rate)  # Convert fps to milliseconds
                images[0].save(
                    output,
                    format='GIF',
                    append_images=images[1:],
                    save_all=True,
                    duration=duration,
                    loop=0,
                    optimize=True
                )
            
            # Return base64 encoded GIF
            return base64.b64encode(output.getvalue()).decode('utf-8')
        finally:
            # Clean up
            if 'pdf_document' in locals():
                pdf_document.close()
            if os.path.exists(tmp_pdf_path):
                os.unlink(tmp_pdf_path)
            
    except Exception as e:
        raise Exception(f"Error converting PDF to GIF: {str(e)}")

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length)
            body = json.loads(request_body.decode('utf-8'))
            
            # Get parameters
            pdf_data = body.get('pdfData')
            frame_rate = int(body.get('frameRate', 1))
            quality = body.get('quality', 'medium')
            
            if not pdf_data:
                self.send_error_response(400, 'No PDF data provided')
                return
            
            # Convert PDF to GIF
            gif_base64 = convert_pdf_to_gif(pdf_data, frame_rate, quality)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                'success': True,
                'gif': gif_base64
            }
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def send_error_response(self, status_code, error_message):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_data = {
            'success': False,
            'error': error_message,
            'traceback': traceback.format_exc()
        }
        self.wfile.write(json.dumps(error_data).encode('utf-8'))

def handler(request, context):
    """Vercel serverless function handler"""
    if request['method'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if request['method'] == 'POST':
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
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': False,
                        'error': 'No PDF data provided'
                    })
                }
            
            # Convert PDF to GIF
            gif_base64 = convert_pdf_to_gif(pdf_data, frame_rate, quality)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'success': True,
                    'gif': gif_base64
                })
            }
            
        except Exception as e:
            traceback_str = traceback.format_exc()
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({
                    'success': False,
                    'error': str(e),
                    'traceback': traceback_str
                })
            }
    
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'error': 'Method not allowed'
        })
    } 