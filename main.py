from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
import json
from waitress import serve
from flask_jwt_extended import create_access_token, verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
import datetime
import requests
import re

app = Flask(__name__)
cors = CORS(app)
app.config['JWT_SECRET_KEY'] = '*#m1S1oNTI3*'
jwt = JWTManager(app)

@app.route("/", methods=['GET'])
def test():
    json = {}
    json['mensaje'] = "Servidor corriendo..."
    return jsonify(json)
@app.route("/login", methods =['POST'])
def crear_token():
    datos = request.get_json()
    url = dataConfig["url-microservicio-seguridad"]+'/usuarios/login'
    headers = {"Content-Type":"application/json; charset = utf-8"}
    respuesta = requests.post(url, json = datos, headers=headers)
    if respuesta.status_code == 200:
        usuario = respuesta.json()
        vigencia = datetime.timedelta(hours = 1)
        access_token = create_access_token(identity=usuario,expires_delta=vigencia)
        return jsonify({"token":access_token, "user_id":usuario["_id"]})
    else:
        return jsonify({"mensaje":"Credenciales incorrectas"}),401

def validarPermiso(endpoint, metodo, idRol):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-seguridad"]+'/permisos-rol/validar-permiso/rol/'+idRol
    infoPermiso = {
        "url":endpoint,
        "metodo":metodo
    }
    tienePermiso = False
    respuesta = requests.get(url, json = infoPermiso, headers=headers)
    try:
        datos = respuesta.json()
        if "_id" in datos:
            tienePermiso= True
    except:
        pass
    return tienePermiso


def reemplazarEnUrl(url): #/estudiantes/jgjgjg55g5g5g -> /estudiantes/?
    partes = url.split("/") #/estudiantes/jgjgjg55g5g5g -> ['estudiantes','jgjgjg55g5g5g']
    for i in partes:
       if re.search('\\d',i):
           url = url.replace(i, '?') #/estudiantes/?
    return url

@app.before_request
def before_request_callback():
    endpoint = reemplazarEnUrl(request.path)
    rutasSinPermiso = ["/login"]
    if rutasSinPermiso.__contains__(endpoint):
        pass
    elif verify_jwt_in_request():
        usuario = get_jwt_identity()
        if usuario['rol'] is not None:
            tienePermiso = validarPermiso(endpoint, request.method,usuario['rol']['_id'])
            if not tienePermiso:
                return jsonify({"mensaje":"Permiso denegado"}), 401
        else:
            return jsonify({"mensaje": "Permiso denegado"}), 401

#####CONEXIÓN MS ACADÉMICO Y APIGATEWAY
#####SERVICIOS MÓDULO ESTUDIANTES
@app.route("/estudiantes",methods=['POST'])
def CrearEstudiante():
    datos = request.get_json()
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"]+'/estudiantes'
    respuesta = requests.post(url, json = datos, headers=headers)
    return jsonify(respuesta.json())

@app.route("/estudiantes",methods=['GET'])
def ObtenerEstudiantes():
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/estudiantes'
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())

@app.route("/estudiantes/<string:id>", methods=['GET'])
def ObtenerEstudiante(id):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/estudiantes/'+id
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())

@app.route("/estudiantes/<string:id>", methods=['PUT'])
def ActualizarEstudiante(id):
    datos = request.get_json()
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/estudiantes/'+id
    respuesta = requests.put(url, json = datos, headers=headers)
    return jsonify(respuesta.json())

@app.route("/estudiantes/<string:id>", methods = ['DELETE'])
def EliminarEstudiante(id):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/estudiantes/' + id
    respuesta = requests.delete(url, headers=headers)
    return jsonify(respuesta.json())

#EXPONIENDO FUNCIONALIDADES DEPARTAMENTOS API GATEWAY
@app.route("/departamentos",methods=['POST'])
def crearDepartamento():
    datosDepartamento = request.get_json()
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/departamentos'
    respuesta = requests.post(url, json=datosDepartamento, headers=headers)
    return jsonify(respuesta.json())

@app.route("/departamentos",methods=['GET'])
def mostrarDepartamentos():
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/departamentos'
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())
@app.route("/departamentos/<string:id>",methods=['GET'])
def mostrarDepartamento(id):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/departamentos/'+id
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())

