import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64
from std_msgs.msg import String

import math
import time

# TODO
# [X] - Create mapping system (look @ wavefront planner for kif and rip that framework)
#   [X] - Some sort of goal line or something? Travels along the goal line until it runs into an obstacle and/or finds a fire
#   [X] - Have squares on map represent areas 1/3 the size of Reginald
#   [X] - Numbers for filling in: 0 for spot found with fire, 1 for goal line, 2 for searched line space, 3+ for any other space, 100 for padding, 999 for obstacles
# [X] - System for adding obstacles to map w/ padding

# When encountering an obstacle
# 1 - Stop
# 2 - Update distance from last point
# 3 - Add obstacle to self.obstacles
# 4 - Generate instructions
# 5 - Start moving again

# Types of instructions given from the map:
# - Forward --> move forward a designated amount or forever (only happens when on goal line)
# - Turn Left
# - Turn Right
# - Move Backwards (do it when you're in an obstacle)

# Instructions processing
# [X] - Initial instruction set for start of challenge 2
# [X] - Refresh instructions after adding obstacles & updating map
#   [X] - Need to give preference for moving around the obstacle to get to the line, likely with a right movement bias (will happen naturally as coding is done)
#   [X] - Move in direction of decreasing values, unless on the goal line, in that case move in the default direction (east) --> might be able to nab this from wavefront
#     [X] - If reconnected to the goal line after hitting obstacle, check if there is any spots that were missed and get those before continuing on (though technically the fire should be right behind the obstacle so maybe just do a sweep of the area until it's found)
# [NO] - Likely try to overshoot the obstacle a bit (move 5-7 squares at a time)
# [X] - After moving past the obstacle turn and move back towards the next spot after the obstacle

# TODO 12/5
# [X] - Add instructions processing
# [X] - Traveled distance calculation in movement.py for map updating
# [X] - Determine how direction is given to the path planning node (keep track of direction in movement.py in a self.direc var or calculate that and send it too?)
# [X] - print_map get_logger functionality instead of print() (otherwise it wont show up in the termial)
#   [ ] - Test to make sure this actually works (no clue if it will)
# [ ] - Begin testing Challenge 2 code

# Reginald measurements: 220mm x 288mm
# Grid Square size: 100mm x 100mm (or if needed, 50mm x 50mm for even higher resolution)

# BIG IDEA: Orient the map so that the goal line is always straight? Could help out quite a bit rather than trying to path it out diagonally.

