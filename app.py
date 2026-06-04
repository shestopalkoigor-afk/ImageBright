from flask import Flask, render_template, request, send_file, url_for
from PIL import Image, ImageEnhance, ImageDraw, ImageFont 
import numpy as np
import matplotlib.pyplot as plt
import io
import os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB максимальный размер файла
# Создаем папку для загрузок если ее нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
def adjust_brightness(image_array, brightness_level):
    """
    Изменяет яркость изображения
    brightness_level: -100 до +100 (проценты)
    """
    # Нормализуем уровень яркости от -1.0 до +1.0
    brightness_factor = brightness_level / 100.0
    # Преобразуем в float для точных вычислений
    image_float = image_array.astype(np.float32)
    # Применяем изменение яркости
    if brightness_factor >= 0:
        # Увеличение яркости
        adjusted_image = image_float + (255 * brightness_factor)
    else:
        # Уменьшение яркости
        adjusted_image = image_float * (1 + brightness_factor)
    # Ограничиваем значения от 0 до 255
    adjusted_image = np.clip(adjusted_image, 0, 255)
    return adjusted_image.astype(np.uint8)
def create_histogram(image_array, title, filename):
    
    # Создает гистограмму распределения цветов
    plt.figure(figsize=(10, 6))
    # Разделяем на каналы RGB
    colors = ('red', 'green', 'blue')
    channel_names = ('Red', 'Green', 'Blue')
    
    for i, color in enumerate(colors):
        histogram, bins = np.histogram(image_array[:,:,i].flatten(), 256, [0,256])
        plt.plot(bins[:-1], histogram, color=color, alpha=0.7, label=channel_names[i])
    
    plt.title(f'Гистограмма цветов - {title}', fontsize=14)
    plt.xlabel('Значение интенсивности')
    plt.ylabel('Количество пикселей')
    plt.legend()
    plt.grid(True, alpha=0.3)
    # Сохраняем гистограмму
    plt.tight_layout()
    plt.savefig(filename, dpi=100, bbox_inches='tight')
    plt.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    try:
        # Проверяем загружен ли файл
        if 'image' not in request.files:
            return render_template('index.html', error='Файл не выбран')
        
        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', error='Файл не выбран')
        
        # Получаем уровень яркости
        brightness_level = int(request.form.get('brightness', 0))
        # Ограничиваем диапазон яркости
        brightness_level = max(-100, min(100, brightness_level))
        # Загружаем изображение
        image = Image.open(file.stream)
        # Конвертируем в RGB если нужно
        if image.mode != 'RGB':
            image = image.convert('RGB')
        # Преобразуем в numpy array
        img_array = np.array(image)
        # Создаем уникальные имена файлов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = f'original_{timestamp}.png'
        processed_filename = f'processed_{timestamp}.png'
        original_hist_filename = f'hist_original_{timestamp}.png'
        processed_hist_filename = f'hist_processed_{timestamp}.png'
        
        # Сохраняем оригинальное изображение
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        image.save(original_path)
        # Создаем гистограмму для оригинального изображения
        original_hist_path = os.path.join(app.config['UPLOAD_FOLDER'], original_hist_filename)
        create_histogram(img_array, 'Исходное изображение', original_hist_path)
        # Изменяем яркость
        processed_array = adjust_brightness(img_array, brightness_level)
        res_img = Image.fromarray(processed_array)
        
        # Добавляем чекбокс даты и времени
        add_timestamp = request.form.get('add_timestamp') == 'on'
        if add_timestamp:
            draw = ImageDraw.Draw(res_img)
            text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Безопасно загружаем шрифт
            try:
                font = ImageFont.truetype("arial.ttf", 178)
            except IOError:
                font = ImageFont.load_default()
            
            # Наносим текст на изображение (с черной обводкой для читаемости)
            draw.text((40, 40), text, font=font, fill="white", stroke_width=20, stroke_fill="black")
            
        # Сохраняем обработанное изображение
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        res_img.save(processed_path)
        # Создаем гистограмму для обработанного изображения
        processed_hist_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_hist_filename)
        create_histogram(processed_array, 'Измененная яркость', processed_hist_path)
        
        # Формируем URL для изображений
        original_url = url_for('static', filename=f'uploads/{original_filename}')
        processed_url = url_for('static', filename=f'uploads/{processed_filename}')
        original_hist_url = url_for('static', filename=f'uploads/{original_hist_filename}')
        processed_hist_url = url_for('static', filename=f'uploads/{processed_hist_filename}')
        
        return render_template('index.html',
                             original_image=original_url,
                             res_img=processed_url,
                             original_histogram=original_hist_url,
                             processed_histogram=processed_hist_url,
                             brightness_level=brightness_level)
    
    except Exception as e:
        return render_template('index.html', error=f'Ошибка обработки: {str(e)}')
@app.route('/cleanup', methods=['POST'])
def cleanup():
        # Очистка загруженных файлов
    try:
        upload_folder = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return 'Файлы очищены'
    except Exception as e:
        return f'Ошибка очистки: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)