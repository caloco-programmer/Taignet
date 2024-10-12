from flask import Flask, jsonify, request, session, redirect, url_for
import oracledb
from config import name, psw, cdir, wltloc, wlpsw, dsn, correo, correo_psw
import bcrypt
from flask_cors import CORS
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os 
import time
import base64

app = Flask(__name__)

CORS(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = correo
app.config['MAIL_PASSWORD'] = correo_psw
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = correo # Asegúrate de usar tu correo real


app.secret_key = os.urandom(24)
mail = Mail(app)
s = URLSafeTimedSerializer('secreto')

# In-memory storage for pending users
pending_users = {}

@app.route('/usuario/<username>', methods=['GET'])
def obtener_usuario(username):
    try:
        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            with connection.cursor() as cursor:
                sql = """SELECT NAME_USER, AP_USER, USERNAME, MAIL,PASWORD FROM USUARIO WHERE USERNAME = :username"""
                cursor.execute(sql, [username])
                result = cursor.fetchone()

                if result is None:
                    return None, 404  # No encontrado, devuelve None y código de estado

                usuario = {
                    "nomb": result[0],
                    "apellido": result[1],
                    "username": result[2],
                    "gmail": result[3],
                    "password": result[4]
                }
                return usuario, 200  # Devuelve el usuario y el código de estado 200

    except Exception as ex:
        print(str(ex))  # Log del error en consola
        return None, 500  # Error del servidor, devuelve None y código de estado 500

@app.route('/usuarios', methods=['POST'])
def agregar_usuario():
    try:
        data = request.json
        nombre = data['nombre']
        apellido = data['apellido']
        username = data['username']
        email = data['gmail']
        
        if data['password'] is not None:
            psws = data['password']
            pasw = psws.encode('utf-8')
            sal = bcrypt.gensalt()
            password = bcrypt.hashpw(pasw, sal)
            password_real = password.decode('utf-8')

            # Almacenar usuario pendiente en memoria
            pending_users[email] = {
                "nombre": nombre,
                "apellido": apellido,
                "username": username,
                "password": password_real,
                "estado": "Pendiente"
            }

            token = s.dumps(email, salt='correo-confirmacion')  # Genera el token
            link = url_for('confirmar_email', token=token, _external=True)

            msg = Message('Confirma tu correo', sender='tu_correo@gmail.com', recipients=[email])
            msg.body = f'Por favor confirma tu correo haciendo clic en el siguiente enlace: {link}'
            mail.send(msg)

            return jsonify({"message": "Se ha enviado un correo de confirmación."}), 201
        else:
            return jsonify({"error": "La contraseña no puede ser nula."}), 400

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

@app.route('/add_friend', methods=['POST'])
def add_friend():
    try:

        data = request.json
        username = data['usuario']
        friend = data['user_friend']
        print(data)
        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            with connection.cursor() as cursor:
                sql = """SELECT NAME_USER, AP_USER, USERNAME, MAIL,PASWORD FROM USUARIO WHERE USERNAME = :username"""
                cursor.callproc('pkg_amigos.pa_ad_friend',[friend,username])
                
                connection.commit()

                
                return jsonify({'status': 'success' }), 200   # Devuelve el usuario y el código de estado 200

    except Exception as ex:
        print(str(ex))  # Log del error en consola
        return None, 500  # Error del servidor, devuelve None y código de estado 500

@app.route('/get_friend', methods = ['POST'])
def obtener_amigo():
    try:
        data = request.json
        username = data['username']
        print(data)
        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            with connection.cursor() as cursor:
                sql = """select user_id,estado from amigo where friend_id = (select id_usuario from usuario where username = :username)"""
                print(username)
                cursor.execute(sql, [username])
                result = cursor.fetchall()
                print(result)
                if result is None:
                    return jsonify({'status': 'error', 'message': 'No friends found'}), 404

                amigos = []
                for row in result:

                    user_id = row[0]
                    print(user_id)
                    estado = row[1]
                    sql2 = """select username from usuario where id_usuario = :user_id"""
                    cursor.execute(sql2, [user_id])

                    friend_username=cursor.fetchone()
                    print(friend_username)
                    if friend_username:
                        amigo = {
                            "username": friend_username[0],
                            "estado": estado
                        }
                    
                        amigos.append(amigo)
                        print(amigos)
                return jsonify({'status': 'success', 'amigos': amigos}), 200 

    except Exception as ex:
        print(str(ex))
        print("error")  # Log del error en consola
        return jsonify({'status': 'error', 'message': str(ex)}), 500  # Error del servidor, devuelve None y código de estado 500

@app.route('/confirmar_friend',methods = ['POST']) 
def confirm_friend():
    try:
        data = request.json
        username_friend = data['username_friend']
        estado = data['estado']
        username = data['username']
        print("este es el estado "+estado)
        print(data)
        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            with connection.cursor() as cursor:
                sql = """select id_usuario from usuario where username = :username_friend"""
                print(username_friend)
                cursor.execute(sql, [username_friend])
                result = cursor.fetchall()
                
                if result is None:
                    return jsonify({'status': 'error', 'message': 'No friends found'}), 404
                else:
                    id_usuario=result[0][0]
                    cursor.execute("select id_usuario from usuario where username = :username",[username])
                    id_user = cursor.fetchall()
                    id_us = id_user[0][0]
                    print(id_us)
                    
                    if estado == 'aceptado':
                        sql2="""update amigo set estado = :estado where user_id = :id_usuario and friend_id = :id_us"""
                        cursor.execute(sql2,[estado,id_usuario,id_us])
                        connection.commit()

                    if estado == 'rechazado' :
                        sql2="""delete FROM amigo where friend_id = :id_us and user_id = :id_usuario"""
                        cursor.execute(sql2,[id_us,id_usuario])

                        
                        connection.commit()
                
                return jsonify({'status': 'success', 'amigos': estado}), 200 

    except Exception as ex:
        print(str(ex))
        print("error")  # Log del error en consola
        return jsonify({'status': 'error', 'message': str(ex)}), 500  # Error del servidor, devuelve None y código de estado 500
    
@app.route('/confirmar/<token>')
def confirmar_email(token):
    try:
        email = s.loads(token, salt='correo-confirmacion', max_age=3600)  # Token válido por 1 hora

        # Verificar si el usuario está pendiente
        if email in pending_users:
            user_info = pending_users.pop(email)  # Eliminar de usuarios pendientes

            # Insertar usuario en la base de datos
            with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                                  wallet_location=wltloc, wallet_password=wlpsw) as connection:
                with connection.cursor() as cursor:
                    sql = """INSERT INTO USUARIO VALUES(seq_id_usuario.NEXTVAL, :nombre, :apellido, :username, :mail, :password,
                    :estado)"""
                    cursor.callproc('pkg_usuario.pa_add', [user_info['nombre'], user_info['apellido'], 
                                                           user_info['username'], email, user_info['password'], 'Activo'])
                    connection.commit()

            return f'<h3>Correo {email} confirmado exitosamente. Tu cuenta está activa ahora.</h3>'
        else:
            return '<h3>El correo no está pendiente de confirmación.</h3>', 400

    except SignatureExpired:
        return '<h3>El token ha expirado, por favor solicita uno nuevo.</h3>'
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password_input = data['password'].encode('utf-8')  # Codificar la contraseña ingresada

        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            with connection.cursor() as cursor:
                # Obtener la contraseña almacenada
                sql = """SELECT PASWORD FROM USUARIO WHERE USERNAME = :username"""
                cursor.execute(sql, [username])
                result = cursor.fetchone()

                if result is None:
                    return jsonify({"error": "Usuario no encontrado"}), 404

                # Obtener el hash de la contraseña almacenada
                stored_password_hash = result[0].encode('utf-8')  # Asegúrate de que esté en bytes

                # Verificar la contraseña ingresada contra el hash almacenado
                if bcrypt.checkpw(password_input, stored_password_hash):
                    session['username'] = username
                    
                    # Llama a la función para obtener los datos del usuario
                    usuario_data, status = obtener_usuario(username)

                    if status == 200:
                        return jsonify({'status': 'success', 'usuario': usuario_data}), 200  # Retorna el usuario en la respuesta
                    else:
                        return jsonify({"error": "Usuario no encontrado"}), status  # Maneja el error

                else:
                    return jsonify({"error": "Contraseña incorrecta"}), 401

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