@app.route("/departamentos/<string:id>", methods=['PUT'])
def actualizarDepartamento(id):
    datosDepartamento = request.get_json()
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/departamentos/' + id
    respuesta = requests.put(url, json= datosDepartamento, headers=headers)
    return jsonify(respuesta.json())
@app.route("/departamentos/<string:id>", methods=['DELETE'])
def eliminarDepartamento(id):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/departamentos/' + id
    respuesta = requests.delete(url, headers=headers)
    return jsonify(respuesta.json())

#EXPONIENDO FUNCIONALIDADES MATERIAS API GATEWAY
@app.route("/materias",methods=['POST'])
def crearMateria():
    datosMateria = request.get_json()
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/materias'
    respuesta = requests.post(url, json=datosMateria, headers=headers)
    return jsonify(respuesta.json())

@app.route("/materias",methods=['GET'])
def mostrarMaterias():
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/materias'
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())

@app.route("/materias/<string:id>",methods=['GET'])
def mostrarMateria(id):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/materias/'+id
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())

@app.route("/materias/<string:id>",methods=['PUT'])
def actualizarMateria(id):
    datosMateria = request.get_json()
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/materias/' + id
    respuesta = requests.put(url, json= datosMateria, headers=headers)
    return jsonify(respuesta.json())

@app.route("/materias/<string:id>",methods=['DELETE'])
def eliminarMateria(id):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/materias/' + id
    respuesta = requests.delete(url, headers=headers)
    return jsonify(respuesta.json())
@app.route("/materias/<string:id>/departamento/<string:id_departamento>",methods=['PUT'])
def asignarMateria(id, id_departamento):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/materias/' + id+'/departamento/'+id_departamento
    respuesta = requests.put(url, headers=headers)
    return jsonify(respuesta.json())

#EXPONIENDO FUNCIONALIDADES INSCRIPCIONES API GATEWAY
@app.route("/inscripciones/estudiante/<string:id_estudiante>/materia/<string:id_materia>",methods=['POST'])
def crearInscripcion(id_estudiante, id_materia):
    datosInscripcion = request.get_json()
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/inscripciones/estudiante/'+id_estudiante+'/materia/'+id_materia
    respuesta = requests.post(url, json=datosInscripcion, headers=headers)
    return jsonify(respuesta.json())

@app.route("/inscripciones",methods=['GET'])
def mostrarInscripciones():
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/inscripciones'
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())

@app.route("/inscripciones/<string:id>",methods = ['GET'])
def mostrarInscripcion(id):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/inscripciones/'+id
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())

@app.route("/inscripciones/<string:id>/estudiante/<string:id_estudiante>/materia/<string:id_materia>",methods = ['PUT'])
def actualizarInscripcion(id,id_estudiante,id_materia):
    datosInscripcion = request.get_json()
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/inscripciones/'+id+'/estudiante/'+id_estudiante+'/materia/'+id_materia
    respuesta = requests.put(url, json=datosInscripcion, headers=headers)
    return jsonify(respuesta.json())

@app.route("/inscripciones/<string:id>",methods =['DELETE'])
def eliminarInscripcion(id):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/inscripciones/' + id
    respuesta = requests.delete(url, headers=headers)
    return jsonify(respuesta.json())

@app.route("/inscripciones/materia/<string:id_materia>", methods =['GET'])
def inscritosMateria(id_materia):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/inscripciones/materia/'+id_materia
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())

@app.route("/inscripciones/notas_mayores", methods =['GET'])
def notasMayores():
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/inscripciones/nota_mayores'
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())

@app.route("/inscripciones/promedio/materia/<string:id_materia>", methods = ['GET'])
def promedioMateria(id_materia):
    headers = {"Content-Type": "application/json; charset = utf-8"}
    url = dataConfig["url-microservicio-academico"] + '/inscripciones/promedio/materia/'+id_materia
    respuesta = requests.get(url, headers=headers)
    return jsonify(respuesta.json())


def loadFileConfig():
    with open('config.json') as f:
        datos = json.load(f)
    return datos

if __name__=='__main__':
    dataConfig = loadFileConfig()
    print("Servidor corriendo en: "+dataConfig['url-api-gateway']+ " puerto: "
          +str(dataConfig['puerto']))
    serve(app, host = dataConfig['url-api-gateway'], port = dataConfig['puerto'])