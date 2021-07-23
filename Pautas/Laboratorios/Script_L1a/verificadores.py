## pauta.py
### Este archivo es parte del Corrector automatico 
### de entregas de laboratorio desarrollado para el 
### curso IIC2115. Este archivo debe contener:
##### - Soluciones a cada uno de los problemas
##### - Funciones generadores de inputs
##### - Funciones de verificacion de respuesta correcta
### Francisco Garrido-Valenzuela 2020
import random # no borrar
from typing import Dict, List, Tuple
import json
import config

INPUTS_PATH: Dict[str, str] = config.INPUTS_PATH
# FORMATOS:
## Todo lo qu este entre [], debe ser modificado en cada caso

## SOLUCIONES
### def [nombre_problema](input1, input2, ..., inputn):
###     # solucion
###     return resp

## INPUTS
### def inputs_[problem_code](size, seed, index):
###     # generacion
###     return [input1, input2, ..., inputn]

## VERIFICADORES
### def verificar_[problem_code](resp, inputs)
###     correcta = [nombre_problema](*inputs)
###         if resp == correcta:
###             return 1
###         else:
###             return 0

####################
#### SOLUCIONES ####
####################

# Imports necesarios en solucion de problemas

######## Problema 1 #########

class GraphP1:
    def __init__(self, edges, N):
        self.adj_list = [[] for _ in range(N)]
        for (src, dest) in edges:
            self.adj_list[src].append(dest)
            self.adj_list[dest].append(src)

    def is_safe(self, color, v, c):
        for u in self.adj_list[v]:
            if color[u] == c:
                return False
        return True

    def k_colorable(self, color, k, v, N, COLORS):
        if v == N:
            return [COLORS[color[v]] for v in range(N)]
        for c in range(k):
            if self.is_safe(color, v, c):
                color[v] = c
                color_ret = self.k_colorable(color, k, v + 1, N, COLORS)
                if color_ret:
                    return color_ret
                color[v] = 0
        return None


def transformar_en_grafo(lineas, combinaciones):
    nodes = {i: v for i, v in enumerate(lineas)}
    quick_index = {}
    edges = set()
    for i in range(len(lineas)):
        for k in lineas[i]:
            quick_index[k] = i
    for e1, e2 in combinaciones:
        n1 = quick_index[e1]
        n2 = quick_index[e2]
        if n1 == n2:
            # print("THIS IS PAUTA!")
            # print(lineas)
            # print(combinaciones)
            raise Exception("Error de construcción del grafo!!")
        edges.add((n1, n2))
    return nodes, list(edges)


def asignar_colores(lineas, combinaciones, verbose=False):
    nodes, edges = transformar_en_grafo(lineas, combinaciones)
    COLORS = list(range(len(nodes)))
    g = GraphP1(edges, len(nodes))
    for k in range(1, len(nodes) + 1):
        colors = [None] * len(nodes)
        asignaciones = g.k_colorable(colors, k, 0, len(nodes), COLORS)
        if asignaciones:
            return asignaciones

#############################

######## Problema 2 #########

# Below lists detail all eight possible movements from a cell
row = [-1, -1, -1, 0, 0, 1, 1, 1]
col = [-1, 0, 1, -1, 1, -1, 0, 1]

# Function to check if it is possible to go to position next
# from the current position. The function returns false if next is
# not in a valid position, or it is already visited
def p2_move_is_valid(x, y, path, M, N):
    return (0 <= x < M) and (0 <= y < N) and (x, y) not in path


def DFS(mat, word, i, j, path, index, bucket_results):
    # return if characters don't match
    if mat[i][j] != word[index]:
        return
    # if all words are matched, print the result and return
    if index == len(word) - 1:
        bucket_results.append(path.copy() + [(i, j)])
        return
    # include the current cell in the path
    path.append((i, j))
    # check all eight possible movements from the current cell
    # and recur for each valid movement
    for k in range(8):
        # check if it is possible to go to the next position
        # from the current position
        if p2_move_is_valid(i + row[k], j + col[k], path, len(mat), len(mat[0])):
            DFS(mat, word, i + row[k], j + col[k], path, index + 1, bucket_results)
    # backtrack: remove the current cell from the path
    path.pop()


def encontrar_ocurrencias(sopa, texto):
    path = []
    bucket = []
    for i in range(len(sopa)):
        for j in range(len(sopa[0])):
            DFS(sopa, texto, i, j, path, 0, bucket)
    return bucket

#############################

######## Problema 3 #########

class Job:
    def __init__(self, taskID, deadline, profit):
        self.taskID = taskID
        self.deadline = deadline
        self.profit = profit
    
    def __repr__(self):
        return f"{self.taskID:>3} {self.deadline:>3} {self.profit:>3}"