@app.route('/update', methods=['POST'])
def update_usuario():
    data = request.json
   
    try:
        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            
            with connection.cursor() as cursor:
                print(data)
                user_antiguo = data['user_antiguo']
                username = data['username']
                # Llama al procedimiento almacenado
                cursor.callproc('pkg_usuario.pa_update', [data['nomb'],
                                                           data['apellido'],username, data['gmail'], data['password'],'activo',user_antiguo])
                connection.commit()  # Asegúrate de hacer commit

                user_data,status=obtener_usuario(username)
               
               

                if status == 200:
                    session['username'] = data['username']
                    session['nomb'] = data['nomb']
                    session['apellido'] = data['apellido']
                    session['gmail'] = data['gmail']
                    print("Sesión actualizada con los nuevos datos:", session)  # Verifica que la sesión se actualiza
                    return jsonify({'status': 'success', 'usuario': user_data}), 200  # Retorna el usuario en la respuesta
                else:
                    return jsonify({"error": "Usuario no encontrado"}), status  # Maneja el error


        return jsonify({"status": "success", "message": "Usuario actualizado"}), 200

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500
    
@app.route('/add_tarjeta', methods=['POST'])
def add_tarjeta():
    try:

        data = request.json
        username = data['usuario']
        nombre = data['nombre']
        tipo = data['tipo']
        cantidad = data['cantidad']
        print(data)
        print(username)
        print(nombre)
        print(tipo)
        print(cantidad)

        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            with connection.cursor() as cursor:
                
                cursor.callproc('pkg_tarjeta.pa_add_tarjeta',[nombre,username,tipo,cantidad])
                
                connection.commit()

                
                return jsonify({'status': 'success' }), 200   # Devuelve el usuario y el código de estado 200

    except Exception as ex:
        print(str(ex))  # Log del error en consola
        return None, 500  # Error del servidor, devuelve None y código de estado 500

