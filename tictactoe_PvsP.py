def drawBoard(arr):
    """
    arr is the array of X, O, or " " as it is in the board
    """
    n = len(arr) # the length of the array - the board is an nxn board
    top = "  "  # the board has a top which has all the numbers across
    demLine = "  "
    rowLine = "" 
    for i in range(0,n):
        top += "  " + str(i) + " " # add the number markers to the top string
        demLine += "* * " # this is the demarcation between each row
    print(top) # print the top which contains the numbers across
    for i in range(0,n):
        rowLine = str(i) + " " # current row of X, O, and " ". Starts with row number
        print(demLine, end = "*\n") # print the demarcation ending w/ an * and newline 
        for j in range(0,n):
            rowLine += "* " + arr[i][j] + " " # add X, O, or " " to current row    * X * O
        print(rowLine + "*") # show the current row ending with an *
    print(demLine, end = "*\n") # print the last demarcation line at the end

def checkCood(x,n):
    """
    This function checks if a value of x or y inputed by the user to place X or 
    O in a certain location (x,y) is correct.
    Returns True if x is a valid input.
    Returns False otherwise.
    """
    try:
        int(x) # converts to integer. No error if x is an integer
    except ValueError:
        # if x is not an integer:
        print("Input an integer between 0 and " + str(n) + " inclusive")
        return False
    # if x is an interger:
    if not (0 <= int(x) < n):
        # if x is an integer but is not a valid index i.e not in 0 <= x < n
        print("Wrong coordinate input")
        return False
    else:
        # if there is no error
        return True

def playGame(n,thresh):
    tttboard = [] # this keeps record of the board, either X or O or " "
    plays = 0 # number of time both players have played in total

    # generate a double array of spaces as an initial board
    inner = []
    for i in range(0,n):
        inner.append(" ")
    for i in range(0,n):
        tttboard.append(inner[:])
      
    # To check if someone has won. If anyone wins, won is going to be
    # a  string: X wins, O wins, or DRAW
    won = None
    
    currPlayer = True # boolean to check player 1 or 2
    drawBoard(tttboard) # displays inital empty board

    while (won == None): # if won is None, no player has won
        if currPlayer:
            print("Player 1") # if currPlayer is true player 1 is to play
        else:
            print("CPu") # if currPlayer is false player 2 is to play ##CHANGE TO CPU ARTIFICIAL INTELLIGENCE, CJ, DEQUANE AND I.##

        # the current player has to choose a location to play to
        validPlLoc = False # validPlLoc tracks whether the player has chosen a valid location
        while not validPlLoc: # while a valid location (x,y) has not been chosen
            validNo = False
            while not validNo: # while a valid x value has not been chosen
                x = input("Input the x location: ") # x is a string
                validNo = checkCood(x,n) # check if x is an integer between 0 and n
            x = int(x)
            validNo = False
            while not validNo: # while a valid y value has not been chosen
                y = input("Input the y location: ")
                validNo = checkCood(y,n) # check if y is an integer between 0 and n
            y = int(y)

            # if (x,y) contains X or O, then player has to choose another
            if tttboard[x][y] != " ":
                print("Space used. Select another.")
            else:
                validPlLoc = not validPlLoc # correct location chosen... continue game
        
        # check if any player has won
        if currPlayer:
            tttboard[x][y] = "X"
            if checkWin(tttboard, x, y, thresh, "X"): # check if X has won
                drawBoard(tttboard)
                won = "X wins" # won is no longer None. While loop breaks
                continue
        else:
            tttboard[x][y] = "O"
            if checkWin(tttboard, x, y, thresh, "O"): # check if Y has won
                drawBoard(tttboard)
                won = "O wins" # won is no longer None. While loop breaks
                continue
        
        # if nobody has won
        drawBoard(tttboard) # show the updated board
        plays += 1 # increase the number of those who have played
        currPlayer = not currPlayer # change the player to the next player

        # if people have played n^2 times, the whole board is filled.
        # it's a draw
        if plays == n**2:
            won = "DRAW"
        
    # this runs after won has changed to either "X wins", "O wins", or "DRAW"    
    print(won)

def checkWin(tttboard,x,y,tar,ch):
      if checkrows(tttboard,x,y,tar,ch):
        return True
      elif checkcolumns(tttboard,x,y,tar,ch):
        return True
      elif checkrightdiag(tttboard,x,y,tar,ch):
        return True
      elif checkleftdiag(tttboard,x,y,tar,ch):
        return True
      else: 
        return False

def checkrows(tttboard,x,y,tar,ch): #ch = X
    global currPlayer
    for i in range(y-tar+1,y+1):
        if i < 0:
            continue
        every_x = True
        for j in range(i,i+tar): #i = 1, tar = 3, ch = O, j = 1, 2, 3
            if j >= len(tttboard):
                every_x = False
                break
            if not tttboard[x][j] == ch:
                every_x = False
                break
        if every_x:
            return True
  
def checkcolumns(tttboard,x,y,tar,ch):
    global currPlayer
    for i in range(x-tar+1,x+1):
        if i < 0:
            continue
        every_y = True
        for j in range(i,i+tar):
            if j >= len(tttboard):
                every_y = False
                break
            if not tttboard[j][y] == ch:
                every_y = False
                break
        if every_y:
            return True

def checkrightdiag(tttboard,x,y,tar,ch):
    global currPlayer
    n = len(tttboard)
    for i in range(0,tar):
        if x-i < 0 or y-i < 0:
            continue
        every_xy = True
        for j in range(0,tar):
            if j+x-i >= n or j+y-i >= n:
                every_xy = False
                break
            if not tttboard[j+x-i][j+y-i] == ch:
                every_xy = False
                break
        if every_xy:
            return True

def checkleftdiag(tttboard,x,y,tar,ch):
    global currPlayer
    n = len(tttboard)
    for i in range(0,tar):
        if x+i >= n or y-i < 0:
            continue
        every_xy = True
        for j in range(0,tar):
            if x+i-j < 0 or j+y-i >= n:
                every_xy = False
                break
            if not tttboard[x+i-j][j+y-i] == ch:
                every_xy = False
                break
        if every_xy:
            return True