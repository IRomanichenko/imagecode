
from flask import Flask, request, jsonify, send_file, send_from_directory
import time

import barcode
from pdf import get_pdfinfo_fromfiles, get_page, get_page_filename

from string import Template

app = Flask(__name__)

users = []
messages = []


@app.route("/")
def hello():
    return """Используйте //recognize/<filenames> with | as a path separator"""


@app.route("/status")
def status():
    return {"status": True}

#получить картинку из указанного файла в каталоге /app/doc/
#http://localhost:5000/page/schet-2017-05-04.pdf/1
@app.route("/page/<string:strfilename>/<int:pagenum>", methods=["GET"])
def page(strfilename, pagenum):
    filename = "/app/doc/"+strfilename.replace("|", "/")
    return send_file(get_page_filename(filename, pagenum))

#получить штрихкод из указанного файла в каталоге /app/doc/
#http://localhost:5000/decode_ean13/schet-2017-05-04.pdf/1
@app.route("/decode_ean13/<string:strfilename>/<int:pagenum>", methods=["GET"])
def decode_ean13(strfilename, pagenum):
    filename = "/app/doc/"+strfilename.replace("|", "/")
    imagefilename = get_page_filename(filename, pagenum)
    decoded = barcode.decode_ean13(imagefilename)
    return jsonify(decoded)

# recognize barcode from first page of pdf file or from image,
# accepts file data or file path, accessible by local network
#http://localhost:5000/pdfinfo/schet-2017-05-04.pdf
@app.route("/pdfinfo/<string:strfilenames>", methods=["GET"])
def pdfinfo(strfilenames):
    app.logger.debug('pdfinfo')
    filenames = "/app/doc/"+strfilenames.split(",")
    newfilenames = []
    for filename in filenames:
        newfilenames.append(filename.replace("|", "/"))
    if request.method == "GET":
        info = get_pdfinfo_fromfiles(newfilenames)
        return jsonify(info), 200
    else:
        return {"method": "Unsupported"}

# recognize barcode from first page of pdf file or from image,
# accepts file data or file path, accessible by local network
@app.route("/recognize/<string:strfilenames>", methods=["GET"])
def recognize(strfilenames):
    app.logger.debug('recognize')
    filenames = "/app/doc/"+strfilenames.split(",")
    newfilenames = []
    for filename in filenames:
        newfilenames.append(filename.replace("|", "/"))
    if request.method == "GET":
        print(request.json)
        return {"method": "GET", "filename": newfilenames[0]}
    else:
        return {"method": "Unsupported"}


@app.route("/pdf2images", methods=["GET", "POST"])
def pdf2images():
    return {"method": "Not implemented"}

#http://localhost:5000/upload
@app.route('/upload', methods=['POST'])
def upload_file():
    # Получаем файл из запроса
    file = request.files['file']
    # Проверяем, что файл не пустой
    if file.filename == '':
        return 'не выбран файл', 400
    # Проверяем, что файл является PDF
    if not file.filename.endswith('.pdf'):
        return 'неверный тип файла', 400
    MAX_FILE_SIZE = 1024  *  1024  *  10  # 10 МБ
    if file.content_length > MAX_FILE_SIZE:
        msg = Template('размер файла превышает $sz МБ')
        return msg.substitute(sz=MAX_FILE_SIZE), 413  
    # Загружаем файл на сервер
    file.save('/app/doc/' + file.filename)
    msg = Template('Файл $fl загружен.')
    return msg.substitute(fl=file.filename), 200


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('uploads', filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

#app.run()







