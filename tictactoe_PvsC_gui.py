from re import L
import pygame, sys
from pygame.locals import *
from turtle import update

WHITE = (255,255,255)
RED = (200,0,0)
BLACK = (0,0,0)
BLUE = (0,0,200)
GREEN = (0,200,0)

def abs(n):
    return max(n,-n)

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

def playerNextMove(n,tttboard,SCREEN,cW,hW,textSize,textPos,surfSize,surfPos):
    validPlLoc = False # validPlLoc tracks whether the player has chosen a valid location
    while not validPlLoc: # while a valid location (x,y) has not been chosen
        validNo = False
        while not validNo: # while a valid x value has not been chosen
            x,y = getInputSpot(cW,hW)
            if x == -10000:
               return (-10000,0)
        # if (x,y) contains X or O, then player has to choose another
            validNo = checkCood(x,n)
            if not validNo:
                newDispText(SCREEN,BLUE,WHITE,"Click valid point",textSize,textPos,surfSize,surfPos)
                continue
            validNo = checkCood(y,n)
            if not validNo:
                newDispText(SCREEN,BLUE,WHITE,"Click valid point",textSize,textPos,surfSize,surfPos)
        if tttboard[x][y] != " ":
            print("Space used. Select another.")
        else:
            validPlLoc = not validPlLoc # correct location chosen... continue game
    return (x,y)

def isEdgeCell(x,y,dir,n,tttboard):
    if x==0 or y==0 or x==n-1 or y==n-1:
        return True

def isGroupFree(start,nCh,oCh,n,dir,tttboard,thresh):
    x,y = start//10, start%10
    if isEdgeCell(x,y,dir,n,tttboard):
        return (0,[])
    x_inc,y_inc = 0, 0
    if dir == 'ro':
        y_inc = 1
    elif dir == 'co':
        x_inc = 1
    elif dir == 'ld':
        x_inc, y_inc = 1, 1
    elif dir == 'rd':
        x_inc, y_inc = -1, 1
    lcheck_x, lcheck_y = x+5*x_inc >= n-1, y+5*y_inc >= n-1
    if dir == 'rd':
        lcheck_x = x+5*x_inc <= 0
    if lcheck_x or lcheck_y:
        return (0,[])
    xi, yi = x-x_inc, y-y_inc
    lcheck_x, lcheck_y = xi >=0, yi >= 0
    if dir == 'rd':
        lcheck_x = xi < n
    if lcheck_x and lcheck_y and tttboard[xi][yi] == oCh:
        return (0,[])
    xi,yi = x + 5*x_inc, y + 5*y_inc
    lcheck_x, lcheck_y = xi < n, yi < n
    if dir == 'rd':
        lcheck_x = xi >= 0
    if xi < n and yi < n and tttboard[xi][yi] == oCh:
        return (0,[])
    # so check within the group for gaps
    # find the first occurence of the character
    xi,yi = x,y
    group = []
    l, r = 0, thresh-1
    foundCh = False
    cntCh = 0
    for i in range(thresh):
        group.append(tttboard[xi][yi])
        if tttboard[xi][yi] == nCh :
            cntCh += 1
            if not foundCh:
                foundCh = True
                l = i
        xi, yi = xi+x_inc, yi+y_inc
    while group[r] == ' ':
        r -= 1
    cnt = 0
    freecells = []
    for i in range(l+1,r):
        if group[i] == ' ':
            freecells.append((x+i*x_inc)*n + (y+i*y_inc))
            cnt += 1
    if cnt > 2 or cnt > 1 and cntCh == 3:
        return (0,[])
    if cnt > 0 and cntCh == 3:
            return (1,freecells)
    l -= 1
    if l >= 0:
        freecells.append((x+l*x_inc)*n + (y+l*y_inc))
        if cntCh == 2:
            l -= 1
            if l >= 0:
                freecells.append((x+l*x_inc)*n + (y+l*y_inc))
            l += 1
    l += 1
    r += 1
    if r <= thresh-1:
        freecells.append((x+r*x_inc)*n + (y+r*y_inc))
        if cntCh == 2:
            r += 1
            if r < thresh-1:
                freecells.append((x+r*x_inc)*n + (y+r*y_inc))
            r -= 1
    r -= 1
    return (1,freecells)

