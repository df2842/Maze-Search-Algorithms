import random
import maze

# Create maze using Pre-Order DFS maze creation algorithm
def create_dfs(m):
    # TODO: Implement create_dfs
    stack = [random.randint(0, len(m.maze_array)-1)]
    while len(stack) != 0:
        neighbors = m.cell_neighbors(stack[-1])
        if (len(neighbors) != 0):
            target = neighbors[random.randint(0,len(neighbors)-1)]
            m.connect_cells(stack[-1], target[0], target[1])
            stack.append(target[0])
        else:
            stack.pop()
    m.refresh_maze_view()
    m.state = "solve"

def main():
    current_maze = maze.Maze('create')
    create_dfs(current_maze)
    while 1:
        maze.check_for_exit()
    return

if __name__ == '__main__':
    main()