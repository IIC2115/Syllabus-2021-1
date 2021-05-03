import json
from time import time


class MoviePtr:
    def __init__(self):
        self.movies = []
        
    def add_movie(self, movie):
        if movie not in self.movies:
            self.movies.append(movie)
    
    def num_movies(self):
        return len(self.movies)


class Genre(MoviePtr):
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name


class Actor(MoviePtr):
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def años_trayectoria(self):
        primera_pelicula = min(self.movies, key=lambda x: x.year.number)
        última_película = max(self.movies, key=lambda x: x.year.number)
        return última_película.year.number - primera_pelicula.year.number
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class Year(MoviePtr):
    def __init__(self, number):
        super().__init__()
        self.number = number
        
    def __repr__(self):
        return str(self.number)
    
    def __str__(self):
        return str(self.number)


class Movie:
    def __init__(self, title, year, cast, genres):
        self.title = title
        self.year = year
        self.cast = cast
        self.genres = genres
    
    def selfadd(self):
        self.year.add_movie(self)
        for actor in self.cast:
            actor.add_movie(self)
        for genre in self.genres:
            genre.add_movie(self)


def better_x(items: list, limit: int, key: str, reverse=False):
    if limit > len(items):
        raise IndexError()
    
    def num_movies(x):
        return x.num_movies()
    
    def años_trayectoria(x):
        return x.años_trayectoria()
    
    def base(x):  # usa el propio ítem como llave
        return x
    
    keys = []
    for item in items:
        if key == "num_movies":
            keys.append(num_movies(item))
        elif key == "años_trayectoria":
            keys.append(años_trayectoria(item))
        else:
            keys.append(base(item))
    zipped = list(zip(items, keys))
    sols = []
    sol_act: tuple = tuple()  # el linter me miraba feo :c
    sol_act = None
    while len(sols) < limit:
        for item, key in zipped:
            if sol_act is None:
                sol_act = item, key
                continue
            if reverse:
                if sol_act[1] < key:
                    sol_act = item, key
            else:
                if sol_act[1] > key:
                    sol_act = item, key
        # supuesto: sol_act no es None
        zipped.remove(sol_act)
        sols.append(sol_act)
        sol_act = None
    return sols


def selfjoin_no_repeat(lista):
    ret = []
    for i in range(len(lista)):
        for k in range(i + 1, len(lista)):
            ret.append((i, k))
    return ret


# consulta 1
def most_popular_genres(genres, limit=5, pocas_lineas=False):
    if not pocas_lineas:
        better_limit = better_x(genres, limit, "num_movies", reverse=True)
        return better_limit
    else:
        sorted_genres = sorted(genres, key=lambda x: x.num_movies(), reverse=True)
        return sorted_genres[:limit]


# consulta 2
def year_more_movies(years, limit=3, pocas_lineas=False):
    if not pocas_lineas:
        better_limit = better_x(years, limit, "num_movies", reverse=True)
        return better_limit
    else:
        sorted_years = sorted(years, key=lambda x: x.num_movies(), reverse=True)
        return sorted_years[:limit]


# consulta 3
def actores_trayectoria_más_larga(actors, limit=5, pocas_lineas=False):
    if not pocas_lineas:
        better_limit = better_x(actors, limit, "años_trayectoria", reverse=True)
        return better_limit
    else:
        sorted_actors = sorted(actors, key=lambda x: x.años_trayectoria(), reverse=True)
        return sorted_actors[:limit]


# consulta 4
def reparto_más_usado(movies, min_num_actors=2):
    # los frozensets son como los sets pero inmutables
    # por lo que se pueden usar como keys en los diccionarios
    repartos = {frozenset(mov.cast): 0 for mov in movies}
    for cast in repartos.keys():
        for mov in movies:
            if cast.issubset(mov.cast):
                repartos[cast] += 1
    return max([(i, v) for i, v in repartos.items() if len(i) >= min_num_actors], key=lambda x: x[1])


if __name__ == "__main__":
    t0 = time()
    with open("movies.json", "r", encoding="utf-8") as movies_file:
        movies = json.load(movies_file)
    t1 = time()

    obj_movies = []
    obj_years = {}
    obj_actors = {}
    obj_genres = {}

    for movie in movies:
        if movie["year"] in obj_years.keys():
            year = obj_years[movie["year"]]
        else:
            year = Year(movie["year"])
            obj_years[movie["year"]] = year
        genres = []
        for genre in movie["genres"]:
            if genre in obj_genres.keys():
                genres.append(obj_genres[genre])
            else:
                obj_genres[genre] = Genre(genre)
                genres.append(obj_genres[genre])
        actors = []
        for actor in movie["cast"]:
            if actor in obj_actors.keys():
                actors.append(obj_actors[actor])
            else:
                obj_actors[actor] = Actor(actor)
                actors.append(obj_actors[actor])
        mov = Movie(movie["title"], year, actors, genres)
        mov.selfadd()
        obj_movies.append(mov)

    t2 = time()
    print("CONSULTA 1")
    print(most_popular_genres(obj_genres.values()))
    t3 = time()
    print("\nCONSULTA 2")
    print(year_more_movies(obj_years.values()))
    t4 = time()
    print("\nCONSULTA 3")
    print(actores_trayectoria_más_larga(obj_actors.values()))
    t5 = time()
    print("\nCONSUTLA 4")
    print(reparto_más_usado(obj_movies))
    t6 = time()
    print(f"\nCargar json: {t1 - t0:.3f} s")
    print(f"Generar instancias: {t2 - t1:.3f} s")
    print(f"Consulta 1: {t3 - t2:.3f} s")
    print(f"Consulta 2: {t4 - t3:.3f} s")
    print(f"Consulta 3: {t5 - t4:.3f} s")
    print(f"Consulta 4: {t6 - t5:.3f} s")
