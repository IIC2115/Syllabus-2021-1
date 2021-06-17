import sqlite3
import csv


def create_connection(path):    
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    return conn, cursor


def initialize(conn, cursor):
    cursor.execute("DROP TABLE IF EXISTS empleado;")
    cursor.execute("DROP TABLE IF EXISTS departamento;")
    cursor.execute("DROP TABLE IF EXISTS trabaja_en;")
    cursor.execute("""
    CREATE TABLE empleado(
        id INTEGER NOT NULL PRIMARY KEY,
        nombre TEXT NOT NULL,
        edad INTEGER NOT NULL,
        sueldo FLOAT NOT NULL
    );""")
    cursor.execute("""
    CREATE TABLE departamento(
        id INTEGER NOT NULL PRIMARY KEY,
        nombre TEXT NOT NULL,
        presupuesto FLOAT NOT NULL,
        id_jefe INTEGER NOT NULL,
        FOREIGN KEY(id_jefe) REFERENCES empleado(id)
    );""")
    cursor.execute("""
    CREATE TABLE trabaja_en(
        id_empleado INTEGER NOT NULL,
        id_dpto INTEGER NOT NULL,
        porcentaje_tiempo INTEGER NOT NULL,
        PRIMARY KEY (id_empleado, id_dpto),
        FOREIGN KEY (id_empleado) REFERENCES empleado(id),
        FOREIGN KEY (id_dpto) REFERENCES departamento(id)
    );""")
    
    # importamos los datos

    with open("empleados.txt", "r", encoding="utf-8") as f:
        data = csv.DictReader(f, ["id", "nombre", "edad", "sueldo"])
        for row in data:
            cursor.execute("INSERT INTO empleado(id, nombre, edad, sueldo) VALUES ('{id}', '{nombre}', '{edad}', '{sueldo}')".format(**row))

    with open("departamentos.txt", "r", encoding="utf-8") as f:
        data = csv.DictReader(f, ["id", "nombre", "presupuesto", "id_jefe"])
        for row in data:
            cursor.execute("INSERT INTO departamento(id, nombre, presupuesto, id_jefe) VALUES ('{id}', '{nombre}', '{presupuesto}', '{id_jefe}')".format(**row))

    with open("trabaja_en.txt", "r", encoding="utf-8") as f:
        data = csv.DictReader(f, ["id_empleado", "id_dpto", "porcentaje_tiempo"])
        for row in data:
            cursor.execute("INSERT INTO trabaja_en(id_empleado, id_dpto, porcentaje_tiempo) VALUES ('{id_empleado}', '{id_dpto}', '{porcentaje_tiempo}')".format(**row))
    conn.commit()


def consulta_1(cursor):
    con_1 = """
    SELECT DISTINCT e.nombre, e.edad
    FROM empleado AS e, trabaja_en AS t1, trabaja_en AS t2, departamento AS d1, departamento as d2
    WHERE (
        t1.id_empleado = e.id AND
        t2.id_empleado = e.id AND
        t1.id_dpto = d1.id AND
        t2.id_dpto = d2.id AND
        d1.id <> d2.id AND (
            d1.nombre = "Software" AND
            d2.nombre = "Hardware"
        )
    );"""
    print("consulta 1")
    for x in cursor.execute(con_1).fetchall():
        print (x)


def consulta_2(cursor):
    con_2 = """
    SELECT e.nombre
    FROM empleado AS e, departamento AS d
    WHERE e.id = d.id_jefe AND d.presupuesto = (SELECT MAX(d2.presupuesto) FROM departamento as d2);"""
    print("consulta 2")
    for x in cursor.execute(con_2).fetchall():
        print (x)


def consulta_3(cursor):
    con_3 = """
    SELECT e.nombre
    FROM empleado AS e
    WHERE e.sueldo > (
        SELECT d.presupuesto
        FROM departamento AS d, trabaja_en AS t
        WHERE d.id = t.id_dpto AND t.id_empleado = e.id
    );"""
    print("consulta 3")
    for x in cursor.execute(con_3).fetchall():
        print (x)


def consulta_4(cursor):
    con_4 = """
    SELECT x.nombre, x.num_empleados
    FROM (
        SELECT d.nombre, SUM(t.porcentaje_tiempo) AS dedicacion, COUNT(t.id_empleado) AS num_empleados
        FROM departamento AS d, trabaja_en AS t
        WHERE d.id = t.id_dpto
        GROUP BY d.id
    ) as x  -- nombre cualquiera
    WHERE x.dedicacion >= 2000;"""
    print("consulta 4")
    for x in cursor.execute(con_4).fetchall():
        print (x)


if __name__ == "__main__":
    conn, cursor = create_connection("db.db")
    initialize(conn, cursor)
    conn.commit()  # guardamos los datos en la base de datos
    
    consulta_1(cursor)
    consulta_2(cursor)
    consulta_3(cursor)
    consulta_4(cursor)
    
    cursor.close()
    conn.close()