# Function to schedule jobs to maximize profit
def schedule_jobs(jobs, T):
    # stores the maximum profit that can be earned by scheduling jobs
    profit = 0
    # list to store used and unused slots info
    slot = [-1] * T
    # arrange the jobs in decreasing order of their profits
    jobs.sort(key=lambda x: x.profit, reverse=True)
    # consider each job in decreasing order of their profits
    for job in jobs:
        # search for the next free slot and map the task to that slot
        for j in reversed(range(job.deadline)):
            if j < T and slot[j] == -1:
                slot[j] = job.taskID
                profit += job.profit
                break
    scheduled_jobs = list(filter(lambda x: x != -1, slot))
    return profit, scheduled_jobs


def programar_evaluaciones(evaluaciones) -> Tuple[List[str], float]:
    jobs = {evaluacion[0]: Job(*evaluacion) for evaluacion in evaluaciones}
    T = len(jobs.keys())
    _, scheduled_jobs = schedule_jobs(list(jobs.values()), T)
    nota = 0
    ponds = 0
    sch_jobs_set = set(scheduled_jobs)
    for name, job in jobs.items():
        if name in sch_jobs_set:
            nota += 1 * job.profit
        ponds += job.profit
    nota /= ponds
    nota = round(nota, 2)
    return scheduled_jobs, nota

#############################

######## Problema 4 #########

# A class to represent a graph object
class GraphP4:
    # Constructor
    def __init__(self, edges, N):
        # A list of lists to represent an adjacency list
        self.adjList = [[] for _ in range(N)]
        # stores in-degree of a vertex
        # initialize in-degree of each vertex by 0
        self.indegree = [0] * N
        # add edges to the undirected graph
        for (src, dest) in edges:
            # add an edge from source to destination
            self.adjList[src].append(dest)
            # increment in-degree of destination vertex by 1
            self.indegree[dest] = self.indegree[dest] + 1

# Recursive function to find all topological orderings of a given DAG
def p4_findAllTopologicalOrders(graph, path, discovered, N, ret):
    # do for every vertex
    for v in range(N):
        # proceed only if the current node's in-degree is 0 and
        # the current node is not processed yet
        if graph.indegree[v] == 0 and not discovered[v]:
            # for every adjacent vertex `u` of `v`, reduce the in-degree of `u` by 1
            for u in graph.adjList[v]:
                graph.indegree[u] = graph.indegree[u] - 1
            # include the current node in the path and mark it as discovered
            path.append(v)
            discovered[v] = True
            # recur
            p4_findAllTopologicalOrders(graph, path, discovered, N, ret)
            # backtrack: reset in-degree information for the current node
            for u in graph.adjList[v]:
                graph.indegree[u] = graph.indegree[u] + 1
            # backtrack: remove the current node from the path and
            # mark it as undiscovered
            path.pop()
            discovered[v] = False
    # print the topological order if all vertices are included in the path
    if len(path) == N:
        ret.append(path.copy())

class NodeP4:
    def __init__(self, id_, neighbours):
        self.id_ = id_
        self.neighbours = neighbours
        self.u = 0
        self.v = 0
        self.parent = None
        self.color = 0  # 0, 1 or 2
    
    def __repr__(self):
        return f"Node(id: {self.id_}, neigbours: {self.neighbours}, u: {self.u}, v: {self.v}, parent: {self.parent}, color: {self.color})"


class NodedGraphP4:
    def __init__(self, graph: GraphP4):
        self.nodes = [NodeP4(i, v) for i, v in enumerate(graph.adjList)]
    
    def reverse_edges(self):
        new_neigbours = [[] for _ in range(len(self.nodes))]
        for node in self.nodes:
            for nei in node.neighbours:
                new_neigbours[nei].append(node.id_)
        for n, v in zip(self.nodes, new_neigbours):
            n.neighbours = v
    
    def __repr__(self):
        return str(self.nodes)
    
    def print(self):
        print(*self.nodes, sep="\n")


def find_all_cfcs(graph):
    graph.reverse_edges()
    cfcs = []
    watched = set()
    actual_cfc = []
    for current in sorted(graph.nodes, key=lambda x: x.v, reverse=True):
        if current.id_ in watched:
            continue
        if list(filter(lambda x: (graph.nodes[x].v <= current.v and x not in watched) or x in actual_cfc, current.neighbours)):
            actual_cfc.append(current.id_)
            watched.add(current.id_)
        while True:
            try:
                nex = max(
                    filter(
                        lambda x: any(map(lambda y: y in graph.nodes[x].neighbours and x not in watched, actual_cfc)) or (graph.nodes[x].v <= current.v and x not in watched), 
                        current.neighbours), 
                    key=lambda x: graph.nodes[x].v)
                watched.add(nex)
                actual_cfc.append(nex)
                current = graph.nodes[nex]
            except ValueError:
                if len(actual_cfc):
                    cfcs.append(actual_cfc)
                    actual_cfc = []
                break
    return cfcs


def p4_recursive_dfs(graph, n_i=0, parent=0, timer=0, is_ciclic=False):
    node = graph.nodes[n_i]
    if node.color == 2:
        return timer - 1, is_ciclic
    elif node.color == 1:
        return timer - 1, True
    else:
        node.parent = parent
        node.color = 1  # lo abro
        node.u = timer
        for vecino in node.neighbours:
            timer, is_ciclic = p4_recursive_dfs(graph, vecino, n_i, timer + 1, is_ciclic)
        node.v = timer + 1
        node.color = 2  # lo cierro
    return timer + 1, is_ciclic


