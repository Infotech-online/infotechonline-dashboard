import mysql.connector
import json
from datetime import datetime, timedelta
import secrets


class mysqlConnection_wallet():

    def __init__(self):
        
        print("Utilizando Conexión a MySQL en PythonAnywhere")
        
        try:

            # Conexión a la base de datos MySQL a través del túnel SSH
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Mifamilia42024",
                database="JGallego$Fondos"
            )   

            self.mycursor = self.mydb.cursor()
            if self.mydb is not None:
                print("Conexión Exitosa")

        except mysql.connector.Error as e:
            print("Error al conectar a la base de datos:", e)



    #Operaciones Globales:

    # Mostrar todos los datos de cualquier tabla
    def Get_Table(self, table):
        try:
            self.mycursor.execute(f"SELECT * FROM {table}")
            myresult = self.mycursor.fetchall()
            
            # Obtener los nombres de las columnas
            column_names = [desc[0] for desc in self.mycursor.description]

            # Formatear los resultados en formato JSON
            formatted_results = []
            for row in myresult:
                row_dict = {}
                for i, value in enumerate(row):
                    # Convertir cadenas JSON a objetos Python si es necesario
                    if isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            pass  # Si no se puede decodificar como JSON, mantener el valor original
                    row_dict[column_names[i]] = value
                formatted_results.append(row_dict)

            return formatted_results
        except mysql.connector.Error as e:
            return f"Error al obtener los datos de la tabla {table}: {e}"

    #ELiminar todos los registros de cualquier tabla
    def Eliminar_data(self,table):
        sql = f"DELETE FROM {table}"
        self.mycursor.execute(sql)
        self.mydb.commit()

        # Comprobar si la eliminación fue exitosa
        if self.mycursor.rowcount > 0:
            print("Todos los registros de la tabla fueron eliminados correctamente.")
        else:
            print("No se eliminaron registros.")



    # Parte dededicada a metodos CRUD Basicos de la tabla Fondo

    # Actualizar un registro de Fondo
    def update_fondo_id(self, NIT, info):
        # Construir la consulta SQL dinámicamente
        sql = f"UPDATE Fondo SET "
        values = []
        for key, value in info.items():
            if isinstance(value, dict):  # Si el valor es un diccionario (para el contacto principal)
                for sub_key, sub_value in value.items():
                    values.append(sub_value)  # Añadir el valor del sub-diccionario
                    sql += f"{key} = JSON_SET({key}, '$.{sub_key}', %s), "  # JSON_SET para actualizar el campo JSON
            else:
                values.append(value)  # Añadir el valor directamente
                sql += f"{key} = %s, "  # Añadir el nombre del campo

        sql = sql[:-2]  # Eliminar la coma y el espacio al final
        sql += f" WHERE NIT = {NIT}"

        try:
            # Ejecutar la consulta SQL con los valores pasados como secuencia
            self.mycursor.execute(sql, values)
            # Confirmar los cambios en la base de datos
            self.mydb.commit()

            # Recuperar el registro actualizado
            self.mycursor.execute(f"SELECT * FROM Fondo WHERE NIT = {NIT}")
            updated_record = self.mycursor.fetchone()

            return "Informacion Actualizada Correctamente"
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la actualización
            return f"Error al actualizar el registro: {e}"

    #Traer fondo por NIT
    def Get_fondo_id(self, ID):
        try:
            self.mycursor.execute(f"SELECT NIT, Direccion, Nombre_legal, Contacto_principal FROM Fondo WHERE NIT = {ID}")
            results = self.mycursor.fetchall()
            if results:
                formatted_results = []
                for row in results:
                    # Convertir la cadena JSON en un diccionario Python
                    contacto_principal_dict = json.loads(row[3])  # La cuarta columna es Contacto_principal
                    # Crear un nuevo resultado con el orden de las columnas de la tabla
                    formatted_result = {
                        'NIT': row[0],
                        'Direccion': row[1],
                        'Nombre_legal': row[2],
                        'Contacto_principal': contacto_principal_dict
                    }
                    formatted_results.append(formatted_result)
                return formatted_results  # Devolver los resultados encontrados
            else:
                return f"No se encontró ningún registro con el NIT {ID}"
        except mysql.connector.Error as e:
            return f"Error al Mostrar el registro {e}"


    #Añadir registro Fondo
    def create_Fondo(self,NIT, Direccion, Nombre_legal,Nombre_Representante,Telefono_Representante,Cedula_Representante,Puesto_Representante):

        # Crear un diccionario con las claves requeridas y los valores de la tupla
        contacto_principal_data = {
            "Nombre": Nombre_Representante,
            "Telefono": Telefono_Representante,
            "Cedula": Cedula_Representante,
            "Puesto": Puesto_Representante
        }

        # Convertir el diccionario a formato JSON
        contacto_principal_json = json.dumps(contacto_principal_data)

        # Insertar el registro en la base de datos
        sql = "INSERT INTO Fondo (NIT, Direccion, Nombre_legal, contacto_principal) VALUES (%s, %s, %s, %s)"
        self.mycursor.execute(sql, (NIT, Direccion, Nombre_legal, contacto_principal_json))
        self.mydb.commit()

        # Comprobar si la inserción fue exitosa
        if self.mycursor.rowcount > 0:
            return "Datos enviados correctamente."
        else:
            return "Error al enviar los datos."

    #Eliminar Registro fondo
    def Delete_fondo_id(self,ID):
        try:
            sql = f"DELETE FROM Fondo WHERE NIT = {ID}"
            self.mycursor.execute(sql)
            self.mydb.commit()
            return f"Registro con id:{ID} Fue eliminado correctamente"
        except mysql.connector.Error as e:
            return f"Error al eliminar el registro: {e}"



    #Parte dededicada a metodos CRUD Basicos de la tabla Usuario

    #Crear un registro de Usuario:
    def create_usuario(self, cedula, nombre, correo, numero_telefono, fondo_nit):
        try:
            # Construir la consulta SQL de inserción
            sql = "INSERT INTO Usuario (Cedula, Nombre, Correo, Numero_telefono, Estado, Fondo_NIT) VALUES (%s, %s, %s, %s, 'Activo', %s)"
            values = (cedula, nombre, correo, numero_telefono, fondo_nit)

            # Ejecutar la consulta SQL
            self.mycursor.execute(sql, values)
            # Confirmar los cambios en la base de datos
            self.mydb.commit()

            return "Registro de usuario creado exitosamente."

        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la inserción
            return f"Error al crear el registro de usuario: {e}"

    #Mostrar un registro de Usuario Por ID
    def Get_Usuario_id(self, cedula):
        try:
            self.mycursor.execute(f"SELECT * FROM Usuario WHERE Cedula = {cedula}")
            results = self.mycursor.fetchall()
            if results:
                # Definir el nombre de las columnas
                column_names = ['ID', 'Cedula', 'Nombre', 'Correo', 'Numero_telefono', 'Estado', 'Fondo_NIT']
                # Crear una lista para almacenar los resultados en formato JSON con el nombre de la columna
                formatted_results = []
                for row in results:
                    # Crear un diccionario para almacenar cada fila con el nombre de la columna
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[column_names[i]] = value
                    # Agregar el diccionario a la lista de resultados formateados
                    formatted_results.append(row_dict)
                return formatted_results
            else:
                return f"No se encontró ningún registro con la cedula {cedula}."
        except mysql.connector.Error as e:
            return f"Error al Mostrar el registro {e}"

    #Actualizar informacion de usuario
    def update_usuario(self, cedula, info):
        # Construir la consulta SQL dinámicamente
        sql = "UPDATE Usuario SET "
        values = []
        for key, value in info.items():
            values.append(value)  # Añadir el valor directamente
            sql += f"{key} = %s, "  # Añadir el nombre del campo

        sql = sql[:-2]  # Eliminar la coma y el espacio al final
        sql += " WHERE Cedula = %s"

        try:
            # Ejecutar la consulta SQL con los valores pasados como secuencia
            self.mycursor.execute(sql, values + [cedula])
            # Confirmar los cambios en la base de datos
            self.mydb.commit()

            # Verificar si al menos una fila fue actualizada
            if self.mycursor.rowcount > 0:
                # Verificar si la información actualizada es igual a la información planeada
                self.mycursor.execute(f"SELECT * FROM Usuario WHERE Cedula = {cedula}")
                updated_record = self.mycursor.fetchone()

                if updated_record == tuple(info.values()):
                    return "La información no se ha actualizado porque no hay cambios."
                else:
                    return "Registro actualizado exitosamente."
            else:
                return f"No se encontró ningún registro para actualizar con la cédula {cedula} proporcionada."
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la actualización
            return f"Error al actualizar el registro: {e}"

    # Eliminar un registro de la tabla Usuario
    def delete_usuario_data(self, cedula):
        try:
            # Construir la consulta SQL para eliminar el usuario con la cédula especificada
            sql = f"DELETE FROM Usuario WHERE Cedula = {cedula}"

            # Ejecutar la consulta SQL
            self.mycursor.execute(sql)

            # Confirmar los cambios en la base de datos
            self.mydb.commit()

            return f"Usuario con cédula {cedula} eliminado correctamente."
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la eliminación
            return f"Error al eliminar el usuario: {e}"


    
    # Métodos CRUD para la tabla Codigo_verificacion

    #Crear codigo de verificacion
    def create_codigo_verificacion(self, usuario_cedula):
        try:
            # Generar un código aleatorio
            codigo = secrets.randbelow(999999999 - 100000000 + 1) + 100000000
            # Obtener la hora actual
            current_time = datetime.now()

            # Calcular la fecha final sumando 15 minutos a la fecha de inicio
            fecha_final = current_time + timedelta(minutes=15)

            # Convertir las fechas al formato deseado (sin el prefijo 'datetime.datetime')
            current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            fecha_final_str = fecha_final.strftime("%Y-%m-%d %H:%M:%S")

            # Construir la consulta SQL de inserción
            sql = "INSERT INTO Codigo_verificacion (Codigo, Fecha_inicio, Fecha_Final, Usuario_Cedula) VALUES (%s, %s, %s, %s)"
            # Ejecutar la consulta SQL con el código generado
            self.mycursor.execute(sql, (codigo, current_time_str, fecha_final_str, usuario_cedula))
            # Confirmar los cambios en la base de datos
            self.mydb.commit()

            return "Código de verificación creado exitosamente."

        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la inserción
            return f"Error al crear el código de verificación: {e}"

    # Mostrar un registro de Codigo de Verificación por ID
    def Get_Codigo_verificacion_id(self, codigo):
        try:
            self.mycursor.execute(f"SELECT * FROM codigo_verificacion WHERE Codigo = {codigo}")
            results = self.mycursor.fetchall()
            if results:
                # Definir el nombre de las columnas
                column_names = ['Codigo', 'Fecha_inicio', 'Fecha_Final', 'Estado', 'Usuario_Cedula']
                # Crear una lista para almacenar los resultados en formato JSON con el nombre de la columna
                formatted_results = []
                for row in results:
                    # Crear un diccionario para almacenar cada fila con el nombre de la columna
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[column_names[i]] = value
                    # Agregar el diccionario a la lista de resultados formateados
                    formatted_results.append(row_dict)
                return formatted_results
            else:
                return f"No se encontró ningún registro con el código {codigo}."
        except mysql.connector.Error as e:
            return f"Error al mostrar el registro: {e}"
        
    # Cambia el estado del codigo de verificacion a usado
    def actualizar_estado_codigo_verificacion_a_usado(self, codigo_verificacion_codigo):
        try:
            # Actualizar estado del código de verificación a 'Usado'
            sql_update = "UPDATE Codigo_verificacion SET Estado = 'Usado' WHERE Codigo = %s"
            self.mycursor.execute(sql_update, (codigo_verificacion_codigo,))
            self.mydb.commit()
        except mysql.connector.Error as e:
            return f"Error al actualizar el estado del código de verificación a 'Usado': {e}"

    #Verifica si ya se vencio el codigo de verificacion
    def actualizar_estado_codigo_verificacion_a_vencido(self, codigo_verificacion_codigo):  
        try:
            # Obtener la hora actual
            current_time = datetime.now()

            # Consultar la fecha final del código de verificación
            sql = "SELECT Fecha_Final FROM Codigo_verificacion WHERE Codigo = %s"
            self.mycursor.execute(sql, (codigo_verificacion_codigo,))
            fecha_final = self.mycursor.fetchone()

            if fecha_final is not None:
                fecha_final = fecha_final[0]  # Extraer la fecha final del resultado
                # Verificar si la fecha final ha pasado
                if current_time > fecha_final:
                    # Actualizar estado del código de verificación a 'Vencido'
                    sql_update = "UPDATE Codigo_verificacion SET Estado = 'Vencido' WHERE Codigo = %s"
                    self.mycursor.execute(sql_update, (codigo_verificacion_codigo,))
                    self.mydb.commit()
            else:
                return "No se encontró el código de verificación en la base de datos."
        except mysql.connector.Error as e:
            return f"Error al actualizar el estado del código de verificación a 'Vencido': {e}"

    #Esta funcion verifica y trae el estado del codigo de verificacion
    def obtener_estado_codigo_verificacion(self, codigo_verificacion_codigo):
        try:
            # Consulta SQL para obtener el estado del código de verificación
            sql = "SELECT Estado FROM Codigo_verificacion WHERE Codigo = %s"

            # Ejecutar la consulta SQL con el código de verificación proporcionado
            self.mycursor.execute(sql, (codigo_verificacion_codigo,))

            # Obtener el resultado de la consulta
            resultado = self.mycursor.fetchone()

            if resultado:
                # Devolver el estado del código de verificación
                return resultado[0]
            else:
                return None  # Devolver None si no se encuentra ningún registro
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la consulta
            print("Error al obtener el estado del código de verificación:", e)
            return None



    #Métodos CRUD para la tabla Bono

    #Crear Bono
    def create_Bono(self,idBono,saldo,Fecha_vencimiento,Info_Bono):
        try:
            Fecha_Publicacion=datetime.now()
            # Construir la consulta SQL de inserción
            sql = "INSERT INTO Bono (idBono,Saldo,Fecha_Publicacion,Fecha_vencimiento,Info_Bono) VALUES (%s, %s, %s, %s,%s)"
            values = (idBono,saldo,Fecha_Publicacion,Fecha_vencimiento,Info_Bono)
            # Ejecutar la consulta SQL
            self.mycursor.execute(sql, values)
            # Confirmar los cambios en la base de datos
            self.mydb.commit()
            return "Registro de bono creado exitosamente."
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la inserción
            return f"Error al crear el registro de usuario: {e}"
    
    def Get_Bono_id(self, idBono):
        try:
            self.mycursor.execute(f"SELECT * FROM Bono WHERE idBono = '{idBono}'")
            results = self.mycursor.fetchall()
            if results:
                # Definir el nombre de las columnas
                column_names = ['idBono', 'Saldo', 'Fecha_Publicacion', 'Fecha_vencimiento', 'Info_Bono', 'Fecha_actualizacion']
                # Crear una lista para almacenar los resultados en formato JSON con el nombre de la columna
                formatted_results = []
                for row in results:
                    # Crear un diccionario para almacenar cada fila con el nombre de la columna
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[column_names[i]] = value
                    # Agregar el diccionario a la lista de resultados formateados
                    formatted_results.append(row_dict)
                return formatted_results
            else:
                return f"No se encontró ningún registro con el ID de bono {idBono}."
        except mysql.connector.Error as e:
            return f"Error al mostrar el registro: {e}"

    #Actualizar bono
    def update_bono(self, idBono, info):
        # Construir la consulta SQL dinámicamente
        sql = "UPDATE Bono SET "
        values = []
        for key, value in info.items():
            values.append(value)  # Añadir el valor directamente
            sql += f"{key} = %s, "  # Añadir el nombre del campo
        sql = sql[:-2]  # Eliminar la coma y el espacio al final
        sql += " WHERE idBono = %s"
        try:
            # Ejecutar la consulta SQL con los valores pasados como secuencia
            self.mycursor.execute(sql, values + [idBono])
            # Confirmar los cambios en la base de datos
            self.mydb.commit()

            # Verificar si al menos una fila fue actualizada
            if self.mycursor.rowcount > 0:
                return "Registro actualizado exitosamente."
            else:
                return f"No se encontró ningún registro para actualizar con el ID de bono {idBono} proporcionado."
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la actualización
            return f"Error al actualizar el registro: {e}"

    #Eliminar bono
    def delete_Bono(self, id_Bono):
        try:
            # Verificar si el bono con el ID especificado existe antes de intentar eliminarlo
            self.mycursor.execute("SELECT * FROM Bono WHERE idBono = %s", (id_Bono,))
            result = self.mycursor.fetchone()

            if result is None:
                return f"El Bono con el ID {id_Bono} no existe."
            else:
                # Construir la consulta SQL para eliminar el bono con el id especificado
                sql = "DELETE FROM Bono WHERE idBono = %s"
                # Ejecutar la consulta SQL con el ID del bono como parámetro
                self.mycursor.execute(sql, (id_Bono,))
                # Confirmar los cambios en la base de datos
                self.mydb.commit()
                return f"Bono con ID {id_Bono} eliminado correctamente."
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la eliminación
            return f"Error al eliminar el bono: {e}"

    #Obtener el valor del bono
    def obtener_valor_bono(self, bono_idBono):
        # Consulta para obtener el valor del bono
        sql = "SELECT Saldo FROM Bono WHERE idBono = %s"
        self.cursor.execute(sql, (bono_idBono,))
        valor_bono = self.cursor.fetchone()[0]
        return valor_bono
    
    

    #Metodos CRUD para la tabla registro_bono

    #Verificar estado del registro bono
    def verificar_estado_registro_bono(self, bono_idBono):
        try:
            # Consulta SQL para obtener el estado del bono
            sql = "SELECT Estado FROM Registro_bono WHERE Bono_idBono = %s"

            # Ejecutar la consulta
            self.cursor.execute(sql, (bono_idBono,))

            # Obtener el resultado de la consulta
            estado = self.cursor.fetchone()

            if estado:
                return estado[0]  # Retorna el estado del bono
            else:
                return None  # Retorna None si no se encuentra el bono
        except mysql.connector.Error as e:
            print("Error al verificar el estado del bono:", e)

    #Crear Registro_Bono
    def create_registro_bono(self, usuario_cedula, bono_idBono):
        try:
            # Obtener el valor del bono
            saldo_bono = self.obtener_valor_bono(bono_idBono)
            # Construir la consulta SQL de inserción
            sql = "INSERT INTO Registro_bono (Usuario_Cedula, Bono_idBono, Estado, Saldo_bono) VALUES (%s, %s, %s, %s)"
            estado = "Activo"
            values = (usuario_cedula, bono_idBono, estado, saldo_bono)
            # Ejecutar la consulta SQL
            self.mycursor.execute(sql, values)
            # Confirmar los cambios en la base de datos
            self.mydb.commit()
            return "Registro de bono creado exitosamente."

        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la inserción
            return f"Error al crear el registro de usuario: {e}"

    def verificar_estado_bono(self, bono_idBono):
        try:
            # Consulta SQL para obtener el estado del bono
            sql = "SELECT Estado FROM Registro_bono WHERE Bono_idBono = %s"
            # Ejecutar la consulta
            self.mycursor.execute(sql, (bono_idBono,))
            # Obtener el resultado de la consulta
            estado = self.mycursor.fetchone()
            if estado:
                return estado[0]  # Retorna el estado del bono
            else:
                return None  # Retorna None si no se encuentra el bono
        except mysql.connector.Error as e:
            return f"Error al verificar el estado del bono: {e}"
        
    #Actualizar estado Bono

    def obtener_fecha_utilizacion(self, usuario_cedula, bono_idBono):
        try:
            # Consultar la fecha de utilización del bono para el usuario dado
            self.mycursor.execute("SELECT Fecha_Utilizacion FROM Registro_bono WHERE usuario_cedula = %s AND bono_idBono = %s", (usuario_cedula, bono_idBono))
            fecha_utilizacion_json = self.mycursor.fetchone()[0]

            # Parsear el JSON y obtener la fecha de utilización
            fecha_utilizacion = {}
            if fecha_utilizacion_json:
                fecha_utilizacion = json.loads(fecha_utilizacion_json)

            return fecha_utilizacion
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la consulta
            return f"Error al obtener la fecha de utilización: {e}"

    def calcular_valor_utilizado(self, fecha_utilizacion):
        try:
            # Calcular el valor total utilizado del bono
            valor_utilizado_total = sum(fecha_utilizacion.values())
            return valor_utilizado_total
        except Exception as e:
            # Manejar cualquier error que pueda ocurrir durante el cálculo
            return f"Error al calcular el valor utilizado: {e}"
    
    def Update_estado_registro_bono(self, usuario_cedula, bono_idBono):
        try:
            # Consultar la fecha de utilización del bono para el usuario dado
            self.mycursor.execute("SELECT Fecha_Utilizacion FROM Registro_bono WHERE usuario_cedula = %s AND bono_idBono = %s", (usuario_cedula, bono_idBono))
            fecha_utilizacion_json = self.mycursor.fetchone()[0]
            # Parsear el JSON y obtener la fecha de utilización
            fecha_utilizacion = {}
            if fecha_utilizacion_json:
                fecha_utilizacion = json.loads(fecha_utilizacion_json)
            # Calcular el valor total utilizado del bono
            valor_utilizado_total = sum(fecha_utilizacion.values())
            # Obtener el valor total del bono
            valor_total_bono = self.obtener_valor_bono(bono_idBono)
            # Verificar si la suma de los valores utilizados es igual al valor total del bono
            if valor_utilizado_total == valor_total_bono:
                estado = "Usado"
            else:
                estado = "Activo"

            # Construir la consulta SQL para actualizar el estado y el registro en la tabla intermedia
            sql = "INSERT INTO Registro_bono (usuario_cedula, bono_idBono, estado, Registro) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE estado = VALUES(estado), Registro = VALUES(Registro)"

            # Actualizar el registro con la nueva información
            fecha_utilizacion_str = str(datetime.now())
            fecha_utilizacion[fecha_utilizacion_str] = valor_utilizado_total
            registro_json = json.dumps(fecha_utilizacion)

            # Ejecutar la consulta SQL con los valores proporcionados
            self.mycursor.execute(sql, (usuario_cedula, bono_idBono, estado, registro_json))

            # Confirmar los cambios en la base de datos
            self.mydb.commit()

            return "Estado actualizado correctamente."
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la actualización
            return f"Error al actualizar el estado: {e}"

    # Verificar si el bono se ha utilizado para el cliente actual
    def verificar_bono_utilizado_por_cliente(self, usuario_cedula, bono_idBono):
        try:
            # Consultar el estado del bono para el cliente actual
            sql = "SELECT Estado FROM Registro_bono WHERE Usuario_Cedula = %s AND Bono_idBono = %s"
            self.mycursor.execute(sql, (usuario_cedula, bono_idBono))
            estado_bono = self.mycursor.fetchone()

            if estado_bono:
                # Si el bono se ha utilizado, devuelve True
                if estado_bono[0] == "Usado":
                    return True
            return False
        except mysql.connector.Error as e:
            print("Error al verificar el estado del bono para el cliente:", e)
            return False

    def obtener_saldo_Registro_bono(self, usuario_cedula, bono_idBono):
        try:
            # Consulta para obtener el saldo del bono desde la tabla Registro_bono
            sql = "SELECT Saldo_bono FROM Registro_bono WHERE Usuario_Cedula = %s AND Bono_idBono = %s"
            values = (usuario_cedula, bono_idBono)
            self.mycursor.execute(sql, values)
            saldo_bono = self.mycursor.fetchone()[0]
            return saldo_bono
        except mysql.connector.Error as e:
            print("Error al obtener el saldo del bono:", e)

    #Metodos CRUD para la tabla Transaccion:

    def obtener_cedula_usuario(self, codigo_verificacion_codigo):
        try:
            # Consulta para obtener la cédula del usuario asociada al código de verificación
            sql = "SELECT Usuario_Cedula FROM Codigo_verificacion WHERE Codigo = %s"
            self.cursor.execute(sql, (codigo_verificacion_codigo,))
            cedula_usuario = self.cursor.fetchone()[0]
            return cedula_usuario
        except mysql.connector.Error as e:
            print("Error al obtener la cédula del usuario:", e)
            return None
    def calcular_total_compra(self, productos, bono_idBono):
        try:
            
            # Convertir los productos de JSON a un diccionario
            productos_dict = json.loads(productos)

            # Obtener la suma de los valores de los productos
            suma_productos = sum(productos_dict.values())

            # Obtener el valor del bono solo si está activo
            estado_bono = self.verificar_estado_bono(bono_idBono)
            if estado_bono == 'Activo':
                valor_bono = self.obtener_valor_bono(bono_idBono)
            else:
                valor_bono = 0

            # Calcular total_compra
            total_compra = suma_productos - valor_bono
            return total_compra
        except Exception as e:
            return -1  # Retorno que indica un error en el cálculo del total de la compra

    def create_transaccion(self, productos, forma_pago, ciudad_envio, direccion_envio, codigo_verificacion_codigo, bono_idBono):
        try:
            self.actualizar_estado_codigo_verificacion_a_vencido(codigo_verificacion_codigo)
            usuario_cedula = self.obtener_cedula_usuario(codigo_verificacion_codigo)
            # Generar ID de transacción
            id_transaccion = secrets.randbelow(9999999 - 1000000 + 1) + 1000000

            # Calcular total_compra
            total_compra = self.calcular_total_compra(productos, bono_idBono, usuario_cedula)
            
            # Verificar la existencia del código de verificación
            if self.verificar_existencia_codigo(codigo_verificacion_codigo):
                # Obtener el estado del código de verificación
                estado_codigo = self.obtener_estado_codigo_verificacion(codigo_verificacion_codigo)

                if estado_codigo == "Usado":
                    return "El código de seguridad ya ha sido utilizado."
                elif estado_codigo == "Vencido":
                    return "El código de seguridad ha excedido su fecha de utilización. Por favor, genere otro."
                else:
                    # Actualizar estado del código de verificación a 'Usado'
                    self.actualizar_estado_codigo_verificacion_a_usado(codigo_verificacion_codigo)

                    # Obtener saldo del bono desde la tabla Registro_bono
                    saldo_bono = self.obtener_saldo_Registro_bono(usuario_cedula, bono_idBono)

                    # Insertar transacción
                    sql = """
                        INSERT INTO Transaccion (ID, Productos, Total_compra, Forma_pago, Ciudad_envio, Direccion_envio, Codigo_verificacion_Codigo, Bono_idBono, Saldo_bono)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (id_transaccion, productos, total_compra, forma_pago, ciudad_envio, direccion_envio, codigo_verificacion_codigo, bono_idBono, saldo_bono)
                    self.mycursor.execute(sql, values)
                    self.mydb.commit()

                    if usuario_cedula is not None:
                        # Actualizar estado en la tabla Registro_bono
                        self.Update_estado_registro_bono(usuario_cedula, bono_idBono)

                    return "Registro de transacción creado exitosamente."
            else:
                return "Código de verificación incorrecto. No se puede realizar la transacción."
        except mysql.connector.Error as e:
            print("Error al crear el registro de transacción:", e)

    












