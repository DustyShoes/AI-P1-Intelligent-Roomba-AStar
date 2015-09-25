
goal = [1,2,3,4,5,6,7,8,None]

def isGoal(node):
    (state, yeah, path) = node
    return state == goal
    
def swapNew(state, a, b):
    copy = state[:]
    copy[a], copy[b] = copy[b], copy[a]
    return copy

def getHash(node):
    (state, yeah, path) = node
    return str(state)
  
def h1(node):
    (state, yeah, path) = node
    count = 8
    for i in range(9):
        if state[i] == goal[i] and state[i] != None:
            count = count - 1
    return count
  
def h2(node):
    (state, path) = node
    counter = 0
    for i in range(9):
        looking_for = goal[i]
        pos_of = state.index(looking_for)
        col_goal = i % 3
        row_goal = int(i) / 3
        col_cur = pos_of % 3
        row_cur = int(pos_of) / 3
        counter = counter + abs(col_goal - col_cur) + abs(row_goal - row_cur)
    return counter
  
def g(node):
    (state, yeah, path) = node
    return len(path)
  
def generateSuccessors(node):
    (state, yeah, path) = node
    ret = []
    noneloc = state.index(None)
    # Can I move up?
    if noneloc > 2:
        ret.append( (swapNew(state, noneloc, noneloc-3 ), path + 'u' ))
    # Can I move down?
    if noneloc < 6:
        ret.append( (swapNew(state, noneloc, noneloc+3 ), path + 'd' ))
    # Can I move right?
    if noneloc % 3 != 2:
        ret.append( (swapNew(state, noneloc, noneloc+1 ), path + 'r' ))
    # Can I move left?
    if noneloc % 3 != 0:
        ret.append( (swapNew(state, noneloc, noneloc-1 ), path + 'l' ))
    return ret
        
def astar(node, h):
    frontier = [(100 - (h(node) + g(node)),node)]
    explored = {}
    numExpanded = 0
    maxFrontier = 0
    while(len(frontier) > 0):
        (priority, curNode) = frontier.pop()
        numExpanded = numExpanded + 1
        explored[getHash(curNode)] = 1
        for testnode in generateSuccessors(curNode):
            if isGoal(testnode):
                print("I expanded: " + str(numExpanded) + "nodes")
                print("max frontier: " + str(maxFrontier) )
                return testnode
            if getHash(testnode) in explored:
                continue
            frontier.insert(0, (100 - (h(testnode) + g(testnode)),testnode))
            frontier = sorted(frontier, key=lambda a: a[0])
            if len(frontier) > maxFrontier:
                maxFrontier = len(frontier)
      
startNode = ([1,2,3,4,None,6,7,5,8], "yeah", "")

#print(h2(startNode))

print(astar(startNode,h1))
print(astar(startNode,h2))
