import numpy as np
import heapq
import networkx as nx
import matplotlib.pyplot as plt

# Adapt code from https://www.geeksforgeeks.org/a-algorithm-and-its-heuristic-search-strategy-in-artificial-intelligence/

WALL = 5

# Convert grid to graph: only connect if neighbor is not a wall
def grid_to_graph(grid):
    graph = {}
    rows, cols = grid.shape
    for x in range(rows):
        for y in range(cols):
            if grid[x, y] == WALL:
                continue
            neighbors = {}
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx_, ny_ = x + dx, y + dy
                if 0 <= nx_ < rows and 0 <= ny_ < cols and grid[nx_, ny_] != WALL:
                    neighbors[(nx_, ny_)] = grid[nx_, ny_]
            graph[(x, y)] = neighbors
    return graph

# Heuristic function
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# A* algorithm function
def a_star(grid, start, goals):
    graph = grid_to_graph(grid)
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph}
    
    goal_set = set(goals)  # multiple goals
    f_score[start] = min(heuristic(start, g) for g in goals)

    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current not in graph:
            continue  # skip invalid or wall positions

        if current in goal_set:
            return reconstruct_path(came_from, current), current

        for neighbor, cost in graph[current].items():
            tentative_g = g_score[current] + cost
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + min(heuristic(neighbor, g) for g in goals)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))


    return [], None


# Reconstruct the path from start to goal
def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


# Get the path from A* algorithm
#path = a_star(graph, start, goal)
