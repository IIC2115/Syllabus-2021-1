import json
import sqlite3
import random
import urllib.request as net
import ssl
import bs4
from typing import List, Dict
import pyrematch as re


"""
SUPUESTOS:
    1. no hay dos películas con igual título el mismo año
"""


REGEX = {
    "title": re.compile("[Tt]itle"),
    "director": re.compile("[Dd]irector"),
    "cast": re.compile("[Cc]ast"),
    "genre": re.compile("[Gg]enre"),
    "notes": re.compile("[Nn]otes"),
}


ARENT_ACTORS = [
    ".",
    "and",
    "(",
    ")",
    "the",
    "voice",
    "narrator",
    "at",
    "book",
    "narrator",
    "album",
    "uganda",
    "lgbt",
    "with",
    "s",
    "n",
    "a",
    "of",
    "dolphins",
    "common",
    "jojo",
    "abra",
    "kids",
    "sr",
    "by",
    "in",
    "on",
    "iraq",
    "none",
    "narrated by"
]

NUM_SELECTED = 10
WIKIPIDIA_URL = "https://en.wikipedia.org/wiki/List_of_American_films_of_{}"


class WebDownloader:
    def __init__(self, link):
        self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.url =  link

    def getHtmlAsString(self):
        headers = {'User-Agent':self.user_agent}
        request= net.Request(self.url,None,headers)
        gcontext = ssl.SSLContext()
        response = net.urlopen(request,context=gcontext)
        return response.read().decode('utf-8')


def dropear_tablas(cur):
    cur.execute("drop table if exists movies_genres;")
    cur.execute("drop table if exists movies_actors;")
    cur.execute("drop table if exists genres;")
    cur.execute("drop table if exists actors;")
    cur.execute("drop table if exists movies;")


def crear_tablas(cur):
    cur.execute("create table if not exists movies(id integer primary key autoincrement, title text not null, year integer not null, director text, notes text);")
    cur.execute("create table if not exists actors(id text primary key, name text not null unique);")
    cur.execute("create table if not exists genres(id integer primary key autoincrement, name text not null unique);")
    cur.execute("create table if not exists movies_actors(id_movie integer, id_actor text, foreign key (id_movie) references movies(id), foreign key (id_actor) references actors(id), primary key(id_movie, id_actor));")
    cur.execute("create table if not exists movies_genres(id_movie integer, id_genre integer, foreign key (id_movie) references movies(id), foreign key (id_genre) references genres(id), primary key(id_movie, id_genre));")


def poblar_movies(cur, data):
    query = "insert into movies(title, year) values (?, ?);"
    for i in data:
        cur.execute(query, [i["title"], i["year"]])


def poblar_actors(cur: sqlite3.Cursor, data: List[Dict[str, str]], names_dict: Dict[str, str]):
    query = "insert into actors(id, name) values (?, ?);"
    vistos = set()
    pares = set()
    for row in data:
        for i in row["cast"]:
            if i not in vistos:
                cur.execute(query, [i, list(names_dict[i])[0][2]])
                vistos.add(i)
            pares.add((row["title"], row["year"], i))  # pares película-actor
    return pares


def poblar_movies_actors(cur: sqlite3.Cursor, pares):
    query = "insert into movies_actors(id_movie, id_actor) values (?, ?)"
    q1 = "select id from movies where title = ? and year = ? limit 1"
    q2 = "select id from actors where id = ? limit 1"
    tot = len(pares)
    for i, (movie, year, actor) in enumerate(pares):
        cur.execute(q1, [movie, year])
        mov = cur.fetchone()[0]
        cur.execute(q2, [actor])
        act = cur.fetchone()[0]
        cur.execute(query, [mov, act])
        if i % 1000 == 0:
            print(f"{i}/{tot}")


def poblar_genres(cur: sqlite3.Cursor, data: List[Dict[str, str]]):
    query = "insert into genres(name) values (?);"
    vistos = set()
    pares = set()
    for row in data:
        for i in row["genres"]:
            if i not in vistos:
                cur.execute(query, [i])
                vistos.add(i)
            pares.add((row["title"], row["year"], i))
    return pares


