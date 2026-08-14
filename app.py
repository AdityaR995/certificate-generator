from flask import Flask, render_template, request
import pandas as pd
import mysql.connector
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

# MySQL connection
conn = mysql.connector.connect(
    host=os.environ.get('MYSQLHOST'),
    user=os.environ.get('MYSQLUSER'),
    password=os.environ.get('MYSQLPASSWORD'),
    database=os.environ.get('MYSQLDATABASE'),
    port=int(os.environ.get('MYSQLPORT'))
)

cursor = conn.cursor()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['csvfile']
    df = pd.read_csv(file)

    generated_files = []

    os.makedirs("generated", exist_ok=True)

    for index, row in df.iterrows():
        name = row['name']

        cursor.execute(
            'INSERT INTO participants(name) VALUES (%s)',
            (name,)
        )

        img = Image.open('certificate_templates/template.png')
        draw = ImageDraw.Draw(img)

        font = ImageFont.load_default()

        x = 500
        y = 300
        draw.text((x, y), name, fill="black", font=font)
        output_path = f"generated/{name}.png"
        img.save(output_path)

        generated_files.append(output_path)

    conn.commit()

    return (
        '<h2>Certificates Generated Successfully!</h2><br><br>'
        + '<br>'.join(generated_files)
    )

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )