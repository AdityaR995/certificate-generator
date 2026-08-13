from flask import Flask, render_template, request
import pandas as pd
import mysql.connector
from PIL import Image, ImageDraw, ImageFont
import os
app = Flask(__name__)
# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Root@1234',   # put your MySQL password here
    database='certificate_db'
)
cursor = conn.cursor()
# Home page
@app.route('/')
def home():
    return render_template('index.html')
# Upload CSV and generate certificates
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['csvfile']
    # Read CSV
    df = pd.read_csv(file)
    generated_files = []
    for index, row in df.iterrows():
        name = row['name']
        # Save name to MySQL
        cursor.execute(
            'INSERT INTO participants(name) VALUES (%s)',
            (name,)
        )
        # Open certificate template
        img = Image.open('certificate_templates/template.png')
        draw = ImageDraw.Draw(img)
        # Big font
        font = ImageFont.truetype('arial.ttf', 70)
        # Put participant name near the center
        draw.text((800, 530), name, fill='black', font=font)
        # Save certificate
        filename = name.replace(' ', '_') + '.png'
        output_path = os.path.join('generated', filename)
        img.save(output_path)
        generated_files.append(filename)
    conn.commit()
    return '<h2>Certificates Generated Successfully!</h2><br><br>' + '<br>'.join(generated_files)
if __name__ == '__main__':
    app.run(debug=True)