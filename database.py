# database.py
from config import name, psw,cdir,wltloc,wlpsw,dsn 
import oracledb

try:
    with oracledb.connect(user=name,
    password=psw,dsn=dsn,config_dir=cdir,wallet_location=wltloc,wallet_password=wlpsw)  as connection:
        print("hola")
        with connection.cursor() as cursor:
            print("conecto")

            sql = """select * from USUARIO"""
            sql2="""INSERT INTO USUARIO VALUES(seq_id.NEXTVAL,'Joaquin','Torres','caloco','cakitox1@gmail.com','torres12') """
            cursor.execute(sql2)
            print(cursor.execute(sql))
            consultas = cursor.fetchall()
            print(cursor.description)
            print(consultas)
            for r in consultas:
                print("datos")
                print(r)
except Exception as ex:
    print(ex)


