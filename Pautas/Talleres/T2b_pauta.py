from collections import defaultdict


class Nodo:

    def __init__(self):
        self.izq = None
        self.der = None

    def agregar_izq(self, izq):
        self.izq = izq

    def agregar_der(self, der):
        self.der = der

    def obtener_izq(self):
        return self.izq

    def obtener_der(self):
        return self.der


def crear_nodo():
    return Nodo()


class ArbolBinario:

    def __init__(self):
        self.nodos = defaultdict(crear_nodo)
        self.raiz = None

    def agregar_nodos(self, padre, izq, der):
        if izq is not None:
            self.nodos[padre].agregar_izq(self.nodos[izq])
        if der is not None:
            self.nodos[padre].agregar_der(self.nodos[der])

    def agregar_raiz(self, raiz, izq, der):
        self.raiz = self.nodos[raiz]
        if izq is not None:
            self.nodos[raiz].agregar_izq(self.nodos[izq])
        if der is not None:
            self.nodos[raiz].agregar_der(self.nodos[der])

    def obtener_raiz(self):
        return self.raiz


def profundidad_arbol_binario(arbol):
    arbol_binario = ArbolBinario()
    raiz, izq, der = arbol[0]
    arbol_binario.agregar_raiz(raiz, izq, der)
    for i in range(1, len(arbol)):
        padre, izq, der = arbol[i]
        arbol_binario.agregar_nodos(padre, izq, der)
    return profundidad_arbol_binario_recursivo(arbol_binario.obtener_raiz())


def profundidad_arbol_binario_recursivo(nodo):
    if nodo is None:
        return -1
    l_arbol_izq = profundidad_arbol_binario_recursivo(nodo.obtener_izq())
    l_arbol_der = profundidad_arbol_binario_recursivo(nodo.obtener_der())
    if (l_arbol_izq > l_arbol_der):
        return l_arbol_izq + 1
    return l_arbol_der + 1


def grupos_estudio(puntajes, K):
    grupos = [[] for i in range(K)]
    suma_puntajes = sum(puntajes)
    if suma_puntajes % K != 0:
        return grupos
    target = sum(puntajes) // K
    sumas_grupos = [0]*K
    grupos_estudio_backtracking(puntajes, sumas_grupos, grupos, target)
    return grupos


def grupos_estudio_backtracking(puntajes, sumas_grupos, grupos, target):
    if not puntajes:
        return True
    pos = len(puntajes)-1
    puntaje = puntajes.pop()
    for i, suma_actual in enumerate(sumas_grupos):
        if suma_actual + puntaje <= target:
            sumas_grupos[i] += puntaje
            grupos[i].append(pos)
            if grupos_estudio_backtracking(puntajes, sumas_grupos, grupos, target):
                return True
            sumas_grupos[i] -= puntaje
            grupos[i].pop()
        if not suma_actual:
            break
    puntajes.append(puntaje)
    return False


if __name__ == "__main__":
    arbol = [(0, 1, 2), (4, None, 6), (1, 3, None), (2, 4, 5)]
    profundidad = profundidad_arbol_binario(arbol)
    print(profundidad)
    puntajes = [7, 3, 5, 12, 2, 1, 5, 3, 8, 4, 6, 4]
    K = 5
    grupos = grupos_estudio(puntajes, K)
    print(grupos)