@app.route('/get_tarjeta', methods = ['POST'])
def obtener_tarjeta():
    try:
        data = request.json
        username = data['username']
        print(data)
        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            with connection.cursor() as cursor:
                sql = """select id_usuario from usuario where username = :username"""
                print(username)
                cursor.execute(sql, [username])
                result = cursor.fetchall()
                print(result)
                if result is None:
                    return jsonify({'status': 'error', 'message': 'No friends found'}), 404

                tarjetas = []
                for row in result:

                    user_id = row[0]
                    print(user_id)

                    sql2 = """select id_tarjeta,nombre,cantidad,tipo_tarjeta from tarjeta where id_usuario = :user_id"""
                    cursor.execute(sql2, [user_id])

                    cards=cursor.fetchall()
                    print(cards)
                    for card in cards:
                        tarjeta = {
                            "id_tarjeta": card[0],
                            "nombre": card[1],
                            "cantidad": card[2],
                            "tipo_tarjeta": card[3],
                            "id_usuario": row[0],                            
                        }
                    
                        tarjetas.append(tarjeta)
                        print(tarjetas)
                tarjetas_ordenadas = sorted(tarjetas, key=lambda x: x['id_tarjeta'])
                return jsonify({'status': 'success', 'tarjetas': tarjetas_ordenadas}), 200 

    except Exception as ex:
        print(str(ex))
        print("error")  # Log del error en consola
        return jsonify({'status': 'error', 'message': str(ex)}), 500  # Error del servidor, devuelve None y código de estado 500
    

@app.route('/delete_tarjeta',methods=['POST'])
def delete_tarjeta():
    try:

        data = request.json
        print("Tipo de 'data':", type(data))
        
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400

        id_tarjeta = data['id_tarjeta']  # Asegúrate de que 'id_categoria' esté en el JSON
        print("ID de tarjeta:", id_tarjeta)
        

        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            with connection.cursor() as cursor:
                
                cursor.callproc('pkg_tarjeta.pa_delete',[id_tarjeta])
                
                connection.commit()

                
                return jsonify({'status': 'success' }), 200   # Devuelve el usuario y el código de estado 200

    except Exception as ex:
        print(str(ex))
        print("error")  # Log del error en consola
        return jsonify({'status': 'error', 'message': str(ex)}), 500 
    
