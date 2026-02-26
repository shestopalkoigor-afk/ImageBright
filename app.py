from flask import Flask, request, render_template
from PIL import ImageEnhance, Image
import numpy as np
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    image_file = request.files['image']
    brightness_value = float(request.form['brightness'])

    # Обработка изображения и изменения яркости
    image = Image.open(image_file)
    enhancer = ImageEnhance.Brightness(image)
    bright_image = enhancer.enhance(brightness_value)

    # Визуализация гистограмм
    original_colors = get_color_distribution(image)
    bright_colors = get_color_distribution(bright_image)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    plot_histogram(original_colors, 'Original Image', ax=axes[0])
    plot_histogram(bright_colors, 'Brightened Image', ax=axes[1])
    
    # Преобразование графика в изображение
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close()
    image_data = img_buf.getbuffer()

    return f'<img src="data:image/png;base64,{image_data.decode()}" alt="Histograms">'

def get_color_distribution(image):
    # Функция для подсчета распределения цветов
    pass

def plot_histogram(colors, title, ax):
    # Функция для построения гистограммы
    pass

if __name__ == '__main__':
    app.run(debug=True) 