def poblar_movies_genres(cur: sqlite3.Cursor, pares):
    query = "insert into movies_genres(id_movie, id_genre) values (?, ?);"
    q1 = "select id from movies where title = ? and year = ? limit 1;"
    q2 = "select id from genres where name = ? limit 1;"
    tot = len(pares)
    for i, (movie, year, genre) in enumerate(pares):
        cur.execute(q1, [movie, year])
        mov = cur.fetchone()[0]
        cur.execute(q2, [genre])
        gen = cur.fetchone()[0]
        cur.execute(query, [mov, gen])
        if i % 1000 == 0:
            print(f"{i}/{tot}")


def agregar_directores_y_notas(cur: sqlite3.Cursor, data: List[Dict[str, str]]):
    update_query = "update movies set director = ?, notes = ? where title = ? and year = ?;"
    for movie in data:
        movie["director"] = ""
        movie["notes"] = ""
    cur.execute("select distinct year from movies order by year;")
    años = cur.fetchall()
    for año in años:
        url = WIKIPIDIA_URL.format(año[0])
        print(url)
        dw = WebDownloader(url)
        soup = bs4.BeautifulSoup(dw.getHtmlAsString(), features="html.parser")
        tables = soup.findAll("table")
        for tab in tables:
            rows = tab.findAll("tr")
            if len(rows) == 0:
                continue
            header = rows[0].findAll("th")
            if (len(header) == 5
                and REGEX["title"].search(header[0].text)
                and REGEX["director"].search(header[1].text)
                and REGEX["cast"].search(header[2].text)
                and REGEX["genre"].search(header[3].text)
                and REGEX["notes"].search(header[4].text)
            ):
                for row in rows[1:]:
                    values = row.findAll("td")
                    for movie in data:
                        if values[0].text == movie["title"] and movie["year"] == año[0]:
                            print(movie["title"])
                            movie["director"] = values[1].text.strip()
                            try:
                                movie["notes"] = values[4].text.strip()
                            except IndexError:
                                print("\t\tnefastos... ¡skip!")
                            cur.execute(update_query, [movie["director"], movie["notes"], movie["title"], movie["year"]])


def filtrar_actores(data):
    names_dict = {}
    for k, movie in enumerate(data):
        keep = []
        nns = []
        lower = set()
        for i, name in enumerate(movie["cast"]):
            del_chars = [".", ",", "-", "–", "_", "(", ")", "[", "]", "/", "'", "\"", "?", "$"]
            nn = name.lower()
            for c in del_chars:
                nn = nn.replace(c, "")
            nn = nn.strip()
            if nn == "":
                continue
            elif nn.isdecimal():
                continue
            elif nn in ARENT_ACTORS:
                continue
            elif nn in lower:
                continue
            keep.append(i)
            lower.add(nn)
            nns.append(nn)
            names_dict[nn] = names_dict.get(nn, set())
            names_dict[nn].add((k, movie["title"], name))  # agrego el nombre al directorio
        movie["cast"] = nns
    freqs = {key: len(values) for key, values in names_dict.items()}
    for i, v in freqs.items():
        if v < 2:
            for k, mov, rname in names_dict[i]:
                data[k]["cast"].remove(i)
            del names_dict[i]
    return names_dict


def consulta_1(cur: sqlite3.Cursor):
    query = """
    select m.year, count(m.title) num_movies
    from movies m
    group by m.year
    order by num_movies desc
    limit 3;
    """
    cur.execute(query)
    return [("year", "num_movies")] + cur.fetchall()


def consulta_2(cur: sqlite3.Cursor):
    query = """
    select a.name, (max(m.year) - min(m.year)) traj
    from movies m, movies_actors ma, actors a
    where m.id = ma.id_movie and ma.id_actor = a.id
    group by a.id, a.name
    order by traj desc
    limit 5;
    """
    cur.execute(query)
    return [("name", "trajectory")] + cur.fetchall()