class NaviPathPlanning(Node):
    def __init__(self):
        super().__init__("pathi")

        # Initialize path planning publisher
        self.instructions_pub = self.create_publisher(String, 'instructions', 10)

        # Initialize subscriptions
        self.path_planning_ = self.create_subscription(String, 'path_planning', self.path_planning_callback, 10)
        
        # Challenge number
        self.challenge = 2
        
        # Path Planning Variables
        self.instructions = []

        # Challenge 1 stuff
        # Waypoint format: (heading/angle (degrees), distance (meters)) --> each waypoint is based off of the previous waypoint's position
        self.waypoints = [(352,1.92),(60,0.94)]

        # Challenge 2 Stuff
        # Map for Path Planning
        self.map = Map(debug=False)

        # Given heading
        self.heading = 307.5

        # Generate initial instructions
        self.generate_instructions()

        # Online message
        self.get_logger().info("Path Planning Online")

    def path_planning_callback(self, msg):
        stateList = eval(msg.data)
        state = stateList[0]
        if (state == 0): # Create initial instruction set & map
            self.generate_instructions()
        elif (state == 1): # Update map & instructions for instances where an obstacle is detected
            self.obstacle(stateList[1], stateList[2])
        elif (state == 2): # Update map & return empty instruction set
            self.fire(stateList[1], stateList[2])
    
    def generate_instructions(self):
        if self.challenge == 1: # Challenge 1 code
            # Vector values to find the correct direction and distance required to go back to the start
            vector_vals = []
            
            # Converts the waypoints into a list of instructions
            for waypoint in self.waypoints:
                self.instructions.append(f"t{waypoint[0]}")
                self.instructions.append(f"d{waypoint[1]}")
                x = waypoint[1] * math.cos((waypoint[0])*math.pi/180)
                y = waypoint[1] * math.sin(waypoint[0]*math.pi/180)
                self.get_logger().info(f"y: {y}")
                self.get_logger().info(f"x: {x}")
                vector_vals.append((x,y))
            
            # Calculate resultant vector
            total_x = 0
            total_y = 0
            for vec in vector_vals:
                total_x += vec[0]
                total_y += vec[1]
            self.get_logger().info(f"total_y: {total_y}")
            self.get_logger().info(f"total_x: {total_x}")
            angle = math.atan2(-total_y, -total_x) * (180 / math.pi)
            if (angle < 0):
                angle += 360
            dist = math.sqrt((total_x)**2 + (total_y)**2)
            self.instructions.append(f"t{angle}")
            self.instructions.append(f"d{dist}")

        if self.challenge == 2: # Challenge 2 code
            # Initial intructions for the start
            # Need to add angle to turn to to make map line up + send the angle for east (same angle)
            self.instructions.append(f"a{self.heading}") # allows the heading angle to be passed to the movement file
            self.instructions.append(f"t{self.heading}")
            # Move forward very far lmao
            self.instructions.append(f"d{20}")
            # Aaaaand that's it, just those two things
            self.printMap()

        self.get_logger().info(f"Instructions: {self.instructions}")
        
        # Publish instruction Set
        instructions = String()
        instructions.data = repr(self.instructions)
        self.instructions_pub.publish(instructions)
    
    def obstacle(self, dist, direc):
        # Update the map
        self.map.update_loc(dist, direc)
        self.map.add_obstacle(direc)
        self.printMap()
        
        # Create new instructions based on the current map
        self.instructions = []

        # Move in direction of decreasing values
        loc = self.map.curr_loc
        mapval = self.map.map[loc[0]][loc[1]]
        prevDirec = direc
        while (mapval != 1):
            moveBackwards = 1
            if (self.map.map[loc[0]+1][loc[1]] < mapval): # Search East
                # Turn if there's a change in direction
                if (prevDirec != 0):
                    turnAngle = 360 - 90*prevDirec + self.heading
                    if (turnAngle >= 360):
                        turnAngle -= 360
                    if ((360 - 90*prevDirec) == 180):
                        moveBackwards = -1
                    else:
                        self.instructions.append(f"t{turnAngle}")
                    prevDirec = 0
                
                # Change mapval & loc
                mapval = self.map.map[loc[0]+1][loc[1]]
                loc = [loc[0]+1,loc[1]]

                repMapval = mapval # repetitive map val variable for checking repeated movement in the same direction
                nextMapval = self.map.map[loc[0]+1][loc[1]]
                count = 1
                # Check for multiple instances of the instruction
                while (nextMapval < repMapval and loc[0]+1 < self.map.cols):
                    loc = [loc[0]+1,loc[1]]
                    count += 1
                    repMapval = nextMapval
                    nextMapval = self.map.map[loc[0]+1][loc[1]]
                    
                # Add instruction 
                dist = 0.1 * count
                self.instructions.append(f"d{dist*moveBackwards}")

            elif (self.map.map[loc[0]][loc[1]+1] < mapval): # Search South
                # Turn if there's a change in direction
                if (prevDirec != 3):
                    turnAngle = 360 - 90*prevDirec + self.heading
                    if (turnAngle >= 360):
                        turnAngle -= 360
                    if ((360 - 90*prevDirec) == 180):
                        moveBackwards = -1
                    else:
                        self.instructions.append(f"t{turnAngle}")
                    prevDirec = 3
                
                # Change mapval & loc
                mapval = self.map.map[loc[0]][loc[1]+1]
                loc = [loc[0],loc[1]+1]

                repMapval = mapval # repetitive map val variable for checking repeated movement in the same direction
                nextMapval = self.map.map[loc[0]][loc[1]+1]
                count = 1
                # Check for multiple instances of the instruction
                while (nextMapval < repMapval and loc[1]+1 < self.map.cols):
                    loc = [loc[0],loc[1]+1]
                    count += 1
                    repMapval = nextMapval
                    nextMapval = self.map.map[loc[0]][loc[1]+1]
                    
                # Add instruction 
                dist = 0.1 * count
                self.instructions.append(f"d{dist*moveBackwards}")

            elif (self.map.map[loc[0]-1][loc[1]] < mapval): # Search West
                # Turn if there's a change in direction
                if (prevDirec != 2):
                    turnAngle = 360 - 90*prevDirec + self.heading
                    if (turnAngle >= 360):
                        turnAngle -= 360
                    if ((360 - 90*prevDirec) == 180):
                        moveBackwards = -1
                    else:
                        self.instructions.append(f"t{turnAngle}")
                    prevDirec = 2
                
                # Change mapval & loc
                mapval = self.map.map[loc[0]-1][loc[1]]
                loc = [loc[0]-1,loc[1]]

                repMapval = mapval # repetitive map val variable for checking repeated movement in the same direction
                nextMapval = self.map.map[loc[0]-1][loc[1]]
                count = 1
                # Check for multiple instances of the instruction
                while (nextMapval < repMapval and loc[0]-1 > 0):
                    loc = [loc[0]-1,loc[1]]
                    count += 1
                    repMapval = nextMapval
                    nextMapval = self.map.map[loc[0]-1][loc[1]]
                    
                # Add instruction 
                dist = 0.1 * count
                self.instructions.append(f"d{dist*moveBackwards}")

            elif (self.map.map[loc[0]][loc[1]-1] < mapval): # Search North
                # Turn if there's a change in direction
                if (prevDirec != 1):
                    turnAngle = 360 - 90*prevDirec + self.heading
                    if (turnAngle >= 360):
                        turnAngle -= 360
                    if ((360 - 90*prevDirec) == 180):
                        moveBackwards = -1
                    else:
                        self.instructions.append(f"t{turnAngle}")
                    prevDirec = 1
                
                # Change mapval & loc
                mapval = self.map.map[loc[0]][loc[1]-1]
                loc = [loc[0],loc[1]-1]

                repMapval = mapval # repetitive map val variable for checking repeated movement in the same direction
                nextMapval = self.map.map[loc[0]][loc[1]-1]
                count = 1
                # Check for multiple instances of the instruction
                while (nextMapval < repMapval and loc[1]-1 > 0):
                    loc = [loc[0],loc[1]-1]
                    count += 1
                    repMapval = nextMapval
                    nextMapval = self.map.map[loc[0]][loc[1]-1]
                    
                # Add instruction 
                dist = 0.1 * count
                self.instructions.append(f"d{dist*moveBackwards}")

        # Once back on the line, check for 1s in the west direction & move west if there are any
        if self.map.map[loc[0]-1][loc[1]] == 1:
            # Angle Turn
            turnAngle = 180 + self.heading
            if (turnAngle >= 360):
                turnAngle -= 360
            self.instructions.append(f"t{turnAngle}")

            # Distance movement
            repMapval = self.map.map[loc[0]-1][loc[1]] # repetitive map val variable for checking repeated movement in the same direction
            loc = [loc[0]-1,loc[1]]
            nextMapval = self.map.map[loc[0]-1][loc[1]]
            count = 1
            # Check for multiple instances of the instruction
            while (nextMapval == repMapval and loc[0]-1 > 0):
                loc = [loc[0]-1,loc[1]]
                count += 1
                repMapval = nextMapval
                nextMapval = self.map.map[loc[0]-1][loc[1]]
                
            # Add instruction 
            dist = 0.1 * count
            self.instructions.append(f"d{dist}")

            # Turn around and move east again (?) might just have it so that it continues back to the obstacle and then moves around the area until it finds the fire
            self.instructions.append(f"d-0.1")
            self.instructions.append(f"t{self.heading}")
            self.instructions.append(f"d{20}")
        else:
            # Turn to face east
            self.instructions.append(f"t{self.heading}")
            # Continue forever :D
            self.instructions.append(f"d{20}")

        # Place square of 1s if moving west and found an obstacle (?)

        self.get_logger().info(f"Instructions: {self.instructions}")
        
        # Publish instruction Set
        instructions = String()
        instructions.data = repr(self.instructions)
        self.instructions_pub.publish(instructions)

    def fire(self, dist, direc):
        # Update the map
        self.map.update_loc(dist, direc)
        self.map.add_fire()
        self.printMap()

        # Empty instruction set because the goal has been reached
        self.instructions = []

        self.get_logger().info(f"Instructions: {self.instructions}")
        
        # Publish instruction Set
        instructions = String()
        instructions.data = repr(self.instructions)
        self.instructions_pub.publish(instructions)
        
    def printMap(self):
        for i in range(len(self.map.map[0])):
            line = ""
            for j in range(len(self.map.map)):
                line += f"{self.map.map[j][i]:<2}"
            self.get_logger().info(line)

