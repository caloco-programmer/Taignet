---PACKAGES----
CREATE OR REPLACE PACKAGE pkg_usuario as
PROCEDURE pa_add (p_name VARCHAR2,p_ap VARCHAR2,p_username VARCHAR2,p_mail VARCHAR2,p_password VARCHAR2,p_estado VARCHAR2);
PROCEDURE pa_update(p_name VARCHAR2,p_ap VARCHAR2,p_username VARCHAR2,p_mail VARCHAR2,p_password VARCHAR2,p_estado VARCHAR2,p_user_antiguo VARCHAR2);
PROCEDURE pa_delete(p_username VARCHAR2);
END;
/


CREATE OR REPLACE PACKAGE BODY pkg_usuario AS

PROCEDURE pa_add (p_name IN VARCHAR2,p_ap IN VARCHAR2,p_username IN VARCHAR2,p_mail IN VARCHAR2,p_password IN VARCHAR2,p_estado VARCHAR2) AS

BEGIN

INSERT INTO USUARIO VALUES(seq_id_usuario.NEXTVAL,p_name,p_ap,p_username,p_mail,p_password,p_estado);

END;

PROCEDURE pa_update(p_name VARCHAR2,p_ap VARCHAR2,p_username VARCHAR2,p_mail VARCHAR2,p_password VARCHAR2,p_estado VARCHAR2,p_user_antiguo VARCHAR2) AS

BEGIN

UPDATE USUARIO SET name_user = p_name, ap_user = p_ap,username = p_username,mail = p_mail,pasword=p_password,estado=p_estado WHERE username = p_user_antiguo;
END;


PROCEDURE pa_delete(p_username VARCHAR2) AS
BEGIN

DELETE FROM USUARIO WHERE username = p_username;

END;


END;
/

CREATE OR REPLACE PACKAGE pkg_amigos AS
PROCEDURE pa_ad_friend(p_friend_user VARCHAR2,p_username VARCHAR2);
PROCEDURE pa_upd_friend(p_respuesta VARCHAR2,p_friend VARCHAR2,p_username VARCHAR2); 
PROCEDURE pa_del_friend(p_friend VARCHAR2,p_username VARCHAR2);

END;
/

CREATE OR REPLACE PACKAGE BODY pkg_amigos AS

PROCEDURE pa_ad_friend(p_friend_user VARCHAR2,p_username VARCHAR2) AS
v_id_friend NUMBER(10);
v_id_user NUMBER (10);

BEGIN

SELECT id_usuario INTO v_id_user
FROM USUARIO WHERE username = p_username;

SELECT id_usuario INTO v_id_friend
FROM USUARIO WHERE username = p_friend_user;

INSERT INTO AMIGO VALUES(seq_id_amigo.NEXTVAL,v_id_user,v_id_friend,'SOLICITADO',SYSDATE);

END;

PROCEDURE pa_upd_friend(p_respuesta VARCHAR2,p_friend VARCHAR2,p_username VARCHAR2) AS
v_id_friend NUMBER(10);
v_id_user NUMBER (10);


BEGIN
SELECT id_usuario INTO v_id_friend
FROM USUARIO WHERE username = p_friend;

SELECT id_usuario INTO v_id_user
FROM USUARIO WHERE username = p_username;

IF p_respuesta = 'si' THEN
    UPDATE USUARIO SET estado = 'aceptada';
    
END IF;
IF p_respuesta = 'no' THEN
    DELETE FROM AMIGO WHERE user_id = v_id_user AND friend_id = v_id_friend;
END IF;

END;

PROCEDURE pa_del_friend(p_friend VARCHAR2,p_username VARCHAR2) AS
v_id_friend NUMBER(10);
v_id_user NUMBER (10);

BEGIN

SELECT id_usuario INTO v_id_user
FROM USUARIO WHERE username = p_username;

SELECT id_usuario INTO v_id_friend
FROM USUARIO WHERE username = p_friend;

DELETE FROM AMIGO WHERE user_id = v_id_user AND friend_id = v_id_friend;

