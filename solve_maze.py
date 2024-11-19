import maze
import generate_maze
import sys
import random

# Solve maze using Pre-Order DFS algorithm, terminate with solution
def solve_dfs(m):
    # TODO: Implement solve_dfs
    stack = [0]
    while not len(m.maze_array) - 1 in stack:
        neighbors = m.cell_neighbors(stack[-1])
        if len(neighbors) != 0:
            target = neighbors[random.randint(0, len(neighbors) - 1)]
            m.visit_cell(stack[-1], target[0], target[1])
            stack.append(target[0])
            m.refresh_maze_view()
        else:
            m.backtrack(stack[-1])
            stack.pop()
    m.refresh_maze_view()

# Solve maze using BFS algorithm, terminate with solution
def solve_bfs(m):
    # TODO: Implement solve_bfs
    queue = [0]
    while not len(m.maze_array) - 1 in queue:
        neighbors = m.cell_neighbors(queue[0])
        if len(neighbors) > 0:
            for neighbor in neighbors:
                m.bfs_visit_cell(neighbor[0], neighbor[1])
                queue.append(neighbor[0])
                m.refresh_maze_view()
        queue.pop(0)
    m.reconstruct_solution(len(m.maze_array) - 1)
    m.refresh_maze_view()

# Solve maze using IDS algorithm, terminate with solution
def solve_ids(m, t, i):
    # TODO: Implement solve_ids
    stack = [0]
    counter = 0
    while not len(m.maze_array) - 1 in stack:
        if len(stack) == 0:
            stack.append(0)
            t += i
            m.ids_clear_maze()
            m.refresh_maze_view()
        neighbors = m.cell_neighbors(stack[-1])
        if len(neighbors) != 0 and counter < t:
            target = neighbors[random.randint(0, len(neighbors) - 1)]
            m.visit_cell(stack[-1], target[0], target[1])
            stack.append(target[0])
            m.refresh_maze_view()
            counter += 1
        elif len(neighbors) != 0 or m.ids_backtrack_cell_neighbors(stack[-1]):
            m.ids_backtrack(stack[-1], False)
            stack.pop()
            counter -= 1
        else:
            m.ids_backtrack(stack[-1], True)
            stack.pop()
            counter -= 1
    m.refresh_maze_view()

# Eliminates visual dead-ends  
def eliminate_dead_ends(m):
    # TODO: Eliminate dead-ends using number of wall bits
    stack = []
    for cell in range (1, len(m.maze_array) - 1):
        if m.maze_array[cell] & 0b0000000000001111 in [1, 2, 4, 8]:
            current = cell
            while len(m.cell_neighbors(current)) <= 2 and current != 0 and current != len(m.maze_array) - 1:
                for neighbor in m.cell_neighbors(current):
                    if not neighbor[0] in stack:
                        stack.append(current)
                        current = neighbor[0]
    m.eliminate_cells(stack)

def print_solution_array(m):
    solution = m.solution_array()
    print('Solution ({} steps): {}'.format(len(solution), solution))

def main(elim=False, solver='bfs'):
    current_maze = maze.Maze('create')
    generate_maze.create_dfs(current_maze)
    if elim:
        eliminate_dead_ends(current_maze)
    if solver == 'dfs':
        solve_dfs(current_maze)
    elif solver == 'bfs':
        solve_bfs(current_maze)
    elif solver == 'ids':
        solve_ids(current_maze, current_maze.w_cells * 2.5, current_maze.h_cells * 1.5)
    while 1:
        maze.check_for_exit()
    return

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()