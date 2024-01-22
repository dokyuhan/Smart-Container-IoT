from flask import Flask, render_template, request
from twilio.rest import Client
import mysql.connector

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
@app.route('/sensor_data', methods=['POST']) #Pregunta para examen, cuantos metodos y cuales (DELETE, GET, POST, PUT)
def receive_sensor_data():

    if request.headers['Content-Type'] == 'application/json':

        data = request.json

        humidity = str(data.get('humidity'))
        temperature = str(data.get('temperature'))
        date_time = data.get('date_time')

        print(humidity)
        print(temperature)
        print(date_time)
        message = client.messages.create(
        from_='whatsapp:+14155238886',
        body='Humedad: '+humidity+" temperatura:"+temperature,
        to='whatsapp:+5215585735929'
        )
        print(message.sid)

        cnx, cursor = createConnection('sql3678877', 'sql3678877', 'gRuTQXqsSI', 'sql3.freemysqlhosting.net', '3306')   #conexion a la base de datos

        add_data = ("INSERT INTO dht_sensor_data (humidity, temperature, date_time) VALUES (%s, %s, %s)")  #inserta los queries a la base de datos
        
        cursor.execute(add_data, (humidity, temperature, date_time))  #ejecuta los queries hola
        cnx.commit()  #hace commit a la base de datos (guarda los datos a la base de datos)
        cursor.close()  #cierra el cursor
        cnx.close()  #cierra la conexion

        return 'Data received successfully.', 200
    else:
        return 'Invalid content type. Expected application/json.', 0

#solamente muestra la pagina web
@app.route("/")
def hello_world():
    message = client.messages.create(
    from_='whatsapp:+14155238886',   #whatsapp hello
    body='Servicio activado',
    to='whatsapp:+5215585735929'
    )
    print(message.sid)
    return render_template("index.html", title="Alumno", tamano="small" )

@app.route("/cafeteria")
def hello_world1():
    return render_template("cafeteria.html", title="Cafeteria")