END;

END;
/


CREATE OR REPLACE PACKAGE pkg_tarjeta AS
PROCEDURE pa_add_tarjeta (p_nombre VARCHAR2,p_username VARCHAR2,p_tipo VARCHAR2,p_cantidad NUMBER);
PROCEDURE pa_update_tarjeta(p_id_tarjeta NUMBER,p_nombre VARCHAR2,p_tipo VARCHAR2);
PROCEDURE pa_delete(p_id_tarjeta NUMBER);
END;
/

CREATE OR REPLACE PACKAGE BODY pkg_tarjeta AS
PROCEDURE pa_add_tarjeta (p_nombre VARCHAR2,p_username VARCHAR2,p_tipo VARCHAR2,p_cantidad NUMBER)  AS
v_id_user NUMBER(10);

BEGIN
SELECT id_usuario INTO v_id_user
FROM USUARIO WHERE username = p_username ;

INSERT INTO TARJETA VALUES(seq_id_tarjeta.NEXTVAL,p_nombre,v_id_user,p_tipo,p_cantidad);

END;

PROCEDURE pa_update_tarjeta (p_id_tarjeta NUMBER,p_nombre VARCHAR2,p_tipo VARCHAR2) AS

BEGIN

UPDATE TARJETA SET  id_tarjeta = id_tarjeta, nombre = p_nombre,id_usuario =id_usuario, tipo_tarjeta = p_tipo WHERE id_tarjeta = p_id_tarjeta;

END;

PROCEDURE pa_delete(p_id_tarjeta NUMBER) AS

BEGIN

 DELETE FROM TARJETA WHERE id_tarjeta = p_id_tarjeta;
END;

END;
/

CREATE OR REPLACE PACKAGE  pkg_categoria AS
PROCEDURE pa_add_categoria(p_nombre VARCHAR2,p_username VARCHAR2,p_imagen BLOB);
PROCEDURE pa_delete_categoria(p_id_cat NUMBER);
END;
/

CREATE OR REPLACE PACKAGE BODY pkg_categoria AS

PROCEDURE pa_add_categoria(p_nombre VARCHAR2,p_username VARCHAR2,p_imagen BLOB) AS

v_id_user NUMBER(10);

BEGIN
SELECT id_usuario INTO v_id_user 
FROM usuario WHERE username = p_username;

INSERT INTO CATEGORIA VALUES(seq_id_categoria.NEXTVAL,p_nombre,v_id_user,p_imagen);


END;

PROCEDURE pa_delete_categoria(p_id_cat NUMBER) AS

BEGIN

DELETE FROM CATEGORIA WHERE id_categoria = p_id_cat;

END;

END;
/

id_usuario NUMBER(10) NOT NULL,
id_categoria NUMBER(10) NOT NULL,
id_tarjeta NUMBER(10) NOT NULL,
categoria VARCHAR2(20) NOT NULL,
tipo VARCHAR(10) NOT NULL,
nombre VARCHAR2(20) NOT NULL,
total NUMBER(20) NOT NULL,
tarjeta VARCHAR2(15),
fecha_ingreso DATE NOT NULL,
fecha_vencimiento DATE NOT NULL);
CREATE OR REPLACE PACKAGE pkg_gastos AS
PROCEDURE pa_add_gasto(p_username VARCHAR2,id_categoria NUMBER,id_tarjeta NUMBER,p_nombre VARCHAR2,p_fecha VARCHAR2);

PROCEDURE pa_delete_gasto(p_id_gasto NUMBER);

END;
/

CREATE OR REPLACE PACKAGE BODY pkg_gastos AS

PROCEDURE pa_add_gasto(p_username VARCHAR2,id_categoria NUMBER,id_tarjeta NUMBER,p_nombre VARCHAR2,p_fecha VARCHAR2) AS

v_categoria VARCHAR2;


BEGIN


END;


PROCEDURE pa_delete_gasto(p_id_gasto NUMBER) AS


BEGIN


END;

END;
/