@app.route('/add_categoria', methods=['POST'])
def add_categoria():
    try:
        # Obtener los datos del formulario
        categoria = request.form['categoria']
        username = request.form['usuario']
        
        # Verificar si hay una imagen en los archivos
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            # Leer el archivo como binario
            file_content = imagen.read()
            
            # Conectar a la base de datos
            with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                                  wallet_location=wltloc, wallet_password=wlpsw) as connection:
                with connection.cursor() as cursor:
                    # Llamar al procedimiento almacenado pasando la imagen en formato BLOB
                    cursor.callproc('pkg_categoria.pa_add_categoria', [categoria, username, file_content])
                    connection.commit()

            return jsonify({'status': 'success'}), 200

        else:
            return jsonify({'error': 'No image provided'}), 400

    except Exception as ex:
        print(str(ex))  # Imprimir el error
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/get_categorias', methods = ['POST'])
def obtener_categorias():
    try:
        data = request.json
        username = data['username']
        print(data)
        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            with connection.cursor() as cursor:
                # Buscar el id del usuario por su username
                sql = """select id_usuario from usuario where username = :username"""
                print(username)
                cursor.execute(sql, [username])
                result = cursor.fetchall()
                print(result)
                if result is None:
                    return jsonify({'status': 'error', 'message': 'Usuario no encontrado'}), 404

                categorias = []
                for row in result:
                    user_id = row[0]
                    print(user_id)

                    # Obtener las categorías del usuario
                    sql2 = """select id_categoria, nombre, img from categoria where id_usuario = :user_id"""
                    cursor.execute(sql2, [user_id])

                    cards = cursor.fetchall()
                    print(cards)

                    for card in cards:
                        # Convertir la imagen BLOB a base64 para que sea serializable en JSON
                        img_blob = card[2]
                        if img_blob is not None:
                            img_base64 = base64.b64encode(img_blob.read()).decode('utf-8')
                        else:
                            img_base64 = None

                        categoria = {
                            "id_categoria": card[0],
                            "nombre": card[1],
                            "imagen": img_base64,  # Imagen en formato base64
                        }
                    
                        categorias.append(categoria)
                        print(categorias)
                    
                return jsonify({'status': 'success', 'categorias': categorias}), 200 

    except Exception as ex:
        print(str(ex))
        print("error")  # Log del error en consola
        return jsonify({'status': 'error', 'message': str(ex)}), 500  # Error del servidor


@app.route('/delete_categoria',methods=['POST'])
def delete_categoria():
    try:

        data = request.json
        print("Tipo de 'data':", type(data))
        
        if not isinstance(data, dict):
            return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400

        id_categoria = data['id_categoria']  # Asegúrate de que 'id_categoria' esté en el JSON
        print("ID de categoría:", id_categoria)
        

        with oracledb.connect(user=name, password=psw, dsn=dsn, config_dir=cdir, 
                              wallet_location=wltloc, wallet_password=wlpsw) as connection:
            with connection.cursor() as cursor:
                
                cursor.callproc('pkg_categoria.pa_delete_categoria',[id_categoria])
                
                connection.commit()

                
                return jsonify({'status': 'success' }), 200   # Devuelve el usuario y el código de estado 200

    except Exception as ex:
        print(str(ex))
        print("error")  # Log del error en consola
        return jsonify({'status': 'error', 'message': str(ex)}), 500 



@app.route('/delete_categoria',methods=['OPTIONS'])
def option_delete_categoria():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, 200  # Asegúrate de que se devuelva el estado 200

@app.route('/usuarios', methods=['OPTIONS'])
def options_usuarios():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, 200  # Asegúrate de que se devuelva el estado 200
@app.route('/get_tarjeta', methods=['OPTIONS'])
def options_get_tarjeta():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, 200  # Asegúrate de que se devuelva el estado 200
@app.route('/add_tarjeta', methods=['OPTIONS'])
def options_add_tarjeta():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, 200  # Asegúrate de que se devuelva el estado 200

@app.route('/add_categoria', methods=['OPTIONS'])
def options_add_categoria():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, 200  # Asegúrate de que se devuelva el estado 200
@app.route('/get_categorias', methods=['OPTIONS'])
def options_get_categorias():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, 200  # Asegúrate de que se devuelva el estado 200

@app.route('/login', methods=['OPTIONS'])
def options_login():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, 200  # Asegúrate de que se devuelva el estado 200


@app.route('/update', methods=['OPTIONS'])
def options_usuario_updt():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, 200  # Asegúrate de que se devuelva el estado 200

@app.route('/add_friend', methods=['OPTIONS'])
def options_add_friend():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, 200  # Asegúrate de que se devuelva el estado 200

@app.route('/get_friend', methods=['OPTIONS'])
def options_get_friend():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response, 200  # Asegúrate de que se devuelva el estado 200


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=4000)
