from flask import Flask, render_template, request
import pandas as pd
import mysql.connector
from PIL import Image, ImageDraw, ImageFont
import os
conn = mysql.connector.connect(
    host=os.environ.get('MYSQLHOST'),
    user=os.environ.get('MYSQLUSER'),
    password=os.environ.get('MYSQLPASSWORD'),
    database=os.environ.get('MYSQLDATABASE'),
    port=int(os.environ.get('MYSQLPORT'))
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))