class Map(): # Class for a map
    def __init__(self, cols=50, rows=21, size = 100, debug=True):
        # Specific Map values
        # Other map values are obtained by starting at 3 along the goal line and incrementing upwards
        self.fire = 0
        self.goal_line = 1
        self.searched = 45
        self.padding = 90
        self.obstacle = 99

        # Debug variable, controls whether the map is printed to the terminal or not when print_map() is run
        self.debug = debug
        self.mapPrintout = "" # For challenge 2 outputting to terminal
        
        # Load default map
        self.defaultMapVal = 0
        self.cols = cols
        self.rows = rows
        self.square_size = size # size in millimeters
        self.map = [[self.defaultMapVal for _ in range(self.rows)] for _ in range(self.cols)]

        # Variables for keeping track of map filling
        self.count = 0
        self.map_list = [[self.defaultMapVal for _ in range(2)] for _ in range(self.cols*self.rows)]

        # Obstacles & Padding
        self.obstacles = []
        # self.obstacles = [[0,0],[0,10],[10,10],[20,10],[self.cols-1,self.rows-1]] # list of obstacle locations
        self.draw_obstacles()
        self.draw_padding()

        # Start & current location variables
        self.start_loc = [3,int(rows/2)]
        self.curr_loc = self.start_loc # Current Location

        # Locations along the path that have already been searched
        self.searched_locs = []
        self.searched_locs.append(self.start_loc) # Add start location to map as already searched square
        self.draw_searched_locs()

        # Add goal line
        self.draw_goal_line(self.start_loc)

        # Fill the rest of the map
        self.fill_map()

        # Test square
        # self.update_square(loc=(1,4),num=5)

        # Print the map out
        self.print_map()

    def update_square(self, loc, num): # Pass a location (tuple or list formatted as "x,y") and a number to set the square to
        self.map[loc[0]][loc[1]] = num

    def print_map(self): # Prints the map out
        if not self.debug:
            return
        # self.mapPrintout = ""
        for i in range(len(self.map[0])):
            # line = ""
            print(f"{i:<2}: ", end="")
            for j in range(len(self.map)):
                # line += f"{self.map[j][i]:<2}"
                print(f"{self.map[j][i]:<2}", end=" ")
            # self.mapPrintout += line + "\n"
            print()

    # Functions specifically for initial map generation
    def redraw_map(self):
        self.count = 0
        self.map = [[self.defaultMapVal for _ in range(self.rows)] for _ in range(self.cols)]
        self.map_list = [[self.defaultMapVal for _ in range(2)] for _ in range(self.cols*self.rows)]
        self.draw_obstacles()
        self.draw_padding()
        self.draw_searched_locs()
        self.draw_goal_line(self.start_loc)
        self.fill_map()
        self.print_map()

    def draw_obstacles(self):
        for obs in self.obstacles:
            self.update_square(obs, self.obstacle) # add obstacle to map
    
    def draw_padding(self): # Pads a square of value self.padding around each obstacle
        for obs in self.obstacles:
            x = obs[0]-2
            y = obs[1]-2
            for i in range(5):
                for j in range(5):
                    if (x >= 0 and y >= 0 and x < self.cols and y < self.rows and self.map[x][y] == 0):
                        self.map[x][y] = self.padding
                    y += 1
                y = obs[1]-2
                x += 1

    def draw_searched_locs(self):
        for loc in self.searched_locs:
            if (self.map[loc[0]][loc[1]] == 0):
                self.update_square(loc, self.searched) # add value to map

    def draw_goal_line(self, start, end=None): # Adds the goal line to the map
        if end == None:
            end = [self.cols, start[1]]
            #print(end)
        while (start != end):
            if self.map[start[0]][start[1]] == 0:
                self.update_square(start, self.goal_line) # add value to map
                
                # add location to map_list
                self.map_list[self.count] = start
                self.count += 1

            # update location
            start = [start[0]+1, start[1]]

    def fill_map(self):
        # i = len(self.obstacles)
        i = 0
        while (i <= self.count and self.count <= len(self.map_list)-1):
            x = self.map_list[i][0]
            y = self.map_list[i][1]
            if (self.map[x][y] == 1):
                increase = 2
            else:
                increase = 1

            if (y+1 < self.rows):
                if (self.map[x][y+1] == 0):
                    self.map[x][y+1] = self.map[x][y] + increase
                    self.map_list[self.count][0] = x     # x coordinate of new 1
                    self.map_list[self.count][1] = y+1   # y coordinate of new 1
                    self.count += 1
                    # print(i,self.count)

            if (y-1 > -1):
                if (self.map[x][y-1] == 0):
                    self.map[x][y-1] = self.map[x][y] + increase
                    self.map_list[self.count][0] = x     # x coordinate of new 1
                    self.map_list[self.count][1] = y-1   # y coordinate of new 1
                    self.count += 1
                    # print(i,self.count)

            if (x+1 < self.cols):
                if (self.map[x+1][y] == 0):
                    self.map[x+1][y] = self.map[x][y] + increase
                    self.map_list[self.count][0] = x+1    # x coordinate of new 1
                    self.map_list[self.count][1] = y      # y coordinate of new 1
                    self.count += 1
                    # print(i,self.count)

            if (x-1 > -1):
                if (self.map[x-1][y] == 0):
                    self.map[x-1][y] = self.map[x][y] + increase
                    self.map_list[self.count][0] = x-1   # x coordinate of new 1
                    self.map_list[self.count][1] = y     # y coordinate of new 1
                    self.count += 1
                    # print(i,self.count)
            i += 1

    # Functions for modifying the map
    def update_loc(self, dist, direc=0):
        '''Supply the distance and direction traveled from the last known location to approximate the
           current tile'''
        
        # Update current location
        map_dist = int(dist / self.square_size)
        x = self.curr_loc[0]
        y = self.curr_loc[1]
        if direc == 0: # default direction, east / +x direction
            new_loc = [x+map_dist,y]
        elif direc == 1: # north / -y direction
            new_loc = [x,y-map_dist]
        elif direc == 2: # west / -x direction
            new_loc = [x-map_dist,y]
        elif direc == 3: # south / +y direction
            new_loc = [x,y+map_dist]
        
        self.add_searched(new_loc, direc) # add searched tiles from last location to new location
        self.curr_loc = new_loc # Update current location

        self.redraw_map()
    
    def add_searched(self, new_loc, direc):
        while self.curr_loc != new_loc:
            x = self.curr_loc[0]
            y = self.curr_loc[1]
            if direc == 0: # default direction, east / +x direction
                self.curr_loc = [x+1,y]
            elif direc == 1: # north / -y direction
                self.curr_loc = [x,y-1]
            elif direc == 2: # west / -x direction
                self.curr_loc = [x-1,y]
            elif direc == 3: # south / +y direction
                self.curr_loc = [x,y+1]
            
            self.update_square(self.curr_loc, self.searched)
            self.searched_locs.append(self.curr_loc)
        
        self.redraw_map()
        
    def add_obstacle(self, direc=0):
        '''Add an obstacle to the obstacles list'''
        x = self.curr_loc[0]
        y = self.curr_loc[1]

        # Add new obstacle to obstacles list
        if direc == 0: # default direction, east / +x direction
            new_obs = [x+1,y]
        elif direc == 1: # north / -y direction
            new_obs = [x,y-1]
        elif direc == 2: # west / -x direction
            new_obs = [x-1,y]
        elif direc == 3: # south / +y direction
            new_obs = [x,y+1]
        
        # Add obstacle if within map boundary
        if (0 <= new_obs[0] < self.cols and 0 <= new_obs[1] < self.rows):
            self.obstacles.append(new_obs)
        
        self.redraw_map()
    
    def add_fire(self):
        '''Adds the fire tile to the map when found, because of the location of the sensor on the robot this will be on the robot's current tile'''
        self.update_square(self.curr_loc, self.fire)

        self.redraw_map()

def main(args=None):
    # map = Map(debug=True)
    # map.update_loc(1600,0) # simulate moving forward 16 squares
    # map.print_map() # print da map

    rclpy.init(args=args)
    node = NaviPathPlanning()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
    
if __name__ == "__main__":
    main()