def consulta_3(cur: sqlite3.Cursor):
    query = """
    select
        gen_s.*,
        (
            select a.name
            from actors a
            inner join movies_actors ma on a.id = ma.id_actor
            inner join movies m on ma.id_movie = m.id
            inner join movies_genres mg on m.id = mg.id_movie
            inner join genres g on g.id = mg.id_genre
            where g.id = gen_s.id
            group by a.id, id_genre
            order by count(ma.id_movie) DESC
            limit 0,1
        ) actor_1,
        (
            select count(ma.id_movie) num_movies
            from actors a
            inner join movies_actors ma on a.id = ma.id_actor
            inner join movies m on ma.id_movie = m.id
            inner join movies_genres mg on m.id = mg.id_movie
            inner join genres g on g.id = mg.id_genre
            where g.id = gen_s.id
            group by a.id, id_genre
            order by count(ma.id_movie) DESC
            limit 0,1
        ) num_movies_a1,
        (
            select a.name
            from actors a
            inner join movies_actors ma on a.id = ma.id_actor
            inner join movies m on ma.id_movie = m.id
            inner join movies_genres mg on m.id = mg.id_movie
            inner join genres g on g.id = mg.id_genre
            where g.id = gen_s.id
            group by a.id, id_genre
            order by count(ma.id_movie) DESC
            limit 1,1
        ) actor_2,
        (
            select count(ma.id_movie) num_movies
            from actors a
            inner join movies_actors ma on a.id = ma.id_actor
            inner join movies m on ma.id_movie = m.id
            inner join movies_genres mg on m.id = mg.id_movie
            inner join genres g on g.id = mg.id_genre
            where g.id = gen_s.id
            group by a.id, id_genre
            order by count(ma.id_movie) DESC
            limit 1,1
        ) num_movies_a2,
        (
            select a.name
            from actors a
            inner join movies_actors ma on a.id = ma.id_actor
            inner join movies m on ma.id_movie = m.id
            inner join movies_genres mg on m.id = mg.id_movie
            inner join genres g on g.id = mg.id_genre
            where g.id = gen_s.id
            group by a.id, id_genre
            order by count(ma.id_movie) DESC
            limit 2,1
        ) actor_3,
        (
            select count(ma.id_movie) num_movies
            from actors a
            inner join movies_actors ma on a.id = ma.id_actor
            inner join movies m on ma.id_movie = m.id
            inner join movies_genres mg on m.id = mg.id_movie
            inner join genres g on g.id = mg.id_genre
            where g.id = gen_s.id
            group by a.id, id_genre
            order by count(ma.id_movie) DESC
            limit 2,1
        ) num_movies_a3
    from (
        select g.*, count(mg.id_movie) num_movies
        from genres g, movies_genres mg
        where g.id = mg.id_genre
        group by g.id
        order by num_movies DESC
    ) gen_s;
    """
    cur.execute(query)
    return [("id", "name", "num_movies", "actor_1", "num_movies_a1", "actor_2", "num_movies_a2", "actor_3", "num_movies_a3"), ] + cur.fetchall()


if __name__ == "__main__":
    with open("movies.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # data = random.sample(data, 1000)  # nos quedamos con 1000 películas aleatorias
    names_dict = filtrar_actores(data)    
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    dropear_tablas(cur)
    print("tablas dropeadas")
    crear_tablas(cur)
    print("tablas creadas")
    poblar_movies(cur, data)
    print("películas pobladas")
    agregar_directores_y_notas(cur, data)
    print("directores y notas agregadas!")
    pares = poblar_actors(cur, data, names_dict)
    print("actores poblados")
    poblar_movies_actors(cur, pares)
    print("películas y actores asociados")
    pares = poblar_genres(cur, data)
    print("géneros poblados")
    poblar_movies_genres(cur, pares)
    print("películas y géneros asociados")
    con.commit()
    print("empezando consultas...")
    print("======= RESULTADO CONSULTA 1 =======")
    r1 = consulta_1(cur)
    print(*r1, sep="\n")
    print("\n======= RESULTADO CONSULTA 2 =======")
    r2 = consulta_2(cur)
    print(*r2, sep="\n")
    print("\n======= RESULTADO CONSULTA 3 =======")
    r3 = consulta_3(cur)
    print(*r3, sep="\n")
