import pygame
import sys

# Screen size and cell size used by the maze window
# Width and height of SCREEN_SIZE should be divisible by CELL_SIZE
SCREEN_SIZE = (1280, 960)
CELL_SIZE = 8

# Some useful numbers needed for the bit manipulation
# Left-most 4 bits store backtrack path, next 4 bits solution,
# next 4 bits border and last 4 bits walls knocked down.
# From left to right, each 4 bit cluster represents W, S, E, N
# NOTE: Border bits are not currently used
#                   directions
#                WSENWSENWSENWSEN
DEFAULT_CELL = 0b0000000000000000
#                |bt||s ||i ||w |
WALL_BITS = 0b0000000000001111
BACKTRACK_BITS = 0b1111000000000000
SOLUTION_BITS = 0b0000111100000000
IDS_BITS = 0b0000000011110000

# Indices match each other
# WALLS[i] corresponds with COMPASS[i], DIRECTION[i], and OPPOSITE_WALLS[i]
WALLS = [0b1000, 0b0100, 0b0010, 0b0001]
OPPOSITE_WALLS = [0b0010, 0b0001, 0b1000, 0b0100]
COMPASS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
DIRECTION = ['W', 'S', 'E', 'N']

# Colors
BLACK = (0, 0, 0, 255)
NO_COLOR = (0, 0, 0, 0)
WHITE = (255, 255, 255, 255)
GREEN = (0, 255, 0, 255)
RED = (255, 0, 0, 255)
LIGHT_RED = (255, 0, 0, 100)
BLUE = (0, 0, 255, 255)
LIGHT_BLUE = (0, 0, 255, 100)
PURPLE = (150, 0, 150, 255)
YELLOW = (255, 255, 0, 255)
GRAY = (235, 235, 235, 255)


