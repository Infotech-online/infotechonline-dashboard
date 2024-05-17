import mysql.connector
import json
from datetime import datetime, timedelta
import secrets
from dotenv import load_dotenv
import os
from flask import Flask
from flask_mail import Mail, Message

from wallet.local_libs.wallet_mysql import mysqlConnection_wallet
wallet = mysqlConnection_wallet()
load_dotenv()


class mysqlConnection_wallet_correo():

    def __init__(self):
        
        print("Utilizando Conexión a MySQL en PythonAnywhere")
        
        try:

            # Conexión a la base de datos MySQL (Test)
            self.mydb = mysql.connector.connect(
                host=os.getenv('DatabaseTestHost'),
                user=os.getenv('DatabaseTestUser'),
                password= os.getenv('DatabaseTestPassword'),
                database=os.getenv('DatabaseTestName')
            )   
            
            # Conexión a la base de datos MySQL (Production)
            """
            self.mydb = mysql.connector.connect(
                host= os.getenv('DatabaseProductionHost'),
                user= os.getenv('DatabaseProductionUser'),
                password= os.getenv('DatabaseProductionPassword'),
                database= os.getenv('DatabaseProductionName')
            )  
            """
            self.mycursor = self.mydb.cursor()
            if self.mydb is not None:
                print("Conexión Exitosa")
        except mysql.connector.Error as e:
            print("Error al conectar a la base de datos:", e)
    
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
        
    def create_codigo_verificacion(self, usuario_cedula,email):
        try:
            # Generar un código aleatorio
            codigo = secrets.randbelow(999999 - 100000 + 1) + 100000
            # Obtener la hora actual
            current_time = datetime.now()

            # Calcular la fecha final sumando 15 minutos a la fecha de inicio
            fecha_final = current_time + timedelta(minutes=15)

            # Convertir las fechas al formato deseado (sin el prefijo 'datetime.datetime')
            current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            fecha_final_str = fecha_final.strftime("%Y-%m-%d %H:%M:%S")
            fecha_final_hour_str = fecha_final.strftime("%H:%M:%S")


            # Construir la consulta SQL de inserción
            sql = "INSERT INTO Codigo_verificacion (Codigo, Fecha_inicio, Fecha_Final, Usuario_Cedula) VALUES (%s, %s, %s, %s)"
            # Ejecutar la consulta SQL con el código generado
            self.mycursor.execute(sql, (codigo, current_time_str, fecha_final_str, usuario_cedula))
            # Confirmar los cambios en la base de datos
            self.mydb.commit()
            usuario = wallet.Get_Usuario_id(usuario_cedula)[0]
            
            # Enviar el código de verificación al usuario por correo electrónico
            # Renderizar la plantilla con los datos dinámicos
            correo = usuario['Correo']
            nombre = usuario['Nombre']

            # Enviar el correo electrónico al usuario con el código de verificación
            msg = Message('Código de verificación Infotechonline', sender='noreply@demo.com', recipients=[correo])
            msg.html = f"""
            <html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" lang="en">


            <head>
                <title></title>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0"><!--[if mso]><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch><o:AllowPNG/></o:OfficeDocumentSettings></xml><![endif]--><!--[if !mso]><!-->
                <link href="https://fonts.googleapis.com/css?family=Oswald" rel="stylesheet" type="text/css">
                <link href="https://fonts.googleapis.com/css?family=Oxygen" rel="stylesheet" type="text/css">
                <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@100;200;300;400;500;600;700;800;900" rel="stylesheet" type="text/css"><!--<![endif]-->
                <link rel="stylesheet" href="/static/css/correo.css">

            </head>

            <body align="center" style="text-align: center;background-color: #000000; margin: 0; padding: 0; -webkit-text-size-adjust: none; text-size-adjust: none;">
                <table align="center" class="nl-container" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #000000; text-align: center;">
                    <tbody>
                        <tr>
                            <td>
                                <table class="row row-1" align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #000009; background-size: auto;text-align: center;">
                                    <tbody>
                                        <tr>
                                            <td>
                                                <table class="row-content stack" align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-image: url(''); background-repeat: no-repeat; background-size: cover; color: #000000; width: 650px; margin: 0 auto;text-align: center;" width="650">
                                                    <tbody>
                                                        <tr>
                                                            <td class="column column-1" width="100%" align="center" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: center; padding-top: 20px; vertical-align: top; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;">
                                                                <table class="image_block block-1" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad" style="padding-bottom:10px;padding-left:20px;padding-right:20px;padding-top:10px;width:100%;">
                                                                            <div class="alignment" align="center" style="line-height:10px">
                                                                                <div style="max-width: 169px;"><img src="https://infotechdecolombia.com/wp-content/uploads/2023/07/logo_info_tech-min.png" style="display: block; height: auto; border: 0; width: 100%;" width="169" alt="Your Logo" title="Your Logo" height="auto"></div>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                    
                                                                <table class="divider_block block-3" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad" style="padding-bottom:15px;padding-left:5px;padding-right:5px;padding-top:15px;">
                                                                            <div class="alignment" align="center">
                                                                                <table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                                    <tr>
                                                                                        <td class="divider_inner" style="font-size: 1px; line-height: 1px; border-top: 5px solid #0b9444;"><span>&#8202;</span></td>
                                                                                    </tr>
                                                                                </table>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                                <table class="heading_block block-4" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad" style="text-align:center;width:100%;">
                                                                            <h1 style="margin: 0; color: #ffffff; direction: ltr; font-family: ヒラギノ角ゴ Pro W3, Hiragino Kaku Gothic Pro,Osaka, メイリオ, Meiryo, ＭＳ Ｐゴシック, MS PGothic, sans-serif; font-size: 50px; font-weight: 400; letter-spacing: normal; line-height: 120%; text-align: center; margin-top: 0; margin-bottom: 0; mso-line-height-alt: 96px;"><span class="tinyMce-placeholder">Código de Verificación</span></h1>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                                <table class="divider_block block-5" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad" style="padding-bottom:20px;padding-left:5px;padding-right:5px;padding-top:15px;">
                                                                            <div class="alignment" align="center">
                                                                                <table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                                    <tr>
                                                                                        <td class="divider_inner" style="font-size: 1px; line-height: 1px; border-top: 5px solid #0b9444;"><span>&#8202;</span></td>
                                                                                    </tr>
                                                                                </table>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                                <table class="heading_block block-6" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad" style="text-align:center;width:100%;">
                                                                            <h2 style="margin: 0; color: #ffffff; direction: ltr; font-family: 'Roboto', Tahoma, Verdana, Segoe, sans-serif; font-size: 20px; font-weight: 700; letter-spacing: normal; line-height: 120%; text-align: center; margin-top: 0; margin-bottom: 0; mso-line-height-alt: 36px;"><span class="tinyMce-placeholder">Usuario {nombre}, tenga en cuenta que este código es de uso exclusivo, personal, intransferible y tendra 15 minutos para hacer uso de este.</span></h2>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                                <table class="divider_block block-7" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad" style="padding-bottom:20px;padding-left:5px;padding-right:5px;padding-top:20px;">
                                                                            <div class="alignment" align="center">
                                                                                <table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                                    <tr>
                                                                                        <td class="divider_inner" style="font-size: 1px; line-height: 1px; border-top: 5px solid #0b9444;"><span>&#8202;</span></td>
                                                                                    </tr>
                                                                                </table>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                                <div style="color:#ffffff;direction:ltr;font-family:Oxygen, Trebuchet MS, Lucida Grande, Lucida Sans Unicode, Lucida Sans, Tahoma, sans-serif;font-size:34px;font-weight:400;letter-spacing:0px;line-height:150%;text-align:center;mso-line-height-alt:22.5px;">
                                                                    <p style="margin: 0;">Codigo de Verificación:</p>
                                                                </div>
                                                                <table class="button_block block-8" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad">
                                                                            <div class="alignment" align="center"><!--[if mso]>
            <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" style="height:51px;width:46px;v-text-anchor:middle;" arcsize="0%" strokeweight="0.75pt" strokecolor="#FFFFFF" fillcolor="#568a58">
            <w:anchorlock/>
            <v:textbox inset="0px,0px,0px,0px">
            <center style="color:#ffffff; font-family:Arial, sans-serif; font-size:18px">
            <![endif]-->
                                                                                <div style="text-decoration:none;display:inline-block;color:#ffffff;background-color:#568a58;border-radius:0px;width:auto;border-top:1px solid #FFFFFF;font-weight:400;border-right:1px solid #FFFFFF;border-bottom:1px solid #FFFFFF;border-left:1px solid #FFFFFF;padding-top:5px;padding-bottom:5px;font-family:'Oswald', Arial, 'Helvetica Neue', Helvetica, sans-serif;font-size:18px;text-align:center;mso-border-alt:none;word-break:keep-all;"><span style="padding-left:20px;padding-right:20px;font-size:18px;display:inline-block;letter-spacing:3px;"><span style="word-break: break-word; line-height: 36px;">{codigo}</span></span></div><!--[if mso]></center></v:textbox></v:roundrect><![endif]-->
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                                <table class="paragraph_block block-9" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;">
                                                                    <tr>
                                                                        <td class="pad">
                                                                            <div style="color:#ffffff;direction:ltr;font-family:Oxygen, Trebuchet MS, Lucida Grande, Lucida Sans Unicode, Lucida Sans, Tahoma, sans-serif;font-size:15px;font-weight:400;letter-spacing:0px;line-height:150%;text-align:center;mso-line-height-alt:22.5px;">
                                                                                <p style="margin: 0;">Codigo válida hasta:{fecha_final_hour_str} <strong id="vigenciaFecha"></strong></p>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                            </td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                                <table class="row row-2" align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                    <tbody>
                                        <tr>
                                            <td>
                                                <table class="row-content stack" align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; color: #000000; width: 650px; margin: 0 auto;" width="650">
                                                    <tbody>
                                                        <tr>
                                                            <td class="column column-1" width="100%" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; vertical-align: top; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;padding-bottom: 20px; ">
                                                                <table class="divider_block block-1" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad">
                                                                            <div class="alignment" align="center">
                                                                                <table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                                    <tr>
                                                                                        <td class="divider_inner" style="font-size: 1px; line-height: 1px; border-top: 5px solid #0b9444;"></td>
                                                                                    </tr>
                                                                                </table>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                            </td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                                <table class="row row-3" align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                    <tbody>
                                        <tr>
                                            <td>
                                                <table class="row-content stack" align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; color: #000000; width: 650px; margin: 0 auto;" width="650">
                                                    <tbody>
                                                        <tr>
                                                            <td class="column column-1" width="100%" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; vertical-align: top; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;">
                                                                <table class="paragraph_block block-1" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;">
                                                                    <tr>
                                                                        <td class="pad">
                                                                            <div style="color:#ffffff;direction:ltr;font-family:Oxygen, Trebuchet MS, Lucida Grande, Lucida Sans Unicode, Lucida Sans, Tahoma, sans-serif;font-size:15px;font-weight:400;letter-spacing:0px;line-height:150%;text-align:center;mso-line-height-alt:22.5px;">
                                                                                <p style="margin: 0; text-align: center;">¡Visita Nuestras Redes Sociales y Nuestro E-commerce!</p>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                                <table class="social_block block-2" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad" style="padding-bottom:10px;padding-left:20px;padding-right:20px;padding-top:10px;text-align:center;">
                                                                            <div class="alignment" align="center">
                                                                                <table class="social-table" width="208px" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; display: inline-block; text-align: center;">
                                                                                    <tr>
                                                                                        <td style="padding:0 10px 0 10px;"><a href="https://www.instagram.com/infotechco/" target="_blank"><img src="https://b8b12a0fdd.imgdist.com/pub/bfra/i3gmza34/hf1/nci/ecj/instagram.png" width="32" height="auto" alt="Custom" title="Instagram" style="display: block; height: auto; border: 0;"></a></td>
                                                                                        <td style="padding:0 10px 0 10px;"><a href="https://www.linkedin.com/company/infotechdecolombia/mycompany/" target="_blank"><img src="https://b8b12a0fdd.imgdist.com/pub/bfra/i3gmza34/tbs/kn4/bzj/6c4f3e9a-81b1-44ea-a43a-e979d962eb1d.png" width="50" height="auto" alt="Custom" title="LinkedIn" style="display: block; height: auto; border: 0;"></a></td>
                                                                                        <td style="padding:0 10px 0 10px;"><a href="https://www.facebook.com/InfotechdeColombia/?locale=es_LA" target="_blank"><img src="https://b8b12a0fdd.imgdist.com/pub/bfra/i3gmza34/54a/7it/pnf/imagen_2024-05-14_111642935.png" width="40" height="auto" alt="Custom" title="Facebook" style="display: block; height: auto; border: 0;"></a></td>
                                                                                        <td style="padding:0 10px 0 10px;"><a href="https://infotechonline.co" target="_blank"><img src="https://i.ibb.co/xYqxKF6/infotechlogo.png" width="90" height="auto" alt="Custom" title="Custom" style="display: block; height: auto; border: 0;"></a></td>
                                                                                    </tr>
                                                                                </table>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                                <table class="paragraph_block block-3" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;">
                                                                    <tr>
                                                                        <td class="pad" style="padding-bottom:10px;padding-left:20px;padding-right:20px;padding-top:10px;">
                                                                            <div style="color:#ffffff;font-family:'Oxygen','Trebuchet MS','Lucida Grande','Lucida Sans Unicode','Lucida Sans',Tahoma,sans-serif;font-size:10px;line-height:120%;text-align:center;mso-line-height-alt:12px;">
                                                                                <p style="margin: 0;">Nos comprometemos a proteger sus datos personales según la Ley Estatutaria 1581 de 2012 y su decreto reglamentario 1377 de 2013 en Colombia. Implementamos medidas para garantizar la confidencialidad y seguridad de la información, obteniendo su consentimiento previo para su uso. Solo utilizamos sus datos para los fines autorizados y no los transferimos a terceros sin su consentimiento. Para más información o ejercer sus derechos como titular de la información, contáctenos.</p>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                                <table class="image_block block-4" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad" style="padding-bottom:10px;padding-left:20px;padding-right:20px;padding-top:10px;width:100%;">
                                                                            <div class="alignment" align="center" style="line-height:10px">
                                                                                <div style="max-width: 169px;"><img src="https://infotechdecolombia.com/wp-content/uploads/2023/07/logo_info_tech-min.png" style="display: block; height: auto; border: 0; width: 100%;" width="169" alt="Your Logo" title="Your Logo" height="auto"></div>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                                <div class="spacer_block block-5" style="height:20px;line-height:20px;font-size:1px;">&#8202;</div>
                                                                <table class="divider_block block-6" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                    <tr>
                                                                        <td class="pad">
                                                                            <div class="alignment" align="center">
                                                                                <table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
                                                                                    <tr>
                                                                                        <td class="divider_inner" style="font-size: 1px; line-height: 1px; border-top: 5px solid #0b9444;"><span>&#8202;</span></td>
                                                                                    </tr>
                                                                                </table>
                                                                            </div>
                                                                        </td>
                                                                    </tr>
                                                                </table>
                                                            </td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </td>
                        </tr>
                    </tbody>
                </table><!-- End -->
            </body>

            </html>
            """
            email.send(msg)

            return "Código de verificación creado exitosamente, revisa tu correo para poder utilizarlo en tu compra"

        except mysql.connector.Error as e:
            # Manejar cualquier error que pueda ocurrir durante la inserción
            return f"Error al crear el código de verificación: {e}"