def updateData(x,y,pCh,cCh,n,tttboard,thresh,playerData,cpuData):
    dir = 'ro' + str(x)
    rel = [[dir,(x,0),(0,1)]]
    dir = 'co' + str(y)
    rel.append([dir,(0,y),(1,0)])
    if x-y <= - thresh or x-y <= thresh:
        dir = 'ld' + str(x-y)
        rel.append([dir,(x-y,0),(1,1)])
        if x-y < 0:
            rel[-1][1] = (0,y-x)
    if x+y+1 >= thresh or x+y+1 <= 2*n - thresh:
        dir = 'rd' + str(x+y)
        rel.append([dir,(x+y,0),(-1,1)])
        if x+y > 9:
            rel[-1][1] = (9,x+y-9)
    for dirdata in rel:
        pres = []
        cres = []
        for i in range(thresh-1):
            pres.append([])
            cres.append([])
        dir = dirdata[0]
        st_x, st_y = dirdata[1]
        x_inc,y_inc = dirdata[2]
        for i in range(n-thresh+1):
            count1,count2 = -1,-1
            if st_x+thresh*x_inc < -1 or st_x+thresh*x_inc > n:
                break
            if st_y+thresh*y_inc < -1 or st_y+thresh*y_inc > n:
                break
            for j in range(thresh):
                xj,yj = st_x+j*x_inc, st_y+j*y_inc
                if tttboard[xj][yj] == pCh:
                    count1 += 1
                    count2 = -thresh-1
                if tttboard[xj][yj] == cCh:
                    count1 = -thresh-1
                    count2 += 1
            if count1 > -1:
                pres[count1].append(st_x*n + st_y)
            if count2 > -1:
                cres[count2].append(st_x*n + st_y)
            st_x,st_y = st_x+x_inc, st_y+y_inc
        for i in range(thresh-1):
            if pres[i] != []:
                playerData[i][dir] = pres[i]
            else:
                if dir in playerData[i]:
                    playerData[i].pop(dir)
            if cres[i] != []:
                cpuData[i][dir] = cres[i]
            else:
                if dir in cpuData[i]:
                    cpuData[i].pop(dir)

def updateData2(x,y,pCh,cCh,n,tttboard,thresh,playerData,cpuData):
    # col
    dir = tttboard[x][y].col
    # change range limits for co and ro
    f = max(x-thresh+1,0)
    l = min(n-thresh,x)
    for start in range(f,l+1):
        count1,count2 = -1,-1
        curr = []
        for j in range(start,start+thresh):
            if tttboard[j][y].ch == ' ':
                tttboard[j][y].setFreedomUpdate(False)
            if tttboard[j][y].ch == pCh:
                count1 += 1
                count2 = -thresh-1
            elif tttboard[j][y].ch == cCh:
                count1 = -thresh-1
                count2 += 1
        if count1 > -1:
            if dir not in playerData[count1]:
                playerData[count1][dir] = {start*n + y}
            else:
                playerData[count1][dir].add(start*n + y)
            if count1 > 0:
                playerData[count1-1][dir].remove(start*n + y)
        if count2 > -1:
            if dir not in cpuData[count2]:
                cpuData[count2][dir] = {start*n + y}
            else:
                cpuData[count2][dir].add(start*n + y)
            if count2 > 0:
                cpuData[count2-1][dir].remove(start*n + y)
    # row
    dir = tttboard[x][y].row
    f = max(y-thresh+1,0)
    l = min(n-thresh,y)
    for start in range(f,l+1):
        count1,count2 = -1,-1
        for j in range(start,start+thresh):
            if tttboard[x][j].ch == ' ':
                tttboard[x][j].setFreedomUpdate(False)
            if tttboard[x][j].ch == pCh:
                count1 += 1
                count2 = -thresh-1
            elif tttboard[x][j].ch == cCh:
                count1 = -thresh-1
                count2 += 1
        if count1 > -1:
            if dir not in playerData[count1]:
                playerData[count1][dir] = {x*n + start}
            else:
                playerData[count1][dir].add(x*n + start)
            if count1 > 0:
                playerData[count1-1][dir].remove(x*n + start)
        if count2 > -1:
            if dir not in cpuData[count2]:
                cpuData[count2][dir] = {x*n + start}
            else:
                cpuData[count2][dir].add(x*n + start)
            if count2 > 0:
                cpuData[count2-1][dir].remove(x*n + start)
    # ldiag
    if x-y <= -thresh or x-y <= thresh:
        dir = tttboard[x][y].ldiag
        if x-y >= 0:
            st_x, st_y = x-y, 0
        else:
            st_x, st_y = 0, y-x
        starts = min(n-st_x,n-st_y) - thresh + 1
        print("starts:",starts)
        for i in range(starts):
            count1,count2 = -1,-1
            for j in range(0,thresh):
                if tttboard[st_x+i+j][st_y+i+j].ch == ' ':
                    tttboard[st_x+i+j][st_y+i+j].setFreedomUpdate(False)
                if tttboard[st_x+i+j][st_y+i+j].ch == pCh:
                    count1 += 1
                    count2 = -thresh-1
                elif tttboard[st_x+i+j][st_y+i+j].ch == cCh:
                    count1 = -thresh-1
                    count2 += 1
            print(dir,i,count1,count2)
            if count1 > -1:
                if dir not in playerData[count1]:
                    playerData[count1][dir] = {(st_x+i)*n + (st_y+i)}
                else:
                    playerData[count1][dir].add((st_x+i)*n + (st_y+i))
                if count1 > 0:
                    playerData[count1-1][dir].remove((st_x+i)*n + (st_y+i))
            if count2 > -1:
                if dir not in cpuData[count2]:
                    cpuData[count2][dir] = {(st_x+i)*n + (st_y+i)}
                else:
                    cpuData[count2][dir].add((st_x+i)*n + (st_y+i))
                if count2 > 0:
                    cpuData[count2-1][dir].remove((st_x+i)*n + (st_y+i))
    # rdiag
    if x+y+1 >= thresh or x+y+1 <= 2*n - thresh:
        dir = tttboard[x][y].rdiag
        if x+y <= 9:
            st_x,st_y = x+y, 0
        else:
            st_x,st_y = 9, x+y-9
        starts = min(2*(n-1)-(x+y),st_x) - thresh + 2
        for i in range(starts):
            count1,count2 = -1,-1
            for j in range(0, thresh):
                if tttboard[st_x-i-j][st_y+i+j].ch == ' ':
                    tttboard[st_x-i-j][st_y+i+j].setFreedomUpdate(False)
                if tttboard[st_x-i-j][st_y+i+j].ch == pCh:
                    count1 += 1
                    count2 = -thresh-1
                elif tttboard[st_x-i-j][st_y+i+j].ch == cCh:
                    count1 = -thresh-1
                    count2 += 1
            if count1 > -1:
                if dir not in playerData[count1]:
                    playerData[count1][dir] = {(st_x-i)*n + (st_y+i)}
                else:
                    playerData[count1][dir].add((st_x-i)*n + (st_y+i))
                if count1 > 0:
                    playerData[count1-1][dir].remove((st_x-i)*n + (st_y+i))
            if count2 > -1:
                if dir not in cpuData[count2]:
                    cpuData[count2][dir] = {(st_x-i)*n + (st_y+i)}
                else:
                    cpuData[count2][dir].add((st_x-i)*n + (st_y+i))
                if count2 > 0:
                    cpuData[count2-1][dir].remove((st_x-i)*n + (st_y+i))

