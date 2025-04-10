# PDF to GIF Converter

A web-based tool that converts PDF documents into animated GIFs. Built with Python and JavaScript.

## Features

- Drag and drop PDF upload
- PDF preview
- Adjustable frame rate and quality settings
- Real-time GIF preview
- Download converted GIFs
- Responsive design

## Tech Stack

- Frontend:
  - HTML5
  - CSS3
  - JavaScript (ES6+)
  - PDF.js for PDF rendering

- Backend:
  - Python
  - PyMuPDF for PDF processing
  - Pillow for image processing
  - Vercel for deployment

## Setup

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-to-gif-converter.git
cd pdf-to-gif-converter
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
python server.py
```

4. Open `http://localhost:8000` in your browser

### Quick Start

For Windows users, simply run:
```bash
start.bat
```

This will:
- Check Python installation
- Install dependencies
- Start the server
- Open the application in your default browser

### Deployment

The application is configured for deployment on Vercel:

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

## Usage

1. Open the application in your browser
2. Drop a PDF file or click to select one
3. Adjust the frame rate and quality settings
4. Click "Convert to GIF"
5. Download the converted GIF

## Limitations

- Free tier limitations on Vercel:
  - Maximum file size: 50MB
  - Function execution time: 10 seconds
  - Memory: 1024MB

## License

MIT License - feel free to use this project for any purpose.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Try it out

You can try the PDF to GIF Converter live by visiting the deployed application on Vercel. Simply upload a PDF, adjust the settings, and convert it to a GIF in real-time.

[Visit the PDF to GIF Converter](https://your-vercel-app-name.vercel.app)

---

git pull origin main --rebase