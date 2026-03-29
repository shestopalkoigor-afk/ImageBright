import os
from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_histogram_url(img):
    """Генерирует base64-строку графика распределения цветов."""
    plt.figure(figsize=(5, 3))
    colors = ('red', 'green', 'blue')
    for i, col in enumerate(colors):
        hist = img.histogram()[i*256:(i+1)*256]
        plt.plot(hist, color=col)
    plt.xlim([0, 256])
    plt.title("Распределение цветов")
    
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png', bbox_inches='tight')
    img_io.seek(0)
    plt.close()
    return base64.b64encode(img_io.getvalue()).decode('ascii')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        brightness = float(request.form.get('brightness', 1.0))
        
        if file:
            img = Image.open(file).convert('RGB')
            orig_hist = get_histogram_url(img)
            
            # Изменение яркости: 1.0 - оригинал, <1.0 - темнее, >1.0 - ярче
            enhancer = ImageEnhance.Brightness(img)
            res_img = enhancer.enhance(brightness)
            res_hist = get_histogram_url(res_img)
            
            save_path = os.path.join(UPLOAD_FOLDER, 'result.jpg')
            res_img.save(save_path)
            
            return render_template('index.html', result_img=save_path, 
                                   orig_hist=orig_hist, res_hist=res_hist)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