def missingCellsGen(n,thresh,tttboard,dir,start):
    cells = []
    x_inc,y_inc = 0, 0
    if dir == 'ro':
        y_inc = 1
    elif dir == 'co':
        x_inc = 1
    elif dir == 'ld':
        x_inc, y_inc = 1, 1
    elif dir == 'rd':
        x_inc, y_inc = -1, 1
    x,y = start//n,start%n
    for i in range(thresh):
        if tttboard[x][y] == ' ':
            cells.append(x*n + y)
        x, y = x+x_inc, y+y_inc
    return cells

def compareOptions(info,refInfo):
    if info[0] < refInfo[0]:
        # if we have 3-in-a-row in info, then it can possibly be a better option
        # if more than 1 exist
        if 3 in refInfo[1]:
            if info[3] > refInfo[3]:
                return True
            elif info[3] < refInfo[3]:
                return False
            if refInfo[2] > 0:
                return False
        if 3 in info[1]:
            # if ref has 3-in-a-row also, then it is better
            if 3 in refInfo[1] and refInfo[2] > 0:
                return False
            if info[0] > 0 and info[2] > 0:
                return True
        if 2 in refInfo[1]:
            if 2 not in info[1]:
                return False
            if refInfo[2] > info[2]:
                return False
            elif refInfo[2] < info[2] and info[0] > 0:
                return True
        ## UPDATE THIS NEXT PART FOR ONES
        return False
    # if they have the same intersection counts
    if info[0] == refInfo[0]:
        # if 3 is in our info, then it is probably better
        if refInfo[3] > info[3]:
            return False
        elif refInfo[3] < info[3]:
            return True
        if 3 in info[1] and info[2] > 0:
            return True
        # if the opponent has 3 instead, choose opponent
        if 3 in refInfo[1] and refInfo[2] > 0:
            return False
        if refInfo[2] > info[2]:
            return False
        return True
    # if intersection is more than in reference
    if info[0] > refInfo[0]:
        if 3 in info[1]:
            if info[3] > refInfo[3]:
                return True
            elif info[3] < refInfo[3]:
                return False
            if info[2] > 0:
                return True
        if 3 in refInfo[1]:
            if 3 in info[1] and info[2] > 0:
                return True
            if refInfo[0] > 0 and refInfo[2] > 0:
                return False
        if 2 in info[1]:
            if 2 not in refInfo[1]:
                return True
            if info[2] > refInfo[2]:
                return True
            if info[2] < refInfo[2] and refInfo[0] > 0:
                return False
        ## UPDATE THIS NEXT PART FOR ONES
        return True

