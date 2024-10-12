import cx_Oracle
import database

connection = None
try:
    connection = cx_Oracle.connect(
        config.username,
        config.password,
        config.dsn,
        encoding=config.encoding)

    # imprime la version de la base de datos
    print(connection.version)

except cx_Oracle.Error as error:
    print(error)

finally:
    # release the connection
    if connection:
        connection.close()