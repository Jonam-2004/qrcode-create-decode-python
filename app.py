from flask import Flask, render_template, request, send_file, url_for, redirect
import qrcode
import cv2
import os
from io import BytesIO

app = Flask(__name__)

# Create a directory for storing QR codes if it doesn't exist
if not os.path.isdir('static'):
    os.makedirs('static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_qr():
    url = request.form.get('url')
    img = qrcode.make(url)
    
    img_file = BytesIO()
    img.save(img_file, 'PNG')
    img_file.seek(0)

    img.save("static/qr_code.png")

    return send_file(img_file, mimetype='image/png')

@app.route('/download')
def download_qr():
    return send_file("static/qr_code.png", as_attachment=True, download_name="qr_code.png")

@app.route('/scan')
def scan_qr():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        _, frame = cap.read()
        data, bbox, _ = detector.detectAndDecode(frame)
        
        if data:
            cap.release()
            cv2.destroyAllWindows()
            return render_template('scan_result.html', url=data)

        cv2.imshow("QR Code Scanner", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_qr():
    if 'qrCodeImage' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['qrCodeImage']
    
    if file.filename == '':
        return redirect(url_for('index'))

    file_path = os.path.join('static', file.filename)
    file.save(file_path)

    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(cv2.imread(file_path))

    if data:
        os.remove(file_path) 
        print(data) 
        return render_template('scan_result.html', url=data) 
    
    os.remove(file_path)  
    return "No QR code found", 400

if __name__ == '__main__':
    app.run(debug=True)