def insertOption(options,optionsInfo,cell,info,l,r):
    while r >= l:
        # compare info to info
        if compareOptions(info,optionsInfo[r]):
            r -= 1
            continue
        break      
    options.insert(r+1,cell)
    optionsInfo.insert(r+1,info)

def updateOptions(options,optionsInfo,cell,freedom,rowsize,dir):
    info = [0,{rowsize:{dir:freedom}},0,0]
    if rowsize == 2:
        info[2] = freedom
    elif rowsize == 3:
        info[3] = 1
    l,r = 0,len(options)-1
    if cell in options:
        i = options.index(cell)
        info = optionsInfo[i]
        dirExists = False
        for s in info[1]:
            if rowsize == s:
                if s == 2:
                    info[2] += freedom
                elif s == 3:
                    info[3] += 1
                if dir in info[1][s]:
                    if freedom == 1:
                        info[1][s][dir] = 1
            if dir in info[1][s]:
                dirExists = True
        if not dirExists:
            info[0] += 1 # an intersection
            if rowsize in info[1]:
                info[1][rowsize][dir] = freedom
            else:
                info[1][rowsize] = {dir:freedom}
        optionsInfo.pop(i)
        options.pop(i)
        r = i-1
    insertOption(options,optionsInfo,cell,info,l,r)

def bestOption(cpuOptions,cpuOptionsInfo,plOptions,plOptionsInfo):
    if cpuOptions == [] and plOptions == []:
        return None
    if cpuOptions == [] and plOptions != []:
        return plOptions[0]
    if cpuOptions != [] and plOptions == []:
        return cpuOptions[0]
    cIsBetter = compareOptions(cpuOptionsInfo[0],plOptionsInfo[0])
    if cIsBetter:
        return cpuOptions[0]
    return plOptions[0]

