from flask import Flask, render_template, request
import pandas as pd
import mysql.connector
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import qrcode

app = Flask(__name__)

conn = mysql.connector.connect(
    host=os.environ.get('MYSQLHOST', 'localhost'),
    user=os.environ.get('MYSQLUSER', 'root'),
    password=os.environ.get('MYSQLPASSWORD', 'Root@1234'),
    database=os.environ.get('MYSQLDATABASE', 'certificate_db'),
    port=int(os.environ.get('MYSQLPORT', 3306))
)

cursor = conn.cursor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/verify/<certificate_id>')
def verify(certificate_id):
    cursor.execute(
        'SELECT name FROM participants WHERE certificate_id = %s',
        (certificate_id,)
    )
    result = cursor.fetchone()

    if result:
        return f'''
        <h1>Certificate Verified ✅</h1>
        <p><b>Name:</b> {result[0]}</p>
        <p><b>Certificate ID:</b> {certificate_id}</p>
        '''
    else:
        return '<h1>Invalid Certificate ❌</h1>'

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['csvfile']
    df = pd.read_csv(file)

    generated_files = []

    os.makedirs("generated", exist_ok=True)

    for index, row in df.iterrows():
        name = row['name']
        certificate_id = str(uuid.uuid4())[:8]

        if index == 0:
            title = "1st Place"
        elif index == 1:
            title = "2nd Place"
        elif index == 2:
            title = "3rd Place"
        else:
            title = None

        cursor.execute(
            'INSERT INTO participants(name, certificate_id) VALUES (%s, %s)',
            (name, certificate_id)
        )

        img = Image.open('certificate_templates/template.png')
        draw = ImageDraw.Draw(img)

        font_name = ImageFont.truetype(
            'fonts/DejaVuSans-Bold.ttf', 70
        )
        font_title = ImageFont.truetype(
            'fonts/DejaVuSans-Bold.ttf', 40
        )
        small_font = ImageFont.truetype(
            'fonts/DejaVuSans-Bold.ttf', 18
        )

        img_width, img_height = img.size

        bbox = draw.textbbox((0, 0), name, font=font_name)
        text_width = bbox[2] - bbox[0]

        x = (img_width - text_width) // 2
        y = 470

        draw.text((x, y), name, fill="black", font=font_name)

        if title:
            bbox2 = draw.textbbox((0, 0), title, font=font_title)
            title_width = bbox2[2] - bbox2[0]

            title_x = (img_width - title_width) // 2
            title_y = 560

            draw.text(
                (title_x, title_y),
                title,
                fill="darkblue",
                font=font_title
            )

        verify_url = (
            f"http://127.0.0.1:5000/verify/{certificate_id}"
        )

        qr = qrcode.make(verify_url)
        qr = qr.resize((120, 120))

        img.paste(qr, (img_width - 150, img_height - 150))

        draw.text(
            (40, img_height - 50),
            f"ID: {certificate_id}",
            fill="black",
            font=small_font
        )

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