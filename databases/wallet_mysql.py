import mysql.connector
import json
from datetime import datetime, timedelta
import secrets
from dotenv import load_dotenv
import os
from flask import Flask, Blueprint, request, jsonify

from flask_mail import Mail, Message

load_dotenv()

app = Flask(__name__)
app.config['MAIL_SERVER']= os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
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

    """
        Retrieves all the data from the specified table in the database.

        Args:
            table (str): The name of the table to retrieve data from.

        Returns:
            list: A list of dictionaries representing the retrieved data. Each dictionary represents a row in the table, with column names as keys and corresponding values.

        Raises:
            mysql.connector.Error: If there is an error while retrieving the data from the table.
    """
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

    """
        Deletes all records from the specified table.

        Args:
            table (str): The name of the table to delete records from.

        Returns:
            str: A message indicating whether the deletion was successful or not.
    """
    #ELiminar todos los registros de cualquier tabla
    def Eliminar_data(self, table):
        
        sql = f"DELETE FROM {table}"
        self.mycursor.execute(sql)
        self.mydb.commit()

        # Check if the deletion was successful
        if self.mycursor.rowcount > 0:
            return "Todos los registros de la tabla fueron eliminados correctamente."
        else:
            return "No se eliminaron registros."


    # Parte dededicada a metodos CRUD Basicos de la tabla Fondo


    """
        Update the information of a Fondo record in the database.

        Args:
            NIT (int): The NIT (identification number) of the Fondo record to update.
            info (dict): A dictionary containing the updated information for the Fondo record.

        Returns:
            str: A message indicating whether the update was successful or an error occurred.

        Raises:
            mysql.connector.Error: If an error occurs during the update process.
    """
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

    """
        Retrieves the fondo information based on the given ID.

        Args:
            ID (int): The NIT (identification number) of the fondo.

        Returns:
            list: A list of dictionaries containing the formatted results. Each dictionary represents a row in the Fondo table with the following keys:
                - 'NIT': The NIT of the fondo.
                - 'Direccion': The address of the fondo.
                - 'Nombre_legal': The legal name of the fondo.
                - 'Envio_Gratuito': A boolean value indicating whether the fondo offers free shipping.
                - 'Margen_beneficio': The profit margin of the fondo.
                - 'Contacto_principal': A dictionary representing the principal contact of the fondo.

        Raises:
            str: If there is an error while executing the SQL query, an error message is returned.

    """
    #Traer fondo por NIT
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
                return column_names, formatted_results
            else:
                return None, f"No se encontró ningún registro con el ID de bono {idBono}."
        except mysql.connector.Error as e:
            return None, f"Error al mostrar el registro: {e}"

    """
        Creates a new record in the Fondo table of the database.

        Args:
            NIT (str): The NIT value for the record.
            Direccion (str): The Direccion value for the record.
            Envio_gratuito (bool): The Envio_gratuito value for the record.
            Margen_beneficio (float): The Margen_beneficio value for the record.
            Nombre_legal (str): The Nombre_legal value for the record.
            Nombre_Representante (str): The Nombre_Representante value for the record.
            Telefono_Representante (str): The Telefono_Representante value for the record.
            Cedula_Representante (str): The Cedula_Representante value for the record.
            Puesto_Representante (str): The Puesto_Representante value for the record.

        Returns:
            str: A message indicating whether the data was successfully sent or an error occurred.
    """
    #Crear un registro de Fondo
    def create_Fondo(self,NIT, Direccion,Envio_gratuito,Margen_beneficio, Nombre_legal,Nombre_Representante,Telefono_Representante,Cedula_Representante,Puesto_Representante):
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
        sql = "INSERT INTO Fondo (NIT, Direccion, Nombre_legal, Envio_Gratuito,Margen_beneficio,contacto_principal) VALUES (%s, %s, %s, %s,%s,%s)"
        self.mycursor.execute(sql, (NIT, Direccion, Nombre_legal,Envio_gratuito,Margen_beneficio,contacto_principal_json))
        self.mydb.commit()

        # Comprobar si la inserción fue exitosa
        if self.mycursor.rowcount > 0:
            return "Datos enviados correctamente."
        else:
            return "Error al enviar los datos."

    """
        Deletes a record from the 'Fondo' table based on the given ID.

        Args:
            ID (int): The ID of the record to be deleted.

        Returns:
            str: A message indicating whether the record was deleted successfully or an error occurred.
    """
    #Eliminar Registro fondo
    def Delete_fondo_id(self, ID):
        
        try:
            sql = f"DELETE FROM Fondo WHERE NIT = {ID}"
            self.mycursor.execute(sql)
            self.mydb.commit()
            return f"Fondo con NIT {ID} Fue eliminado correctamente"
        except mysql.connector.Error as e:
            return f"Error al eliminar el registro: {e}"



    #Métodos CRUD para la tabla Bono

    """
        Create a new Bono record in the database.

        Args:
            idBono (int): The ID of the Bono.
            saldo (float): The saldo of the Bono.
            Fecha_vencimiento (datetime): The expiration date of the Bono.
            Info_Bono (str): Additional information about the Bono.
            Saldo_eliminado (bool): Indicates if the saldo has been eliminated.

        Returns:
            str: A message indicating the success or failure of the operation.
        """
    #Crear Bono
    def create_Bono(self, idBono, saldo, Fecha_vencimiento, Info_Bono):
        try:
            Fecha_Publicacion = datetime.now()
            # Construct the SQL insertion query
            sql = "INSERT INTO Bono (idBono, Saldo, Fecha_Publicacion, Fecha_vencimiento, Info_Bono) VALUES (%s, %s, %s, %s, %s)"
            saldo = float(saldo)
            values = (idBono, saldo, Fecha_Publicacion, Fecha_vencimiento, Info_Bono)
            # Execute the SQL query
            self.mycursor.execute(sql, values)
            # Commit the changes to the database
            self.mydb.commit()
            return "Registro de bono creado exitosamente."
        except mysql.connector.Error as e:
            # Handle any errors that may occur during the insertion
            return f"Error al crear el registro de usuario: {e}"
    
    """
        Retrieves the details of a Bono record based on the provided idBono.

        Args:
            idBono (int): The idBono of the Bono record to retrieve.

        Returns:
            list: A list of dictionaries containing the details of the Bono record.
                  Each dictionary represents a row in the Bono table, with column names as keys.

            If no record is found with the given idBono, returns a string indicating the absence of a matching record.

        Raises:
            mysql.connector.Error: If there is an error executing the SQL query.

        """
    def Get_Bono_id(self, idBono):
        try:
            self.mycursor.execute(f"SELECT * FROM Bono WHERE idBono = '{idBono}'")
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
            return f"Error al obtener el Bono {idBono} {e}"


    """
        Update a record in the 'Bono' table with the provided ID.

        Args:
            idBono (int): The ID of the record to be updated.
            info (dict): A dictionary containing the field names and their updated values.

        Returns:
            str: A message indicating the result of the update operation.

        Raises:
            mysql.connector.Error: If an error occurs during the update operation.
        """
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

    """
        Deletes a Bono from the database based on the specified ID.

        Args:
            id_Bono (int): The ID of the Bono to be deleted.

        Returns:
            str: A message indicating the result of the deletion operation.

        Raises:
            mysql.connector.Error: If an error occurs during the deletion process.
        """
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
    
    
    
    #Parte dededicada a metodos CRUD Basicos de la tabla Usuario

    """
        Creates a new user record in the database.

        Args:
            cedula (str): The user's identification number.
            nombre (str): The user's name.
            correo (str): The user's email address.
            numero_telefono (str): The user's phone number.
            Tipo_usuario (str): The user's type.
            fondo_nit (str): The user's fund NIT.

        Returns:
            str: A message indicating the success or failure of the user creation.

        Raises:
            mysql.connector.Error: If an error occurs during the user creation.

        """
    #Crear un registro de Usuario:
    def create_usuario(self, cedula, nombre, correo, numero_telefono, Tipo_usuario, fondo_nit):
        
        try:
            # Construir la consulta SQL de inserción
            sql = "INSERT INTO Usuario (Cedula, Nombre, Correo, Numero_telefono, Estado, Tipo_usuario, Fondo_NIT) VALUES (%s, %s, %s, %s, 'Activo', %s, %s)"
            values = (cedula, nombre, correo, numero_telefono, Tipo_usuario, fondo_nit)

            # Ejecutar la consulta SQL
            self.mycursor.execute(sql, values)
            # Confirmar los cambios en la base de datos
            self.mydb.commit()

            return "Registro de usuario creado exitosamente."

        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la inserción
            return f"Error al crear el registro de usuario: {e}"

    """
        Retrieves user information based on the provided cedula.

        Args:
            cedula (int): The cedula of the user.

        Returns:
            list: A list of dictionaries containing the user information in JSON format, with column names as keys.
                  If no records are found, returns a string indicating that no record was found.
                  If an error occurs, returns a string indicating the error.

        """
    #Mostrar un registro de Usuario Por ID
    def Get_Usuario_id(self, cedula):
        
        try:
            self.mycursor.execute(f"SELECT * FROM Usuario WHERE Cedula = {cedula}")
            results = self.mycursor.fetchall()
            if results:
                # Definir el nombre de las columnas
                column_names = ['Cedula', 'Nombre', 'Correo', 'Numero_telefono', 'Estado','Tipo_usuario','Saldo', 'Fondo_NIT']
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

    """
        Update the information of a user in the 'Usuario' table.

        Args:
            cedula (str): The cedula (identification number) of the user to update.
            info (dict): A dictionary containing the updated information for the user.

        Returns:
            str: A message indicating the result of the update operation.

        Raises:
            mysql.connector.Error: If an error occurs during the update operation.
        """
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
            # Consultar si hay registros que referencian al usuario que se desea eliminar
            self.mycursor.execute(f"SELECT * FROM registro_movimiento WHERE Usuario_Cedula = {cedula}")
            referencing_records = self.mycursor.fetchall()

            # Si hay registros que hacen referencia al usuario, eliminarlos primero
            if referencing_records:
                # Eliminar los registros referenciados en la tabla registro_movimiento
                self.mycursor.execute(f"DELETE FROM registro_movimiento WHERE Usuario_Cedula = {cedula}")

            # Construir la consulta SQL para eliminar el usuario con la cédula especificada
            sql = f"DELETE FROM Usuario WHERE Cedula = {cedula}"

            # Ejecutar la consulta SQL para eliminar al usuario
            self.mycursor.execute(sql)

            # Confirmar los cambios en la base de datos
            self.mydb.commit()

            return f"Usuario con cédula {cedula} eliminado correctamente."
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la eliminación
            return f"Error al eliminar el usuario: {e}"

    #Obtener saldo de un usuario
    def obtener_saldo_usuario(self, cedula):
        try:
            # Construir la consulta SQL para obtener el saldo del usuario
            sql = "SELECT Saldo FROM Usuario WHERE Cedula = %s"
            
            # Ejecutar la consulta SQL
            self.mycursor.execute(sql, (cedula,))
            
            # Obtener el resultado de la consulta
            saldo_usuario = self.mycursor.fetchone()
            
            # Verificar si se obtuvo un resultado
            if saldo_usuario is not None:
                return saldo_usuario[0]  # Devolver el saldo del usuario
            else:
                return "No se encontró ningún usuario con la cédula proporcionada."
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la consulta
            return f"Error al obtener el saldo del usuario: {e}"
    
    #Obtener cedula de un usuario
    def obtener_cedula_usuario(self, codigo_verificacion_codigo):
        try:
            # Consulta para obtener la cédula del usuario asociada al código de verificación
            sql = "SELECT Usuario_Cedula FROM Codigo_verificacion WHERE Codigo = %s"
            self.mycursor.execute(sql, (codigo_verificacion_codigo,))
            cedula_usuario = self.mycursor.fetchone()[0]
            return cedula_usuario
        except mysql.connector.Error as e:
            print("Error al obtener la cédula del usuario:", e)
            return None
    
    # Obtener envio_gratuito de un usuario
    def obtener_envio_gratuito_usuario(self, cedula):
        try:
            # Consulta SQL para obtener el fondo del usuario
            sql_fondo = "SELECT Fondo_NIT FROM Usuario WHERE Cedula = %s"
            self.mycursor.execute(sql_fondo, (cedula,))
            fondo_nit_usuario = self.mycursor.fetchone()

            if fondo_nit_usuario is not None:
                # Si se encuentra el fondo del usuario, obtener el envío gratuito
                sql_envio_gratuito = "SELECT Envio_Gratuito FROM Fondo WHERE NIT = %s"
                self.mycursor.execute(sql_envio_gratuito, (fondo_nit_usuario,))
                envio_gratuito = self.mycursor.fetchone()

                if envio_gratuito is not None:
                    return envio_gratuito[0]  # Retornar el valor de Envio_Gratuito
                else:
                    return "No se encontró información de envío gratuito para este fondo."
            else:
                return "No se encontró el fondo del usuario en la base de datos."
        except mysql.connector.Error as e:
            print("Error al obtener el valor de Envio_Gratuito del usuario:", e)
            return None

    #Obtener el porcentaje de margen de beneficio de un usuario
    def obtener_margen_beneficio_usuario(self, cedula):
        try:
            # Consulta SQL para obtener el fondo del usuario
            sql_fondo = "SELECT Fondo_NIT FROM Usuario WHERE Cedula = %s"
            self.mycursor.execute(sql_fondo, (cedula,))
            fondo_nit_usuario = self.mycursor.fetchone()
            fondo_nit_usuario = fondo_nit_usuario[0] if isinstance(fondo_nit_usuario, tuple) else fondo_nit_usuario
            if fondo_nit_usuario is not None:
                # Si se encuentra el fondo del usuario, obtener el envío gratuito
                sql_margen_beneficio = "SELECT Margen_beneficio FROM Fondo WHERE NIT = %s"
                self.mycursor.execute(sql_margen_beneficio, (fondo_nit_usuario,))
                margen_beneficio = self.mycursor.fetchone()

                if margen_beneficio is not None:
                    
                    return margen_beneficio[0] / 100 # Retornar el valor de Envio_Gratuito
                else:
                    return "No se encontró información de envío gratuito para este fondo."
            else:
                return "No se encontró el fondo del usuario en la base de datos."
        except mysql.connector.Error as e:
            print("Error al obtener el valor de Envio_Gratuito del usuario:", e)
            return None
    
    def actualizar_saldo_usuario_admin(self, cedula, saldo, descripcion):
        try:
            # Actualizar el saldo del usuario
            sql_update = "UPDATE Usuario SET Saldo = Saldo + %s WHERE Cedula = %s"
            self.mycursor.execute(sql_update, (saldo, cedula))
            self.mydb.commit()
            tipo_accion = "Recarga"
            self.create_registro_movimiento(tipo_accion,descripcion,cedula)
            return "Saldo actualizado correctamente."
        except mysql.connector.Error as e:
            return f"Error al actualizar el saldo del usuario: {e}"
    
    
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
            usuario = self.Get_Usuario_id(usuario_cedula)[0]
            correo = usuario['Correo']
            nombre = usuario['Nombre']
            print(correo)
            #Enviar el correo electronico al usuario con el codigo de verificacion
            msg = Message('Codigo de verificacion Infotechonline', sender='noreply@demo.com', recipients=[correo])
            msg.body =  f"Hola señor {nombre}, muchas gracias por estar interesado en comprar con InfotechOnline." \
                        f"\nTu código de verificación para poder comprar es: {codigo} y expirará en 15 minutos." \
                        f"\nMuchas gracias por elegirnos."
            mail.send(msg)
            return "Código de verificación creado exitosamente, revisa tu correo para poder utilizarlo en tu compra"

        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la inserción
            return f"Error al crear el código de verificación: {e}"

    # Mostrar un registro de Codigo de Verificación por ID
    def Get_Codigo_verificacion_id(self, cedula):
        try:
            self.mycursor.execute(f"SELECT * FROM codigo_verificacion WHERE Usuario_Cedula = {cedula}")
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
                return f"El usuario con cedula {cedula} no tiene un codigo de verificacion."
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

    # Verifica si ya se venció el código de verificación
    def actualizar_estado_codigo_verificacion_a_vencido(self, codigo_verificacion_codigo):  
        try:
            # Consultar la fecha final completa del código de verificación
            sql = "SELECT Fecha_Final FROM Codigo_verificacion WHERE Codigo = %s"
            self.mycursor.execute(sql, (codigo_verificacion_codigo,))
            fecha_final = self.mycursor.fetchone()
            estado = self.obtener_estado_codigo_verificacion(codigo_verificacion_codigo)
            if estado == 'Activo':
                if fecha_final is not None:
                    fecha_final = fecha_final[0]  # Extraer la fecha final del resultado

                    # Obtener la fecha y hora actual completa
                    current_time = datetime.now()

                    # Convertir la fecha final en un objeto datetime completo
                    fecha_final = datetime.combine(fecha_final.date(), fecha_final.time())

                    # Verificar si la fecha final ha pasado
                    if current_time > fecha_final:
                        # Actualizar estado del código de verificación a 'Vencido'
                        sql_update = "UPDATE Codigo_verificacion SET Estado = 'Vencido' WHERE Codigo = %s"
                        self.mycursor.execute(sql_update, (codigo_verificacion_codigo,))
                        self.mydb.commit()
                    else:
                        return "El código de verificación aún no ha vencido."
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

    def verificar_existencia_codigo(self, codigo_verificacion_codigo):
        try:
            # Construir la consulta SQL para verificar la existencia del código de verificación
            sql = "SELECT COUNT(*) FROM Codigo_verificacion WHERE Codigo = %s"
            
            # Ejecutar la consulta SQL
            self.mycursor.execute(sql, (codigo_verificacion_codigo,))
            
            # Obtener el resultado de la consulta
            resultado = self.mycursor.fetchone()
            
            # Verificar si el código existe en la base de datos
            if resultado[0] > 0:
                return True
            else:
                return False
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la verificación
            print(f"Error al verificar la existencia del código de verificación: {e}")
            return False
    
    
    
    
    #Metodos CRUD para la tabla registro_bono


    #Crear Registro_Bono
    def create_registro_bono(self, usuario_cedula, bono_idBono):
        try:
            # Obtener la fecha actual
            fecha_registro = datetime.now()

            # Obtener el saldo del bono desde la tabla Bono
            sql_select_bono = "SELECT Saldo FROM Bono WHERE idBono = %s"
            self.mycursor.execute(sql_select_bono, (bono_idBono,))
            saldo_bono = self.mycursor.fetchone()[0]

            # Construir la consulta SQL de inserción para Registro_bono
            sql_bono = "INSERT INTO Registro_bono (Usuario_Cedula, Bono_idBono, Estado, Fecha_Registro) VALUES (%s, %s, %s, %s)"
            estado = "Activo"
            values_bono = (usuario_cedula, bono_idBono, estado, fecha_registro)

            # Ejecutar la consulta SQL para Registro_bono
            self.mycursor.execute(sql_bono, values_bono)

            # Confirmar los cambios en la base de datos para Registro_bono
            self.mydb.commit()

            # Actualizar el saldo del usuario en la tabla Usuario
            sql_update_saldo_usuario = "UPDATE Usuario SET Saldo = Saldo + %s WHERE Cedula = %s"
            self.mycursor.execute(sql_update_saldo_usuario, (saldo_bono, usuario_cedula))
            self.mydb.commit()

            # Crear el registro de movimiento en la tabla Registro_Movimiento
            tipo_accion = "Bono"
            descripcion = f" Se Registro el bono con el codigo {bono_idBono} con un saldo a favor de {saldo_bono}$"
            
            # Llamar a la función para crear el registro de movimiento
            resultado = self.create_registro_movimiento(tipo_accion, descripcion, usuario_cedula)

            return resultado
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la inserción
            return f"Error al crear el registro de bono: {e}"
    
    def Get_registro_bono_id(self, usuario_cedula):
        try:
            self.mycursor.execute(f"SELECT * FROM Registro_bono WHERE Usuario_Cedula = {usuario_cedula}")
            results = self.mycursor.fetchall()
            if results:
                # Definir el nombre de las columnas
                column_names = ['Usuario_Cedula', 'Bono_idBono', 'Estado', 'Fecha_Registro', 'Fecha_Uso']
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
                return f"No se encontró ningún registro con la cedula {usuario_cedula}."
        except mysql.connector.Error as e:
            return f"Error al mostrar el registro"

    
    #Metodos CRUD para la tabla Transaccion:

    #Calcular total de la compra
    def calcular_total_compra(self, productos, saldo, margen_beneficio, cedula):
        try:
            # Convertir la cadena JSON de productos a un diccionario
            productos_dict = json.loads(productos)
            
            # Inicializar el total de la compra
            total_compra = 0
            
            # Iterar sobre cada producto en el diccionario
            for producto, detalles in productos_dict.items():
                precio = detalles['precio']
                cantidad = detalles['cantidad']
                
                # Calcular el costo total del producto (precio * cantidad) y sumarlo al total de la compra
                total_compra += precio * cantidad
                
            # Convertir el margen de beneficio a float antes de restarlo
            margen_beneficio = float(margen_beneficio  *total_compra)
            
            # Restar el margen de beneficio
            total_compra -= margen_beneficio
            
            # Convertir el saldo a float antes de restarlo
            saldo = float(saldo)
            
            # Restar el saldo del usuario
            total_compra -= saldo
            # Verificar si el total de la compra es negativo
            if total_compra < 0:
                saldo_afavor = abs(total_compra) 
                self.update_usuario(cedula, {"Saldo": saldo_afavor})
                return 0  # El total de la compra es menor que cero, por lo tanto, no se realizará ningún cargo
            else:
                self.update_usuario(cedula, {"Saldo": 0})
                return total_compra  # Devolver el total de la compra
            
        except Exception as e:
            return "Error al Calcular la compra"  # Retorno que indica un error en el cálculo del total de la compra

    #Crear Transaccion
    def create_transaccion(self, productos, forma_pago, ciudad_envio, direccion_envio, codigo_verificacion_codigo):
        try:
            self.actualizar_estado_codigo_verificacion_a_vencido(codigo_verificacion_codigo)
            usuario_cedula = self.obtener_cedula_usuario(codigo_verificacion_codigo)
            
            # Verificar la existencia del código de verificación
            if self.verificar_existencia_codigo(codigo_verificacion_codigo):
                # Obtener el estado del código de verificación
                estado_codigo = self.obtener_estado_codigo_verificacion(codigo_verificacion_codigo)
                #if estado_codigo == "Usado":
                    #return "El código de seguridad ya ha sido utilizado."
                if estado_codigo == "Vencido":
                    return "El código de seguridad ha excedido su fecha de utilización. Por favor, genere otro."
                else:
                    # Generar ID de transacción
                    id_transaccion = secrets.randbelow(9999999 - 1000000 + 1) + 1000000

                    # Convertir los argumentos de tupla a string si es necesario
                    forma_pago = forma_pago[0] if isinstance(forma_pago, tuple) else forma_pago
                    ciudad_envio = ciudad_envio[0] if isinstance(ciudad_envio, tuple) else ciudad_envio
                    direccion_envio = direccion_envio[0] if isinstance(direccion_envio, tuple) else direccion_envio
                    margen_beneficio = self.obtener_margen_beneficio_usuario(usuario_cedula)
                    # Obtener saldo del bono desde la tabla Registro_bono
                    saldo_bono = self.obtener_saldo_usuario(usuario_cedula)
                    print(saldo_bono)
                    productos = json.dumps(productos)  # Convertir productos a formato JSON
                    # Calcular total_compra
                    total_compra = self.calcular_total_compra(productos, saldo_bono,margen_beneficio ,usuario_cedula)
                    # Insertar transacción
                    sql = """
                        INSERT INTO Transaccion (ID, Productos, Total_compra, Forma_pago, Ciudad_envio, Direccion_envio, Codigo_verificacion_Codigo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (id_transaccion, productos, total_compra, forma_pago, ciudad_envio, direccion_envio, codigo_verificacion_codigo)
                    self.mycursor.execute(sql, values)
                    self.mydb.commit()

                    # Crear el registro de movimiento en la tabla Registro_Movimiento
                    tipo_accion = "Transaccion"
                    descripcion = f" Se creó el registro de transaccion {id_transaccion} con un pago de {total_compra}"
                    
                    # Llamar a la función para crear el registro de movimiento
                    self.create_registro_movimiento(tipo_accion, descripcion, usuario_cedula)
                    
                    # Actualizar estado del código de verificación a 'Usado'
                    self.actualizar_estado_codigo_verificacion_a_usado(codigo_verificacion_codigo)
                    
                    return "Transacción realizada con éxito."
            else:
                return "Código de verificación incorrecto. No se puede realizar la transacción."
        except mysql.connector.Error as e:
            return f"Error al crear el registro de transacción {e}"
        
    #obtener compras de usuario por cedula
    def obtener_compras_usuario(self, usuario_cedula):
        try:
            # Consulta SQL para seleccionar las compras del usuario
            sql = """
                SELECT ID, Productos, Total_compra, Forma_pago, Ciudad_envio, Direccion_envio, Codigo_verificacion_Codigo
                FROM Transaccion
                WHERE Codigo_verificacion_Codigo IN (
                    SELECT Codigo
                    FROM Codigo_verificacion
                    WHERE Usuario_Cedula = %s
                )
            """
            # Ejecutar la consulta con el cédula del usuario como parámetro
            self.mycursor.execute(sql, (usuario_cedula,))
            # Obtener todas las filas resultantes
            compras_usuario = self.mycursor.fetchall()
            # Verificar si se encontraron compras para el usuario
            if compras_usuario:
                formatted_results = []
                for row in compras_usuario:
                    # Crear un nuevo resultado con el orden de las columnas de la tabla
                    formatted_result = {
                        'ID': row[0],
                        'Productos': json.loads(row[1]),
                        'Total_compra': float(row[2]),
                        'Forma_pago': row[3],
                        'Ciudad_envio': row[4],
                        'Direccion_envio': row[5],
                        'Codigo_verificacion_Codigo': row[6]
                    }
                    formatted_results.append(formatted_result)
                return formatted_results  # Devolver los resultados encontrados
            else:
                return f"No se encontraron compras para el usuario con cédula {usuario_cedula}"
        except mysql.connector.Error as e:
            return f"Error al obtener las compras del usuario: {e}"


    #Metodos CRUD para la tabla Registro_Movimiento
    def create_registro_movimiento(self, tipo_accion, descripcion, usuario_cedula):
        try:
            # Construir la consulta SQL de inserción
            fecha = datetime.now()
            sql = "INSERT INTO Registro_Movimiento (Tipo_Accion, Descripcion, Fecha, Usuario_Cedula) VALUES (%s, %s, %s, %s)"
            values = (tipo_accion, descripcion, fecha, usuario_cedula)

            # Ejecutar la consulta SQL
            self.mycursor.execute(sql, values)

            # Confirmar los cambios en la base de datos
            self.mydb.commit()

            return "Registro de movimiento creado exitosamente."
        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la inserción
            return f"Error al crear el registro de movimiento: {e}"

    def obtener_movimientos_usuario(self, usuario_cedula):
        try:
            # Consulta SQL para seleccionar los movimientos del usuario
            sql = "SELECT * FROM Registro_Movimiento WHERE Usuario_Cedula = %s"
            # Ejecutar la consulta con el cédula del usuario como parámetro
            self.mycursor.execute(sql, (usuario_cedula,))
            # Obtener todas las filas resultantes
            movimientos_usuario = self.mycursor.fetchall()
            # Verificar si se encontraron movimientos para el usuario
            if movimientos_usuario:
                formatted_results = []
                for row in movimientos_usuario:
                    # Crear un nuevo resultado con el orden de las columnas de la tabla
                    formatted_result = {
                        'ID': row[0],
                        'Tipo_Accion': row[1],
                        'Descripcion': row[2],
                        'Fecha': row[3],
                        'Usuario_Cedula': row[4]
                    }
                    formatted_results.append(formatted_result)
                return formatted_results  # Devolver los resultados encontrados
            else:
                return f"No se encontraron movimientos para el usuario con cédula {usuario_cedula}"
        except mysql.connector.Error as e:
            return f"Error al obtener los movimientos del usuario: {e}"
    