from collections import defaultdict, deque


# Ejercicio 1

def calcular_max_long(parentesis):
    max_long = 0
    stack = [-1]
    for i in range(len(parentesis)):
        if parentesis[i] == "(":
            stack.append(i)
        else:
            stack.pop()
            if len(stack) == 0:
                stack.append(i)
            long_actual = i - stack[-1]
            if long_actual > max_long:
                max_long = long_actual
    return max_long


# Ejercicio 2

def crear_grafo(grafo):
    graph = defaultdict(list)
    for i, j in grafo:
        graph[i].append(j)
    return graph


def caminos_largo_m(grafo, origen, destino, m):
    if m == 0:
        if origen == destino:
            return 1
        return 0
    graph = crear_grafo(grafo)
    cola = deque([[origen]])
    num_caminos = 0
    contador = 0
    while cola:
        nodos = cola.popleft()
        if contador < m - 1:
            prox_nodos = []
            for nodo in nodos:
                prox_nodos += graph[nodo]
            if prox_nodos:
                cola.append(prox_nodos)
        else:
            for nodo in nodos:
                if destino in graph[nodo]:
                    num_caminos += 1
        contador += 1
    return num_caminos


# Solución anexa que permite mostrar los caminos

def caminos_largo_m2(grafo, origen, destino, m):
    if m == 0:
        if origen == destino:
            print([origen])
            return 1
        return 0
    graph = crear_grafo(grafo)
    cola = deque([[origen]])
    num_caminos = 0
    while cola:
        nodos = cola.popleft()
        last = nodos[-1]
        if len(nodos) < m:
            for i in graph[last]:
                cola.append(nodos + [i])
        else:
            for i in graph[last]:
                if i == destino:
                    print(nodos + [destino])
                    num_caminos += 1
    return num_caminos


if __name__ == "__main__":
    print("Ejemplo de ejecución Ej. 1")
    parentesis = "((()()"
    max_long = calcular_max_long(parentesis)
    print(max_long)
    print("Ejemplo de ejecución Ej. 2")
    grafo = [(0, 6), (0, 1), (1, 6), (1, 5), (1, 2), (2, 3), (3, 4), (5, 2), (5, 3), (5, 4), (6, 5), (7, 6), (7, 1)]
    origen = 0
    destino = 3
    m = 4
    num_caminos = caminos_largo_m(grafo, origen, destino, m)
    print(num_caminos)
    print("Ejemplo de ejecución Ej. 2 mostrando caminos (sol. anexa)")
    print(caminos_largo_m2(grafo, origen, destino, m))