class Maze:
    def __init__(self, initial_state='idle'):
        # Maze set up
        self.state = initial_state
        self.w_cells = int(SCREEN_SIZE[0] / CELL_SIZE)
        self.h_cells = int(SCREEN_SIZE[1] / CELL_SIZE)
        self.total_cells = self.w_cells * self.h_cells
        self.maze_array = [DEFAULT_CELL] * self.total_cells

        # Pygame set up
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.background = pygame.Surface(self.screen.get_size())
        self.m_layer = pygame.Surface(self.screen.get_size())
        self.s_layer = pygame.Surface(self.screen.get_size())
        self.setup_maze_window()

    # Return cell neighbors within bounds of the maze
    # Use self.state to determine which neighbors should be included
    def cell_neighbors(self, cell):
        # TODO: Logic for getting neighbors based on self.state
        neighbors = []
        (x, y) = self.x_y(cell)
        for i in range (len(COMPASS)):
            neighborIndex = self.cell_index((x, y)[0] + COMPASS[i][0], (x, y)[1] + COMPASS[i][1])
            if self.state == "create":
                if self.cell_in_bounds((x, y)[0] + COMPASS[i][0], (x, y)[1] + COMPASS[i][1]) and self.maze_array[neighborIndex] & WALL_BITS == 0:
                    neighbors.append((neighborIndex, i))
            if self.state == "solve":
                if self.cell_in_bounds((x, y)[0] + COMPASS[i][0], (x, y)[1] + COMPASS[i][1]) and self.maze_array[neighborIndex] & BACKTRACK_BITS == 0 and self.maze_array[neighborIndex] & SOLUTION_BITS == 0 and self.maze_array[cell] & WALLS[i] != 0 and self.maze_array[neighborIndex] & OPPOSITE_WALLS[i] != 0:
                    neighbors.append((neighborIndex, i))
        return neighbors

    # Connect two cells by knocking down the wall between them
    # Update wall bits of from_cell and to_cell
    def connect_cells(self, from_cell, to_cell, compass_index):
        # TODO: Logic for updating cell bits
        self.maze_array[from_cell] = self.maze_array[from_cell] | WALLS[compass_index]
        self.maze_array[to_cell] = self.maze_array[to_cell] | OPPOSITE_WALLS[compass_index]
        self.draw_connect_cells(from_cell, compass_index)

    # Visit a cell along a possible solution path
    # Update solution bits of from_cell and backtrack bits of to_cell
    def visit_cell(self, from_cell, to_cell, compass_index):
        # TODO: Logic for updating cell bits
        self.maze_array[from_cell] = self.maze_array[from_cell] & 0b1111000011111111
        self.maze_array[from_cell] = self.maze_array[from_cell] | (WALLS[compass_index] << 8)
        self.maze_array[to_cell] = self.maze_array[to_cell] | (OPPOSITE_WALLS[compass_index] << 12)
        if from_cell != 0:
            self.draw_visited_cell(from_cell)

    # Backtrack from cell
    # Blank out the solution bits so it is no longer on the solution path
    def backtrack(self, cell):
        # TODO: Logic for updating cell bits
        self.maze_array[cell] = self.maze_array[cell] & 0b1111000011111111
        if cell != 0:
            self.draw_backtracked_cell(cell)

    # Visit cell in BFS search
    # Update backtrack bits for use in reconstruct_solution
    def bfs_visit_cell(self, cell, from_compass_index):
        # TODO: Logic for updating cell bits
        self.maze_array[cell] = self.maze_array[cell] | (OPPOSITE_WALLS[from_compass_index] << 12)
        if cell != 0 and cell != len(self.maze_array) - 1:
            self.draw_bfs_visited_cell(cell)

    # Reconstruct path to start using backtrack bits
    def reconstruct_solution(self, cell):
        if cell != len(self.maze_array) - 1 and cell != 0:
            self.draw_visited_cell(cell)
            self.refresh_maze_view()
        # TODO: Logic for reconstructing solution path in BFS
        if cell != 0:
            backtrack = int((self.maze_array[cell] & 0b1111000000000000) / 0b1000000000000)
            index = WALLS.index(backtrack)
            neighbor = self.cell_index(self.x_y(cell)[0] + COMPASS[index][0], self.x_y(cell)[1] + COMPASS[index][1])
            self.reconstruct_solution(neighbor)
    
    # Backtrack from cell
    # Blank out the solution bits so it is no longer on the solution path
    # Update IDS backtrack bits for permanently eliminated cells
    def ids_backtrack(self, cell, perm):
        # TODO: Logic for updating cell bits
        if not perm:
            self.maze_array[cell] = self.maze_array[cell] & 0b1111000011111111
            self.maze_array[cell] = self.maze_array[cell] | 0b0000000011000000
            if cell != 0:
                self.draw_ids_backtracked_cell(cell)
        else:
            self.maze_array[cell] = self.maze_array[cell] & 0b1111000011111111
            self.maze_array[cell] = self.maze_array[cell] | 0b0000000000110000
            if cell != 0:
                self.draw_backtracked_cell(cell)

    # Returns boolean based on whether a cell has IDS backtracked neighbors
    def ids_backtrack_cell_neighbors(self, cell):
        # TODO: Logic for getting neighbors based IDS backtrack bits
        (x, y) = self.x_y(cell)
        for i in range (len(COMPASS)):
            neighborIndex = self.cell_index((x, y)[0] + COMPASS[i][0], (x, y)[1] + COMPASS[i][1])
            if self.cell_in_bounds((x, y)[0] + COMPASS[i][0], (x, y)[1] + COMPASS[i][1]) and self.maze_array[cell] & WALLS[i] != 0 and self.maze_array[neighborIndex] & OPPOSITE_WALLS[i] != 0 and self.maze_array[neighborIndex] & 0b0000000011110000 == 192:
                return True
        return False

    # Clear maze for next search iteration
    # Clear all cell colors except for IDS eliminated cells
    # Set all backtrack bits and solution bits to 0000 except for IDS eliminated cells
    def ids_clear_maze(self):
        # TODO: Logic for clearing cell bits
        for cell in range(1, len(self.maze_array) - 1):
            if self.maze_array[cell] & 0b0000000011110000 != 48:
                self.maze_array[cell] = self.maze_array[cell] & 0b0000000000001111
                self.clear_ids_visited_cell(cell)

    # Eliminates cells in dead-ends
    # Updates backtrack bits, solution bits, and IDS bits 
    def eliminate_cells(self, cells):
        # TODO: Logic for updating backtrack bits, solution bits, and IDS bits
        for cell in cells:
            self.maze_array[cell] = self.maze_array[cell] | 0b1111111100110000
            # self.draw_eliminated_cell(cell)
            # self.refresh_maze_view()

    # Check if x, y values of cell are within bounds of maze
    def cell_in_bounds(self, x, y):
        return ((x >= 0) and (y >= 0) and (x < self.w_cells)
                and (y < self.h_cells))

    # Cell index from x, y values
    def cell_index(self, x, y):
        return y * self.w_cells + x

    # x, y values from a cell index
    def x_y(self, index):
        x = index % self.w_cells
        y = int(index / self.w_cells)
        return x, y

    # x, y point values from a cell index
    def x_y_pos(self, index):
        x, y = self.x_y(index)
        x_pos = x * CELL_SIZE
        y_pos = y * CELL_SIZE
        return x_pos, y_pos

    # Build solution array using solution bits
    # Use DIRECTION to return cardinal directions representing solution path
    def solution_array(self):
        solution = []

        # TODO: Logic to return cardinal directions representing solution path

        return solution

    # 'Knock down' wall between two cells, use in creation as walls removed
    def draw_connect_cells(self, from_cell, compass_index):
        x_pos, y_pos = self.x_y_pos(from_cell)
        if compass_index == 0:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos, y_pos + 1),
                             (x_pos, y_pos + CELL_SIZE - 1))
        elif compass_index == 1:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos + 1,
                             y_pos + CELL_SIZE), (x_pos + CELL_SIZE - 1,
                             y_pos + CELL_SIZE))
        elif compass_index == 2:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos + CELL_SIZE,
                             y_pos + 1), (x_pos + CELL_SIZE,
                             y_pos + CELL_SIZE - 1))
        elif compass_index == 3:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos + 1, y_pos),
                             (x_pos + CELL_SIZE - 1, y_pos))

    # Draw green square at cell, use to visualize solution path being explored
    def draw_visited_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, GREEN, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))

    # Draws a red square at cell, use to change cell to visualize backtrack
    def draw_backtracked_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, RED, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))

    # Draw green square at cell, use to visualize solution path being explored
    def draw_bfs_visited_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, LIGHT_BLUE, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))
    
    # Clear color at cell, use to visualize new IDS iteration
    def clear_ids_visited_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, NO_COLOR, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))

    # Draw light blue square at cell, use to change cell to visualize non-permanent IDS backtrack
    def draw_ids_backtracked_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, LIGHT_BLUE, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))
    
    # Draw gray square at cell, use to visualize eliminated dead-end
    def draw_eliminated_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, GRAY, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))

    # Process events, add each layer to screen (blip) and refresh (flip)
    # Call this at the end of each traversal step to watch the maze as it is
    # generated. Skip call until end of creation/solution to make faster.
    def refresh_maze_view(self):
        check_for_exit()
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.s_layer, (0, 0))
        self.screen.blit(self.m_layer, (0, 0))
        pygame.display.flip()

    def setup_maze_window(self):
        # Set up window and layers
        pygame.display.set_caption('Maze Generation and Solving')
        pygame.mouse.set_visible(0)
        self.background = self.background.convert()
        self.background.fill(WHITE)
        self.m_layer = self.m_layer.convert_alpha()
        self.m_layer.fill(NO_COLOR)
        self.s_layer = self.s_layer.convert_alpha()
        self.s_layer.fill(NO_COLOR)

        # Draw grid lines (will be whited out as walls knocked down)
        for y in range(self.h_cells + 1):
            pygame.draw.line(self.m_layer, BLACK, (0, y * CELL_SIZE),
                             (SCREEN_SIZE[0], y * CELL_SIZE))
        for x in range(self.w_cells + 1):
            pygame.draw.line(self.m_layer, BLACK, (x * CELL_SIZE, 0),
                             (x * CELL_SIZE, SCREEN_SIZE[1]))

        # Color start cell blue and exit cell purple.
        # Assumes start at top-left and exit at bottom-right
        pygame.draw.rect(self.s_layer, BLUE,
                         pygame.Rect(0, 0, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(self.s_layer, PURPLE, pygame.Rect(
                         SCREEN_SIZE[0] - CELL_SIZE, SCREEN_SIZE[1] -
                         CELL_SIZE, CELL_SIZE, CELL_SIZE))


def check_for_exit():
    # Aims for 60fps, checks for events.
    # Without event check every frame, window will not exit!
    clock = pygame.time.Clock()
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit(0)