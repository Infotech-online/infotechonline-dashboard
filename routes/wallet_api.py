from flask import Flask, Blueprint, request, jsonify, current_app
from local_libs.wallet_mysql import mysqlConnection_wallet
from functools import wraps
import datetime
import requests

# Blueprint
wallet_blueprint = Blueprint('wallet_BluePrint', __name__)
# mysql = mysqlConnection_wallet()

STATIC_TOKEN = 'nHJGQ8&nYw4FYBzM8i4Xje%VEKpgo$zH25B3oTJu6n2WdUqvtyz#whFX!w$&w6iy997w#UHrnRa@7bDosML#7CrGP%3#PE9iMWaS'

# Función para verificar el token
def token_verification(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener el token de la solicitud
        token = request.headers.get('Authorization')

        # Verificar que el token sea válido
        if token == f'Bearer {STATIC_TOKEN}':
            # La autenticación es exitosa, continuar con la lógica de la ruta
            return f(*args, **kwargs)
        else:
            # El token no es válido, devolver un error de autenticación
            return jsonify(message="Error de autenticación"), 401

    return decorated_function


# FONDOS -------------------------------------------------------------------------------------------

@wallet_blueprint.route('/api/wallet/fondo/create', methods=['POST'])
@token_verification
def create_Fondo():

    mysql = mysqlConnection_wallet()
 
    # Obtener los datos del cuerpo de la solicitud
    data = request.json
    NIT = data.get('NIT')
    Direccion = data.get('Direccion')
    Nombre_legal = data.get('Nombre_legal')
    Envio_Gratuito = data.get('Envio_Gratuito') 
    Margen_beneficio = data.get('Margen_beneficio')
    Nombre_Representante = data.get('Nombre_Representante')
    Telefono_Representante = data.get('Telefono_Representante')
    Cedula_Representante = data.get('Cedula_Representante')
    Puesto_Representante = data.get('Puesto_Representante')
    
    # Llamar a la función create_Fondo con los datos recibidos
    resultado = mysql.create_Fondo(
        NIT=NIT,
        Direccion=Direccion,
        Nombre_legal=Nombre_legal,
        Envio_gratuito=Envio_Gratuito,
        Margen_beneficio=Margen_beneficio,
        Nombre_Representante=Nombre_Representante,
        Telefono_Representante=Telefono_Representante,
        Cedula_Representante=Cedula_Representante,
        Puesto_Representante=Puesto_Representante
    )

    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/fondo/<int:id>', methods=['PUT'])
@token_verification
def update_fondo(id):

    mysql = mysqlConnection_wallet()

    data = request.json
    resultado = mysql.update_fondo_id(id, data)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/fondo/', methods=['GET'])
@token_verification
def all_fondos():

    mysql = mysqlConnection_wallet()

    resultado = mysql.Get_Table("Fondo")
    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/fondo/<int:id>', methods=['GET'])
@token_verification
def fondo_id(id):

    mysql = mysqlConnection_wallet()

    resultado = mysql.Get_fondo_id(id)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/fondo/<int:id>', methods=['DELETE'])
@token_verification
def delete_fondo(id):

    mysql = mysqlConnection_wallet()

    resultado = mysql.Delete_fondo_id(id)
    return jsonify({'message': resultado})


# BONOS -----------------------------------------------------------------------------------------


@wallet_blueprint.route('/api/wallet/bono/create', methods=['POST'])
@token_verification
def bono_create():

    mysql = mysqlConnection_wallet()

    data = request.json
    idBono = data.get("idBono")
    Saldo = data.get("Saldo")
    Fecha_vencimiento = data.get("Fecha_vencimiento")
    Info_Bono = data.get("Info_Bono")
    
    resultado = mysql.create_Bono(
        idBono,  
        Saldo,   
        Fecha_vencimiento,  
        Info_Bono
    )
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/bono/<string:id>', methods=['PUT'])
@token_verification
def bono_update(id):

    mysql = mysqlConnection_wallet()

    data = request.json  
    resultado = mysql.update_bono(id, data)  
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/bono/', methods=['GET'])
@token_verification
def all_bonos():

    mysql = mysqlConnection_wallet()

    resultado = mysql.Get_Table("Bono")
    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/bono/<string:id>', methods=['GET'])
@token_verification
def bono_id(id):

    mysql = mysqlConnection_wallet()

    resultado = mysql.Get_Bono_id(id)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/bono/<string:id>', methods=['DELETE'])
@token_verification
def delete_bono_id(id):

    mysql = mysqlConnection_wallet()

    resultado = mysql.delete_Bono(id)
    return jsonify({'message': resultado})

# USUARIOS ----------------------------------------------------------------------------------


@wallet_blueprint.route('/api/wallet/usuario/create', methods=['POST'])
@token_verification
def usuario_create():

    mysql = mysqlConnection_wallet()

    data = request.json
    cedula = data.get("Cedula")
    nombre = data.get("Nombre")
    correo = data.get("Correo")
    numero_telefono = data.get("Telefono")
    fondo_nit = data.get("Fondo")
    tipo_usuario = data.get("Tipo_usuario", "Usuario")  # Valor por defecto 'Usuario'

    resultado = mysql.create_usuario(
        cedula=cedula,
        nombre=nombre,
        correo=correo,
        numero_telefono=numero_telefono,
        Tipo_usuario=tipo_usuario,
        fondo_nit=fondo_nit
    )
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/usuario/<int:id>', methods=['PUT'])
@token_verification
def update_usuario(id):

    mysql = mysqlConnection_wallet()

    data = request.json
    resultado = mysql.update_usuario(id,data)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/usuario/', methods=['GET'])
@token_verification
def all_usuarios():

    mysql = mysqlConnection_wallet()

    resultado = mysql.Get_Table("Usuario")
    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/usuario/<int:id>',methods=['GET'])
@token_verification
def usuario_id(id):

    mysql = mysqlConnection_wallet()

    resultado = mysql.Get_Usuario_id(id)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/usuario/<int:id>', methods=['DELETE'])
@token_verification
def delete_usuario(id):

    mysql = mysqlConnection_wallet()

    resultado = mysql.delete_usuario_data(id)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/usuario/saldo/<int:id>', methods=["GET"])
@token_verification
def saldo_usuario(id):

    mysql = mysqlConnection_wallet()

    resultado = mysql.obtener_saldo_usuario(id)
    return jsonify({'Saldo': resultado})

@wallet_blueprint.route('/api/wallet/usuario/saldoAdmin/<int:id>', methods=["PUT"])
@token_verification
def update_saldo_usuario_admin(id):

    mysql = mysqlConnection_wallet()

    data = request.json
    saldo = data.get("Saldo")
    descripcion = data.get("Descripcion")
    monto = data.get("Monto")

    resultado = mysql.actualizar_saldo_usuario_admin(id, saldo, descripcion, monto)
    return jsonify({'message': resultado})


# CODIGO DE VERIFICACIÓN ---------------------------------------------------------------------------------

@wallet_blueprint.route('/api/wallet/codigo_verificacion/', methods=['GET'])
@token_verification
def all_codigos_verificacion():

    mysql = mysqlConnection_wallet()

    resultado = mysql.Get_Table("Codigo_verificacion")
    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/codigo_verificacion/<int:id>', methods=['GET'])
@token_verification
def codigo_verificacion(id):

    mysql = mysqlConnection_wallet()
    resultado = mysql.Get_Codigo_verificacion_id(id)

    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/codigo_verificacion/verificar', methods=['GET'])
@token_verification
def verificar_codigo_verificacion():

    mysql = mysqlConnection_wallet()

    # Obtener los parámetros de la solicitud
    user_id = request.args.get('user_id')
    code = request.args.get('verification_code')

    # Código generado en la base de datos
    current_code = mysql.Get_Codigo_verificacion_id(user_id)

    with current_app.app_context():

        SERVER_URL = current_app.config["SERVER_URL"]

        # Se genera un nuevo código de verificación
        generate_verification_code_url = SERVER_URL + '/api/wallet/codigo_verificacion/' + user_id

    if current_code == "empty":

        response = requests.post(generate_verification_code_url)
        message = response.json()

        if message["message"] == "success":
            return jsonify({'error': "Se ha generado un nuevo codigo de verificación."}), 400
        else:
            return jsonify({'error': "Error al generar el código de verificación"}), 500

    # Si el usuario no tiene códigos o esta vencido se genera uno nuevo
    if current_code[0]['Fecha_Final'] < datetime.datetime.now():

        response = requests.post(generate_verification_code_url)
        message = response.json()

        if message["message"] == "success":
            return jsonify({'error': "El código de verificación ha expirado, se ha generado uno nuevo."}), 400
        else:
            return jsonify({'error': "Error al generar el código de verificación"}), 500

    # Si el código de verificacón proporcionado por el usuario es igual al código generado
    if current_code[0]['Codigo'] == int(code):
        
        # Se establece el codigo como usado
        mysql = mysqlConnection_wallet()
        result = mysql.actualizar_estado_codigo_verificacion_a_usado(code)

        return jsonify({'success': "Se ha verificado correctamente"}), 200
    else:
        return jsonify({'error': "Código de verificación incorrecto"}), 400

# REGISTRO DE BONOS  --------------------------------------------------------------------------------------

@wallet_blueprint.route('/api/wallet/registro_bono/create', methods=['POST'])
@token_verification
def registro_bono_create():

    mysql = mysqlConnection_wallet()

    data = request.json
    usuario_cedula= data.get("Cedula")
    bono_idBono= data.get("idBono")

    resultado = mysql.create_registro_bono(
        usuario_cedula,
        bono_idBono
    )
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/registro_bono/<int:id>', methods=['GET'])
@token_verification
def registro_bono_id(id):

    mysql = mysqlConnection_wallet()

    resultado = mysql.Get_registro_bono_id(id)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/registro_bono/', methods=['GET'])
@token_verification
def all_registro_bono():

    mysql = mysqlConnection_wallet()

    resultado = mysql.Get_Table("Registro_bono")
    # Retornar la respuesta
    return jsonify({'message': resultado})


# TRANSACCIONES ----------------------------------------------------------------------------------


@wallet_blueprint.route('/api/wallet/transaccion/create', methods=['POST'])
@token_verification
def transaccion_create():

    mysql = mysqlConnection_wallet()

    data = request.json
    productos = data.get("Productos")
    forma_pago = data.get("Forma_pago")
    ciudad_envio = data.get("Ciudad_envio")
    direccion_envio = data.get("Direccion_envio")
    codigo_verificacion_codigo = data.get("Codigo_verificacion")

    resultado = mysql.create_transaccion(
        productos,
        forma_pago,
        ciudad_envio,
        direccion_envio,
        codigo_verificacion_codigo
    )

    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/transaccion/', methods=['GET'])
@token_verification
def all_transacciones():

    mysql = mysqlConnection_wallet()

    resultado = mysql.Get_Table("Transaccion")
    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/api/wallet/transaccion/<int:id>', methods=['GET'])
@token_verification
def transaccion_id(id):

    mysql = mysqlConnection_wallet()

    resultado = mysql.obtener_compras_usuario(id)
    return jsonify({'message': resultado})


@wallet_blueprint.route('/api/wallet/registro_movimiento/<int:id>', methods=['GET'])
@token_verification
def registro_movimiento_id(id):

    mysql = mysqlConnection_wallet()

    resultado = mysql.obtener_movimientos_usuario(id)
    return jsonify({'message': resultado})