def cpuNextMove(n,thresh,tttboard,pCh,playerData,cCh,cpuData):
    cpuOptions, cpuOptionsInfo = [], []
    plOptions, plOptionsInfo = [], []
    free3 = []
    # check if CPU has 4
    if cpuData[-1] != {}:
        for el in cpuData[-1]:
            dir = el[0:2]
            start = cpuData[-1][el][0]
            cell = missingCellsGen(n,thresh,tttboard,dir,start)[0]
            return (cell//n,cell%n,True)
    # check if Player has 4
    if playerData[-1] != {}:
        for el in playerData[-1]:
            dir = el[0:2]
            start = playerData[-1][el][0]
            cell = missingCellsGen(n,thresh,tttboard,dir,start)[0]
            return(cell//n,cell%n,False)
    # check if CPU has 3
    if cpuData[-2] != {}:
        for el in cpuData[-2]:
            dir = el[0:2]
            for start in cpuData[-2][el]:
                freedom = isGroupFree(start,cCh,pCh,n,dir,tttboard,thresh)
                empty = missingCellsGen(n,thresh,tttboard,dir,start)
                if freedom[0] == 1:
                    for cell in freedom[1]:
                        return (cell//n,cell%n,False)
                for cell in empty:
                    if cell in freedom:
                        continue
                    if cell in cpuOptions:
                        i = cpuOptions.index(cell)
                        if 3 in cpuOptionsInfo[i]:
                            return (cell//n,cell%n,False)
                    updateOptions(cpuOptions,cpuOptionsInfo,cell,0,3,dir) # rowsize is 3 in a row
    # check if Player has 3
    if playerData[-2] != {}:
        for el in playerData[-2]:
            dir = el[0:2]
            for start in playerData[-2][el]:
                freedom = isGroupFree(start,pCh,cCh,n,dir,tttboard,thresh)
                empty = missingCellsGen(n,thresh,tttboard,dir,start)
                if freedom[0] == 1:
                    for cell in freedom[1]:
                        if cell not in free3:
                            free3.append(cell)
                for cell in empty:
                    if cell in freedom[1]:
                        continue
                    updateOptions(plOptions,plOptionsInfo,cell,0,3,dir) # rowsize is 3 in a row
    # check if CPU has 2
    if cpuData[-3] != {}:
        for el in cpuData[-3]:
            dir = el[0:2]
            for start in cpuData[-3][el]:
                freedom = isGroupFree(start,cCh,pCh,n,dir,tttboard,thresh)
                empty = missingCellsGen(n,thresh,tttboard,dir,start)
                for cell in empty:
                    if freedom[0] == 1:
                        if cell in freedom[1]:
                            if cell in cpuOptions:
                                i = cpuOptions.index(cell)
                                if 3 in cpuOptionsInfo[i][1]:
                                    return (cell//n,cell%n,False)
                            updateOptions(cpuOptions,cpuOptionsInfo,cell,1,2,dir)
                            continue
                    updateOptions(cpuOptions,cpuOptionsInfo,cell,0,2,dir)
    # check if Player has 2
    if playerData[-3] != {}:
        for el in playerData[-3]:
            dir = el[0:2]
            for start in playerData[-3][el]:
                freedom = isGroupFree(start,pCh,cCh,n,dir,tttboard,thresh)
                empty = missingCellsGen(n,thresh,tttboard,dir,start)
                for cell in empty:
                    if freedom[0] == 1:
                        if cell in freedom[1]:
                            updateOptions(plOptions,plOptionsInfo,cell,1,2,dir)
                            continue
                    updateOptions(plOptions,plOptionsInfo,cell,0,2,dir)
    # check if CPU has 1
    # check if Player has 1
    print("free3")
    print(free3)
    if free3 != []:
        plBest = -1
        for i in range(len(plOptions)):
            if plOptions[i] in free3:
                plBest = i
                break
        cpuBest = -1
        for i in range(len(cpuOptions)):
            if cpuOptions[i] in free3:
                cpuBest = i
                break
        if cpuBest == -1 and plBest != -1:
            cell = plOptions[plBest]
            return (cell//n,cell%n,False)
        if cpuBest != -1 and plBest == -1:
            cell = cpuOptions[cpuBest]
            return (cell//n,cell%n,False)
        print('cpuBest',cpuBest)
        print('plBest:',plBest)
        if cpuBest != -1 and plBest != -1:
            if compareOptions(cpuOptionsInfo[cpuBest],plOptionsInfo[plBest]):
                cell = cpuOptions[cpuBest]
                return (cell//n,cell%n,False)
            cell = plOptions[plBest]
            return (cell//n,cell%n,False)
        return (free3[0]//n,free3[0]%n,False)
    best = bestOption(cpuOptions,cpuOptionsInfo,plOptions,plOptionsInfo)
    if best != None:
        return (best//n,best%n,False)
    for dir in cpuData[0]:
        for start in cpuData[0][dir]:
            empty = missingCellsGen(n,thresh,tttboard,dir,start)
            if empty == []:
                continue
            return (empty[0]//n,empty[0]%n,False)
    for dir in playerData[0]:
        for start in playerData[0][dir]:
            empty = missingCellsGen(n,thresh,tttboard,dir[0:2],start)
            if empty == []:
                continue
            return (empty[0]//n,empty[0]%n,False)
    for i in range(n):
        for j in range(n):
            if tttboard[i][j] == " ":
                return (i,j,False)

def hasPlayerWon(x,y,n,tttboard,pCh,thresh,playerData):
    cell = x*n+y
    for dir in playerData[-1]:
        for start in playerData[-1][dir]:
            empty = missingCellsGen(n,thresh,tttboard,dir[0:2],start)
            if cell in empty:
                return True

def playGame2(n,thresh):
    tttboard = [] # this keeps record of the board, either X or O or " "
    # generate a double array of spaces as an initial board
    for i in range(n):
        inner = []
        for j in range(n):
            inner.append(' ')
        tttboard.append(inner)

    # data
    playerData = [{} for i in range(thresh-1)]
    cpuData = [{} for i in range(thresh-1)]

    # choose X or O
    plCh = ''
    while plCh != 'X' and plCh != 'O':
        plCh = input('Choose X or O for yourself\n>> ').upper()
    chSelect = {'X':'O','O':'X'}
    cpuCh = chSelect[plCh] 

    plays = 0 # number of time both players have played in total
    won = None # To check if someone has won. If anyone wins, won is going to be
    # a  string: X wins, O wins, or DRAW
    currPlayer = True # boolean to check player 1 or 2
    
    with open('entries.txt','w') as fh:
        drawBoard(tttboard) # displays inital empty board
        x,y = playerNextMove(n,tttboard)
        tttboard[x][y] = plCh
        fh.write(plCh+','+str(x)+','+str(y)+'\n')
        updateData(x,y,plCh,cpuCh,n,tttboard,thresh,playerData,cpuData)
        x,y = n//2, n//2
        if tttboard[x][y] != plCh:
            tttboard[x][y] = cpuCh
            fh.write(cpuCh+','+str(x)+','+str(y)+'\n')
        else:
            tttboard[x][y-1] = cpuCh
            fh.write(cpuCh+','+str(x)+','+str(y-1)+'\n')
            y -= 1
        updateData(x,y,plCh,cpuCh,n,tttboard,thresh,playerData,cpuData)
        plays += 2
        drawBoard(tttboard)
    while (won == None): # if won is None, no player has won
        hasWon = False
        if currPlayer:
            print("Player's turn") # if currPlayer is true player 1 is to play
            currCh = plCh
            x,y = playerNextMove(n,tttboard)
            if playerData[-1] != {}:
                # check to find the winning cell and compare
                hasWon = hasPlayerWon(x,y,n,tttboard,plCh,thresh,playerData)
        else:
            print("CPU's turn") # if currPlayer is false player 2 is to play
            currCh = cpuCh
            x,y,hasWon = cpuNextMove(n,thresh,tttboard,plCh,playerData,cpuCh,cpuData)
            print('CPU move:\n\t',x,y)
        
        # check if any player has won
        tttboard[x][y] = currCh
        with open('entries.txt','a') as fh:
            fh.write(currCh+','+str(x)+','+str(y)+'\n')
        if hasWon:
            drawBoard(tttboard)
            won = currCh + " wins"
            continue
        updateData(x,y,plCh,cpuCh,n,tttboard,thresh,playerData,cpuData)
        print(playerData)
        print(cpuData)
        
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

def playGame(n,thresh):
    tttboard = [] # this keeps record of the board, either X or O or " "
    # generate a double array of spaces as an initial board
    for i in range(n):
        inner = []
        for j in range(n):
            inner.append(' ')
        tttboard.append(inner)

    # data
    playerData = [{} for i in range(thresh-1)]
    cpuData = [{} for i in range(thresh-1)]

    # choose X or O
    plCh = ''
    while plCh != 'X' and plCh != 'O':
        plCh = input('Choose X or O for yourself\n>> ').upper()
    chSelect = {'X':'O','O':'X'}
    cpuCh = chSelect[plCh] 

    plays = 0 # number of time both players have played in total
    won = None # To check if someone has won. If anyone wins, won is going to be
    # a  string: X wins, O wins, or DRAW
    currPlayer = True # boolean to check player 1 or 2
    
    drawBoard(tttboard) # displays inital empty board
    x,y = playerNextMove(n,tttboard)
    tttboard[x][y] = plCh
    updateData(x,y,plCh,cpuCh,n,tttboard,thresh,playerData,cpuData)
    x,y = n//2, n//2
    if tttboard[x][y] != plCh:
        tttboard[x][y] = cpuCh
    else:
        tttboard[x][y-1] = cpuCh
        y -= 1
    updateData(x,y,plCh,cpuCh,n,tttboard,thresh,playerData,cpuData)
    plays += 2
    drawBoard(tttboard)

    while (won == None): # if won is None, no player has won
        hasWon = False
        if currPlayer:
            print("Player's turn") # if currPlayer is true player 1 is to play
            currCh = plCh
            x,y = playerNextMove(n,tttboard)
            if playerData[-1] != {}:
                # check to find the winning cell and compare
                hasWon = hasPlayerWon(x,y,n,tttboard,plCh,thresh,playerData)
        else:
            print("CPU's turn") # if currPlayer is false player 2 is to play
            currCh = cpuCh
            x,y,hasWon = cpuNextMove(n,thresh,tttboard,plCh,playerData,cpuCh,cpuData)
            print('CPU move:\n\t',x,y)
        
        # check if any player has won
        tttboard[x][y] = currCh
        if hasWon:
            drawBoard(tttboard)
            won = currCh + " wins"
            continue
        updateData(x,y,plCh,cpuCh,n,tttboard,thresh,playerData,cpuData)
        print(playerData)
        print(cpuData)
        
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

def newDispText(SCREEN,backCol,txtCol,text,textSize,textPos,surfSize,surfPos):
    whiteSurf = pygame.Surface(surfSize)
    whiteSurf.fill(backCol)
    fontObj = pygame.font.SysFont('consolas',textSize)
    textSurfObj = fontObj.render(text,True,txtCol)
    textRect = textSurfObj.get_rect()
    textRect.top = textPos[0]
    textRect.left = textPos[1]
    whiteSurf.blit(textSurfObj,textRect)
    SCREEN.blit(whiteSurf,surfPos)
    pygame.display.update()

def getInputSpot(cW,hW):
    mouseX = 0
    mouseY = 0
    mouseClicked = False

    while True:
        event = pygame.event.wait()
        if event.type == QUIT:
            x = -10000
            y = -10000
            break
        elif event.type == MOUSEBUTTONUP:
            mouseX,mouseY = pygame.mouse.get_pos()
            y = (mouseX)//cW - 1
            x = (mouseY-hW)//cW - 1
            break
    return x,y

def chooseXorO(SCREEN,n,cW,hW):
    surfPos = (60,10)
    surfSize = (cW*n/2+20,50)
    textSize = 40
    textPos = (20,20)
    newDispText(SCREEN,BLUE,WHITE,'Choose',textSize,textPos,surfSize,surfPos)
    gap = 20
    txtSize = 50
    txtPos = (15,15)
    surfSize = (70,70)
    (L,B) = SCREEN.get_size()
    # surfPos = ((n+2)*cW//2-gap-surfSize[0],15)
    surfPos = (L//2-gap-surfSize[0],15)
    newDispText(SCREEN,WHITE,BLACK,'X',txtSize,txtPos,surfSize,surfPos)
    # surfPos = ((n+2)*cW//2+gap,15)
    surfPos = (L//2+gap,15)
    newDispText(SCREEN,WHITE,BLACK,'O',txtSize,txtPos,surfSize,surfPos)
    while True:
        event = pygame.event.wait()
        if event.type == QUIT:
            x = -10000
            y = -10000
            break
        elif event.type == MOUSEBUTTONUP:
            mouseX,mouseY = pygame.mouse.get_pos()
            if 15 < mouseY < 15+surfSize[1]:
                if L//2-gap-surfSize[0] < mouseX < L//2-gap:
                    pygame.draw.rect(SCREEN,BLUE,(0,0,L,hW))
                    pygame.display.update()
                    return 'X'
                if L//2+gap < mouseX < L//2+gap+surfSize[0]:
                    pygame.draw.rect(SCREEN,BLUE,(0,0,L,hW))
                    pygame.display.update()
                    return 'O'

def playGameGUI(n,thresh):
    pygame.init()
    cW = 60 # cell width
    hW = 100 # header width
    surfPos = (0,45)
    surfSize = (300+20,50)
    textSize = 20
    textPos = (20,20)
    SCREEN = pygame.display.set_mode((cW*(n+2),(n+2)*cW+hW))
    SCREEN.fill(BLUE)
    pygame.draw.rect(SCREEN,WHITE,(0,hW,(n+2)*cW,(n+2)*cW))
    for i in range(cW,cW*(n+2),cW):
        pygame.draw.line(SCREEN,BLACK,(cW,hW+i),((n+1)*cW,hW+i),3)
        pygame.draw.line(SCREEN,BLACK,(i,hW+cW),(i,hW+cW*(n+1)),3)
    for i in range(n):
        sSize = (0.9*cW,0.9*cW)
        sPos = (1,hW+cW+i*cW)
        newDispText(SCREEN,BLUE,WHITE,str(i),textSize,textPos,sSize,sPos)
        sPos = (1+cW+i*cW,hW+1)
        newDispText(SCREEN,BLUE,WHITE,str(i),textSize,textPos,sSize,sPos)

    XSurf = pygame.Surface((44,44))
    XSurf.fill(WHITE)
    pygame.draw.line(XSurf,RED,(0,0),(44,44),5)
    pygame.draw.line(XSurf,RED,(0,44),(44,0),5)
    OSurf = pygame.Surface((56,56))
    OSurf.fill(WHITE)
    pygame.draw.circle(OSurf,BLUE,(28,28),22,5)
    pygame.display.update()

    tttboard = [] # this keeps record of the board, either X or O or " "
    # generate a double array of spaces as an initial board
    for i in range(n):
        inner = []
        for j in range(n):
            inner.append(' ')
        tttboard.append(inner)

    # data
    playerData = [{} for i in range(thresh-1)]
    cpuData = [{} for i in range(thresh-1)]

    # choose X or O
    plCh = chooseXorO(SCREEN,n,cW,hW)
    # plCh = ''
    # while plCh != 'X' and plCh != 'O':
    #     plCh = input('Choose X or O for yourself\n>> ').upper()
    chSelect = {'X':'O','O':'X'}
    cpuCh = chSelect[plCh] 

    plays = 0 # number of time both players have played in total
    won = None # To check if someone has won. If anyone wins, won is going to be
    # a  string: X wins, O wins, or DRAW
    currPlayer = True # boolean to check player 1 or 2
    
    # drawBoard(tttboard) # displays inital empty board
    print("Player's turn")
    x,y = playerNextMove(n,tttboard,SCREEN,cW,hW,textSize,textPos,surfSize,surfPos)
    tttboard[x][y] = plCh
    if plCh == 'X':
        XRect = XSurf.get_rect()
        XRect.center = (cW*(y+1)+cW//2,hW+cW*(x+1)+cW//2)
        SCREEN.blit(XSurf,XRect)
    elif plCh == 'O':
        ORect = OSurf.get_rect()
        ORect.center = (cW*(y+1)+cW//2,hW+cW*(x+1)+cW//2)
        SCREEN.blit(OSurf,ORect)
    pygame.display.update()
    updateData(x,y,plCh,cpuCh,n,tttboard,thresh,playerData,cpuData)
    x,y = n//2, n//2
    if tttboard[x][y] != plCh:
        tttboard[x][y] = cpuCh
    else:
        tttboard[x][y-1] = cpuCh
        y -= 1
    if cpuCh == 'X':
        XRect = XSurf.get_rect()
        XRect.center = (cW*(y+1)+cW//2,hW+cW*(x+1)+cW//2)
        SCREEN.blit(XSurf,XRect)
    elif cpuCh == 'O':
        ORect = OSurf.get_rect()
        ORect.center = (cW*(y+1)+cW//2,hW+cW*(x+1)+cW//2)
        SCREEN.blit(OSurf,ORect)
    pygame.display.update()
    updateData(x,y,plCh,cpuCh,n,tttboard,thresh,playerData,cpuData)
    plays += 2
    # drawBoard(tttboard)

    while (won == None): # if won is None, no player has won
        hasWon = False
        if currPlayer:
            print("Player's turn") # if currPlayer is true player 1 is to play
            newDispText(SCREEN,BLUE,WHITE,"Player's turn",textSize,textPos,surfSize,surfPos)
            currCh = plCh
            x,y = playerNextMove(n,tttboard,SCREEN,cW,hW,textSize,textPos,surfSize,surfPos)
            if x == -10000:
                won == 'END'
                break
            if playerData[-1] != {}:
                # check to find the winning cell and compare
                hasWon = hasPlayerWon(x,y,n,tttboard,plCh,thresh,playerData)
        else:
            print("CPU's turn") # if currPlayer is false player 2 is to play
            newDispText(SCREEN,BLUE,WHITE,"CPU's turn",textSize,textPos,surfSize,surfPos)
            currCh = cpuCh
            x,y,hasWon = cpuNextMove(n,thresh,tttboard,plCh,playerData,cpuCh,cpuData)
            print('CPU move:\n\t',x,y)
        
        text = 'row: ' + str(x) + ", col: " + str(y)
        newDispText(SCREEN,BLUE,WHITE,text,textSize,textPos,surfSize,(300+25,20))
        # check if any player has won
        print(currCh,',',x,',',y)
        tttboard[x][y] = currCh
        drawBoard(tttboard)
        if currCh == 'X':
            XRect = XSurf.get_rect()
            XRect.center = (cW*(y+1)+cW//2,hW+cW*(x+1)+cW//2)
            SCREEN.blit(XSurf,XRect)
        elif currCh == 'O':
            ORect = OSurf.get_rect()
            ORect.center = (cW*(y+1)+cW//2,hW+cW*(x+1)+cW//2)
            SCREEN.blit(OSurf,ORect)
        pygame.display.update()
        if hasWon:
            drawBoard(tttboard)
            won = currCh + " wins"
            continue
        updateData(x,y,plCh,cpuCh,n,tttboard,thresh,playerData,cpuData)
        
        # if nobody has won
        # drawBoard(tttboard) # show the updated board
        plays += 1 # increase the number of those who have played
        currPlayer = not currPlayer # change the player to the next player

        # if people have played n^2 times, the whole board is filled.
        # it's a draw
        if plays == n**2:
            won = "DRAW"
        
    # this runs after won has changed to either "X wins", "O wins", or "DRAW"    
    print(won)
    newDispText(SCREEN,BLUE,WHITE,won,textSize,textPos,surfSize,surfPos)
    pygame.time.delay(1500)

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

playGameGUI(10,5)