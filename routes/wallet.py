from flask import Flask, Blueprint, request, jsonify
from databases.wallet_mysql import mysqlConnection_wallet
import json

# Blueprint
wallet_blueprint = Blueprint('wallet_BluePrint', __name__)
mysql = mysqlConnection_wallet()

@wallet_blueprint.route('/fondo/create', methods=['POST'])
def create_Fondo():
# Obtener los datos del cuerpo de la solicitud
    data = request.json
    NIT = data.get('NIT')
    Direccion = data.get('Direccion')
    Nombre_legal = data.get('Nombre_legal')
    Nombre_Representante = data.get('Nombre_Representante')
    Telefono_Representante = data.get('Telefono_Representante')
    Cedula_Representante = data.get('Cedula_Representante')
    Puesto_Representante = data.get('Puesto_Representante')
    
    # Llamar a la función create_Fondo con los datos recibidos
    resultado = mysql.create_Fondo(
        NIT=NIT,
        Direccion=Direccion,
        Nombre_legal=Nombre_legal,
        Nombre_Representante=Nombre_Representante,
        Telefono_Representante=Telefono_Representante,
        Cedula_Representante=Cedula_Representante,
        Puesto_Representante=Puesto_Representante
    )

    # Retornar la respuesta
    return jsonify({'message': resultado})


@wallet_blueprint.route('/fondo/<int:id>', methods=['PUT'])
def update_fondo(id):
    data = request.json
    resultado = mysql.update_fondo_id(id, data)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/fondo/', methods=['GET'])
def all_fondos():
    resultado = mysql.Get_Table("Fondo")
    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/fondo/<int:id>', methods=['GET'])
def fondo_id(id):
    resultado = mysql.Get_fondo_id(id) 
    return jsonify({'message': resultado})

@wallet_blueprint.route('/fondo/<int:id>', methods=['DELETE'])
def delete_fondo(id):
    resultado = mysql.Delete_fondo_id(id)
    return jsonify({'message': resultado})




@wallet_blueprint.route('/usuario/create', methods=['POST'])
def usuario_create():
    data = request.json
    cedula = data.get("Cedula")
    nombre = data.get("Nombre")
    correo = data.get("Correo")
    numero_telefono = data.get("Telefono")
    fondo_nit = data.get("Fondo")
    resultado = mysql.create_usuario(
        cedula,
        nombre,
        correo,
        numero_telefono,
        fondo_nit
    )
    return jsonify({'message': resultado})

@wallet_blueprint.route('/usuario/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    resultado = mysql.update_usuario(id,data)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/usuario/', methods=['GET'])
def all_usuarios():
    resultado = mysql.Get_Table("Usuario")
    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/usuario/<int:id>',methods=['GET'])
def usuario_id(id):
    resultado = mysql.Get_Usuario_id(id)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/usuario/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    resultado = mysql.delete_usuario_data(id)
    return jsonify({'message': resultado})



@wallet_blueprint.route('/codigo_verificacion/<int:id>', methods=['POST'])
def codigo_verificacion_create(id):
    resultado = mysql.create_codigo_verificacion(id)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/codigo_verificacion/', methods=['GET'])
def all_codigos_verificacion():
    resultado = mysql.Get_Table("Codigo_verificacion")
    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/codigo_verificacion/<int:id>', methods=['GET'])
def codigos_verificacion_id(id):
    resultado = mysql.Get_Codigo_verificacion_id(id)
    # Retornar la respuesta
    return jsonify({'message': resultado})




@wallet_blueprint.route('/bono/create', methods=['POST'])
def bono_create():
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

@wallet_blueprint.route('/bono/<string:id>', methods=['PUT'])
def bono_update(id):
    data = request.json  
    resultado = mysql.update_bono(id, data)  
    return jsonify({'message': resultado})

@wallet_blueprint.route('/bono/', methods=['GET'])
def all_bonos():
    resultado = mysql.Get_Table("Bono")
    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/bono/<string:id>', methods=['GET'])
def bono_id(id):
    resultado = mysql.Get_Bono_id(id)
    return jsonify({'message': resultado})

@wallet_blueprint.route('/bono/<string:id>', methods=['DELETE'])
def delete_bono_id(id):
    resultado = mysql.delete_Bono(id)
    return jsonify({'message': resultado})



@wallet_blueprint.route('/registro_bono/create', methods=['POST'])
def registro_bono_create():
    data = request.json
    usuario_cedula= data.get("Cedula")
    bono_idBono= data.get("idBono")
    resultado = mysql.create_registro_bono(
        usuario_cedula,
        bono_idBono
    )
    return jsonify({'message': resultado})

@wallet_blueprint.route('/registro_bono/', methods=['GET'])
def all_registro_bono():
    resultado = mysql.Get_Table("Registro_bono")
    # Retornar la respuesta
    return jsonify({'message': resultado})

@wallet_blueprint.route('/registro_bono/', methods=['PUT'])
def registro_bono_update():
    data = request.json
    usuario_cedula= data.get("Cedula")
    bono_idBono= data.get("idBono")
    resultado = mysql.Update_estado_registro_bono(
        usuario_cedula,
        bono_idBono
    )
    return jsonify({'message': resultado})
    


@wallet_blueprint.route('/transaccion/create', methods=['POST'])
def transaccion_create():
    data = request.json
    productos = data.get("Productos"),
    forma_pago = data.get("Forma_pago"),
    ciudad_envio = data.get("Ciudad_envio"),
    direccion_envio = data.get("Direccion_envio"),
    codigo_verificacion_codigo= data.get("Codigo_verificacion")
    bono_idBono = data.get("idBono")
    resultado = mysql.create_transaccion(
        productos,
        forma_pago,
        ciudad_envio,
        direccion_envio,
        codigo_verificacion_codigo,
        bono_idBono,
        resultado
    )
    return jsonify({'message': resultado})



@wallet_blueprint.route('/prueba_bono_registro/', methods=['PUT'])
def update():
    data = request.json
    
