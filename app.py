from flask import Flask, jsonify, render_template, request
from twilio.rest import Client
import mysql.connector
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
from io import BytesIO
import base64

#credenciales para el acceso al cliente 
account_sid = 'AC19c841aa09fb5083ae45d96139fa8db1'
auth_token = 'e551e93c1bd2b2f59e32a54811b29e68'
client = Client(account_sid, auth_token)

app = Flask(__name__)


def createConnection(user_name, database_name, user_password, host, port):  #crear una conexion con los parametros de la base de datos
    cnx = mysql.connector.connect(
        user=user_name, database=database_name, password=user_password, host=host, port=port)
    cursor = cnx.cursor()
    return (cnx, cursor)

#esta ruta solamente recibimos datos del emulador virtual
@app.route('/sensor_bote', methods=['POST'])
def receive_sensor_bote():
    
    if request.headers['Content-Type'] == 'application/json':

        capacidad = request.json
        porcentaje = request.json

        mexico_tz = pytz.timezone('America/Mexico_City')
        now_utc = datetime.utcnow()
        now_mexico = now_utc.replace(tzinfo=pytz.utc).astimezone(mexico_tz)
        date_time = now_mexico.strftime("%m/%d/%Y, %H:%M:%S")

        capacidad = int(capacidad.get('capacidad'))
        porcentaje = int(porcentaje.get('porcentaje'))

        print(capacidad)
        print(porcentaje)
        print(date_time)

        if porcentaje in (95, 96, 97, 98, 99, 100):
            message = client.messages.create(
            from_='whatsapp:+14155238886',
            body='El bote esta lleno' ' ,Capacidad: '+ str(capacidad)+ ' ,Porcentaje: ' + str(porcentaje)+' % \nFecha y hora: ' +date_time,
            to='whatsapp:+5215585735929'
            )
            print(message.sid)

        cnx, cursor = createConnection('sql3678877', 'sql3678877', 'gRuTQXqsSI', 'sql3.freemysqlhosting.net', '3306')   #conexion a la base de datos

        add_data = ("INSERT INTO sensor_bote (capacidad, porcentaje, date_time) VALUES (%s, %s, %s)")  #inserta los queries a la base de datos
        
        cursor.execute(add_data, (capacidad, porcentaje, date_time))  #ejecuta los queries
        cnx.commit()  #hace commit a la base de datos (guarda los datos a la base de datos)
        cursor.close()  #cierra el cursor
        cnx.close()  #cierra la conexion 
        
        response_data = {'message': 'Data received successfully'}
        return jsonify(response_data), 200
    else:
        response_data = {'status': 'error', 'message': 'Invalid content type. Expected application/json.'}
        return jsonify(response_data), 0
    
#crea las graficas en base a la base de datos SQL
@app.route("/grafica", methods=['GET'])
def graph():
        # Create a connection to the database
    cnx, cursor = createConnection('sql3678877', 'sql3678877', 'gRuTQXqsSI', 'sql3.freemysqlhosting.net', '3306')

    # Query the database
    query = ("SELECT * FROM sensor_bote")

    # Execute the query
    cursor.execute(query)

    # Get the data
    data = cursor.fetchall()   #fetchall() obtiene todos los datos de la base de datos

    # Cierra la conexión
    cursor.close()
    cnx.close()

    capacidades = [item[2] for item in data]
    dates = [datetime.strptime(item[3], "%m/%d/%Y, %H:%M:%S").strftime("%H:%M") for item in data]

    #date_time = [item[3] for item in data]

    #Datos para la grafica de barras
    plt.figure(figsize=(12, 4))
    plt.plot(dates, capacidades, label = 'capacidad')
    plt.xlabel('Time')
    plt.ylabel('Capacidad (%)')
    plt.title('Capacidad vs. Tiempo')
    plt.legend()

    # Guardar la gráfica en un archivo temporal
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)                                           
    img_data = base64.b64encode(img.getvalue()).decode()   #decodifica la imagen a base 64

    last_data = capacidades[-1]
    empty_percentage = 100 - last_data

    # Datos para la gráfica de pie
    sizes = [last_data, empty_percentage]
    labels = ['Lleno', 'Vacio']

    # Plotting the Pie Chart
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff'])
    plt.legend()

    # Guardar la gráfica en un archivo temporal
    img2 = BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)                                           
    img_data2 = base64.b64encode(img2.getvalue()).decode()   #decodifica la imagen a base 64

    # Regresa los datos de la imagen
    return img_data, img_data2

#solamente muestra la pagina web
@app.route("/", methods=['GET'])
def contenedores():
    return render_template('main.html',tamano = "small")

@app.route("/contenedor_1", methods=['GET'])
def contenedor_1():
    #trae los datos de la imgane de la grafica
    img_data, img_data2 = graph()
    return render_template('Contenedor1.html', img_data2 = img_data2 ,tamano = "small")

@app.route("/agregar", methods=['GET'])
def agregar():
    img_data, img_data2 = graph()
    return render_template('agregar.html',img_data = img_data, tamano = "small")