def solve_problem_4(edges, N):
    graph = GraphP4(edges, N)
    ngraph = NodedGraphP4(graph)
    timer = 1
    is_ciclic = False
    for node in ngraph.nodes:
        if node.color == 0:
            timer, is_ciclic = p4_recursive_dfs(ngraph, node.id_, node.id_, timer, is_ciclic)
    if is_ciclic:
        cfcs = find_all_cfcs(ngraph)
        return None, cfcs
    else:
        path = []
        discovered = [False] * N
        topos = []
        p4_findAllTopologicalOrders(graph, path, discovered, N, topos)
        return topos, None


def num_personas(relaciones):
    sup = set()
    for i in relaciones:
        sup.update(i)
    return len(sup)


def ordenes_vacunacion(relaciones):
    N = num_personas(relaciones)
    tops, cfcs = solve_problem_4(relaciones, N)
    if tops:
        return tops
    else:
        sup = set()
        for i in cfcs:
            sup.update(i)
        return sorted(sup)

#############################

################
#### INPUTS ####
################

def inputs_p1(size, seed, i):
    with open(INPUTS_PATH["p1"], "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[str(size)][i - 1]["input"]

def inputs_p2(size, seed, i):
    with open(INPUTS_PATH["p2"], "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[str(size)][i - 1]["input"]

def inputs_p3(size, seed, i):
    with open(INPUTS_PATH["p3"], "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[str(size)][i - 1]["input"]


def inputs_p4(size, seed, i):
    with open(INPUTS_PATH["p4"], "r", encoding="utf-8") as f:
        data = json.load(f)
    raw = data[str(size)][i - 1]["input"][0]
    return [[tuple(i) for i in raw]]

#######################
#### VERIFICADORES ####
#######################

def verificar_p1(resp, inputs):
    if resp is None:
        return 0
    correcta_posible = asignar_colores(*inputs)
    colores = set(correcta_posible)
    colores_resp = set(resp)
    if len(colores_resp) > len(colores):  # si tiene más colores, F
        return 0
    # ahora tengo que verificar que lo haya pintado bien
    nodes, edges = transformar_en_grafo(*inputs)
    g = GraphP1(edges, len(nodes))
    aj = g.adj_list
    for nodo, vecinos in enumerate(aj):
        c1 = resp[nodo]
        for vecino in vecinos:
            if c1 == resp[vecino] and nodo != vecino:
                return 0
    return 1    


def verificar_p2(resp, inputs):
    if resp is None:
        return 0
    # print(repr(inputs))
    # pueden estar en desorden, pero no faltar ni sobrar ninguna
    r = set(map(tuple, resp))
    if len(r) != len(resp):  # tenía repetidos
        return 0
    correcta = set(map(tuple, encontrar_ocurrencias(*inputs)))
    # print("correcta:", repr(correcta))
    # print("alumno:", repr(resp))
    if r == correcta:
        return 1
    else:
        return 0


def verificar_p3(resp, inputs):
    if resp is None:
        return 0
    # las notas deben ser iguales
    # el orden global debe ser el mismo, pero...
    # para tareas de igual profit dentro del plazo
    # el orden puede ser distinto
    # podría tener otras tareas, pero que respeten los límites.
    jobs = {evaluacion[0]: Job(*evaluacion) for evaluacion in inputs[0]}
    correcta = programar_evaluaciones(*inputs)
    if abs(correcta[1] - resp[1]) > 1e-6:  # si las notas no coinciden, F
        return 0
    # calculemos que la nota esté bien calculada
    nota = 0
    ponds = 0
    for name, job in jobs.items():
        if name in resp[0]:
            nota += 1 * job.profit
        ponds += job.profit
    nota /= ponds
    nota = round(nota, 2)
    # revisamos que la nota esté bien calculada
    if abs(nota - correcta[1]) > 1e-6:
        return 0
    # calculemos que los plazos estén bien
    for i, tarea in enumerate(resp[0]):
        if i + 1 > jobs[tarea].deadline:  # deadlines parten en 1
            return 0
    return 1


def verificar_p4(resp, inputs):
    if resp is None:
        return 0
    # print(repr(inputs))
    correcta = ordenes_vacunacion(*inputs)
    # print("Correcta:", correcta)
    # print("Alumno:", resp)
    if isinstance(correcta[0], int) and isinstance(resp[0], int):  # CFCs
        cset = set(correcta)
        rset = set(resp)
    elif isinstance(correcta[0], list) and isinstance(resp[0], list):   # TOPS
        cset = set(map(tuple, correcta))  # pueden estar en desorden
        rset = set(map(tuple, resp))      # pero los ordenes, ordenados
    else:
        return 0
    if len(rset) != len(resp):
        return 0  # había repetidos!!!
    if len(cset) != len(correcta):
        raise Exception("PAUTA ERROR!!!")  # por si acaso
    if cset == rset:
        return 1
    else:
        return 0
