###########################################################################
#                                                                         #
#-------------------------------------------------------------------------#
#          cal_couches_v4.3.py --- manu_fakto --- 2017-01-09              #
#-------------------------------------------------------------------------#
#                                                                         #
###########################################################################
import Rhino
import System.Drawing.Color
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import time
from os import chdir

def reset_layers_default():
    rs.CurrentLayer("Default")
    layers = rs.LayerNames()    
    for layer in layers:
        if rs.LayerVisible(layer) and layer!='Default':
            rs.LayerVisible(layer,False)
    #rs.Command('_-SelAll _Enter')
    #rs.Command('_-Delete _Enter')

def printLnDelay(n,t):
    for i in range(n):
        print
        time.sleep(t)
    
def printMsg(str):
    print('---------------------------------------------------------------------------------------')
    print('                             '+str)
    print('---------------------------------------------------------------------------------------')
        
if __name__ == '__main__':
    
    rs.ClearCommandHistory()
    
    print('------------------------------------------------------------------------------------------------------')
    print('                         cal_couches.py  ---  manu_fakto  ---  2017  ')
    print('')
    print('              !!! bien positionner le scan exterieur et interieur en 0,0,0 !!!')
    print('------------------------------------------------------------------------------------------------------')

    layAltZ = []
    intLayAltZ = []
    layName = []
    crvsOut = []
    crvsIn = []
    srfsBot = []
    srfsInt = []
    srfsTop = []
    srfs = []
    pts = []
    #######################################################################
    
    rs.Command('_-4View _Enter',echo = False)
    rs.Command('_-Zoom a e _Enter',echo = False)
    rs.ViewDisplayMode(view = 'Perspective', mode = 'X-Ray')
    rs.Command('_-MaxViewport',echo = False)
    brepOut = rs.GetObject("scan exterieur ", rs.filter.polysurface)
    brepIn = rs.GetObject("scan interieur ", rs.filter.polysurface)
    thikLays = rs.GetInteger("Epaisseur des couches ",100,20,500)
    nbIntLays = rs.GetInteger("Nb de couches intermediaires ",0,0,50)
    rs.Command('_-4View _Enter',echo = False)
    rs.Command('_-Zoom a e _Enter',echo = False)
    rs.ViewDisplayMode(view = 'Perspective', mode = 'Rendered')
    rs.Command('_-MaxViewport',echo = False)
    
    #######################################################################
    version = "4.3.2016.01.09"
    timeStart = time.time()
    docName = rs.DocumentName()
	#######################################################################


    brepOut = rs.coercebrep(brepOut)
    brepIn = rs.coercebrep(brepIn)
    boxRS = rs.BoundingBox(brepOut)
    maxX = int(boxRS[1].X-boxRS[0].X)
    maxY = int(boxRS[3].Y-boxRS[0].Y)
    maxZ = int(boxRS[4].Z-boxRS[0].Z)
    nbLays = (int) (maxZ / thikLays) + 1
    intLays = (int) (thikLays / (nbIntLays+1))
    curLay = rs.CurrentLayer()
    printLnDelay(4,0.1)
    printMsg("creation des calques ...")
    time.sleep(0.2)

    ### make layers list with altZ
    altZ = 0
    for i in range(nbLays):
        layAltZ.append(altZ)
        altZ += thikLays

    ### make intLays list with altZ
    altZ = 0
    for i in range(nbLays):
        altZ = layAltZ[i]
        for j in range(nbIntLays):
            altZ += intLays
            intLayAltZ.append(altZ)

    ### make layName list
    for i in range(nbLays):
        nameL = 'CB'+(len(str(nbLays))-len(str(i+1)))*'0'+str(i+1)+'-'
        nameZ = (len(str(maxZ))-len(str(layAltZ[i])))*'0'+str((layAltZ[i]))
        layName.append(nameL+nameZ)
    
    ### add layers
    c = 0
    rs.AddLayer('CcBois',System.Drawing.Color.LightGray)
    for i in range(nbLays):
        if c == 0:
            rs.AddLayer(layName[i],System.Drawing.Color.Red,parent = 'CcBois')
        if c == 1:
            rs.AddLayer(layName[i],System.Drawing.Color.Blue,parent = 'CcBois')
        if c == 2:
            rs.AddLayer(layName[i],System.Drawing.Color.Purple,parent = 'CcBois')
        if c == 3:
            rs.AddLayer(layName[i],System.Drawing.Color.Green,parent = 'CcBois')
        if c == 4:
            rs.AddLayer(layName[i],System.Drawing.Color.Orange,parent = 'CcBois')
            c = -1
        c = c+1
        
    ### make sections list / bottom & top
    printLnDelay(4,0.1)
    printMsg('calcul des sections ...')
    time.sleep(0.2)
    crvsListOutIn = [[] for i in range(nbLays)]
    for i in range(nbLays):
        origin = (0.0, 0.0, layAltZ[i])
        xAxis = (1.0, 0.0, layAltZ[i])
        yAxis = (0.0, 1.0, layAltZ[i])
        plane = rs.PlaneFromPoints(origin, xAxis, yAxis)
        # intersection with brepOut & brepIn at layAltZ[i]
        resultOut,crvsOut,pts = Rhino.Geometry.Intersect.Intersection.BrepPlane(brepOut, plane, 0.0001)
        resultIn,crvsIn,pts = Rhino.Geometry.Intersect.Intersection.BrepPlane(brepIn, plane, 0.0001)
        #Add crvsOut to crvsListOutIn[i] layer i
        j = 0
        while resultOut and j < len(crvsOut): 
            crvsListOutIn[i].append(crvsOut[j])
            j += 1
        #Add crvsIn to crvsListOutIn[i] layer i
        k = 0
        while resultIn and k < len(crvsIn): 
            crvsListOutIn[i].append(crvsIn[k])
            k += 1
    
    ### make sections list / intLays
    crvsListIntOutIn = [[] for i in range(len(intLayAltZ))]
    m = 0
    for i in range(nbLays):
        l = 0
        while l < nbIntLays and intLayAltZ[m] < maxZ:
            origin = (0.0, 0.0, intLayAltZ[m])
            xAxis = (1.0, 0.0, intLayAltZ[m])
            yAxis = (0.0, 1.0, intLayAltZ[m])
            plane = rs.PlaneFromPoints(origin, xAxis, yAxis)
            # intersection with brepOut & brepIn at intLayAltZ[i]
            resultOut,crvsOut,pts = Rhino.Geometry.Intersect.Intersection.BrepPlane(brepOut, plane, 0.0001)
            resultIn,crvsIn,pts = Rhino.Geometry.Intersect.Intersection.BrepPlane(brepIn, plane, 0.0001)
            #Add crvsOut to crvsListIntOutIn[i] layer i
            j = 0
            while resultOut and j < len(crvsOut): 
                crvsListIntOutIn[m].append(crvsOut[j])
                j += 1
            #Add crvsIn to crvsListIntOutIn[i] layer i
            k = 0
            while resultIn and k < len(crvsIn): 
                crvsListIntOutIn[m].append(crvsIn[k])
                k += 1
            m += 1
            l += 1

    ### add i sfrs
    for i in range(nbLays):
        rs.CurrentLayer(layName[i])
        crvs = []
        for crv in (crvsListOutIn[i]):
            crv = rs.coercecurve(crv)
            crv = Rhino.RhinoDoc.ActiveDoc.Objects.AddCurve(crv)
            crvs.append(crv)
        srfsBot.append(rs.AddPlanarSrf(crvs)) 
        rs.DeleteObjects(crvs)

    ### add & move down i+1 sfrs 
    for i in range(nbLays-1):
        rs.CurrentLayer(layName[i])
        crvs = []
        for crv in (crvsListOutIn[i+1]):
            crv = rs.coercecurve(crv)
            crv = Rhino.RhinoDoc.ActiveDoc.Objects.AddCurve(crv)
            crvs.append(crv)
        srfsTop.append(rs.AddPlanarSrf(crvs)) 
        rs.DeleteObjects(crvs)
        vector = 0,0,-thikLays
        rs.MoveObjects(srfsTop[i],vector)
    
    ### add & move down inter sfrs
    m = 0
    for i in range(nbLays):
        rs.CurrentLayer(layName[i])
        j = 0
        while j < nbIntLays and intLayAltZ[m] < maxZ:
            crvs = []
            for crv in (crvsListIntOutIn[m]):
                crv = rs.coercecurve(crv)
                crv = Rhino.RhinoDoc.ActiveDoc.Objects.AddCurve(crv)
                crvs.append(crv)
            srfsInt.append(rs.AddPlanarSrf(crvs)) 
            rs.DeleteObjects(crvs)
            vector = 0,0,-(j+1)*intLays
            rs.MoveObjects(srfsInt[m],vector)   
            m += 1
            j += 1

    #intersection at maxZ -1
    origin = (0.0, 0.0, (maxZ-1))
    xAxis = (1.0, 0.0, (maxZ-1))
    yAxis = (0.0, 1.0, (maxZ-1))
    plane = rs.PlaneFromPoints(origin, xAxis, yAxis)
    resultOut,crvsOut,pts = Rhino.Geometry.Intersect.Intersection.BrepPlane(brepOut, plane, 0.0001)
    rs.CurrentLayer(layName[nbLays-1])
    crvs = []
    for crv in (crvsOut):
        crv = rs.coercecurve(crv)
        crv = Rhino.RhinoDoc.ActiveDoc.Objects.AddCurve(crv)
        crvs.append(crv)
    srfsMaxZ = rs.AddPlanarSrf(crvs)
    rs.DeleteObjects(crvs)
    vector = 0,0,-(maxZ-(1+layAltZ[nbLays-1]))
    rs.MoveObjects(srfsMaxZ,vector)
    
    ### surfaces MeshOutline ExtrudeSrf
    printLnDelay(4,0.1)
    printMsg("extrusion des couches ...")
    rs.Command('_-4View _Enter',echo = False)
    rs.Command('_-Zoom a e _Enter',echo = False)
    rs.ViewDisplayMode(view = 'Perspective', mode = 'Ghosted')
    rs.ViewDisplayMode(view = 'Top', mode = 'Ghosted')
    rs.ViewDisplayMode(view = 'Front', mode = 'Ghosted')
    rs.ViewDisplayMode(view = 'Right', mode = 'Ghosted')
    reset_layers_default()
    for i in range(nbLays):
        rs.CurrentLayer(layName[i])
        rs.Command('_SetActiveViewport Top _Enter',echo = False)
        rs.Command('_-selSrf _Enter',echo = False)
        rs.Command('_-Meshoutline _Enter',echo = False)
        rs.Command('_-SelCrv _Enter',echo = False)
        rs.Command('_-Move 0,0,0 0,0,'+str(layAltZ[i]),echo = False) 
        rs.Command('_SelNone _Enter',echo = False)
        rs.Command('_-SelSrf _Enter',echo = False)
        rs.Command('_-Delete _Enter',echo = False)
        rs.Command('_-SelCrv _Enter',echo = False)
        rs.Command('_-PlanarSrf _Enter',echo = False)
        rs.Command('_-SelSrf _Enter',echo = False)
        rs.Command('_-ExtrudeSrf '+str(thikLays)+' _Enter',echo = False)
        rs.Command('_-SelNone _Enter',echo = False)
        rs.Command('_-SelSrf _Enter',echo = False)
        rs.Command('_-Delete _Enter',echo = False)
        rs.Command('_-SelCrv _Enter',echo = False)
        rs.Command('_-Group _Enter',echo = False)
        rs.CurrentLayer("Default")
        rs.LayerVisible(layName[i],False)
    rs.CurrentLayer("Default")
    for i in range(nbLays):
        rs.LayerVisible(layName[i],True)
    rs.Command('_SelCrv _Enter',echo = False)
    rs.Command('_-ProjectToCPlane Yes',echo = False)
    xx = (int(maxX/500)+2)*500
    rs.Command('_move 0,0,0 '+str(xx)+',0,0',echo = False)
    rs.Command('_SelNone _Enter',echo = False)
    rs.Command('_-selSrf _Enter',echo = False)
    rs.Command('_Delete _Enter',echo = False)
    rs.Command('_-4View _Enter',echo = False)
    rs.Command('_-Zoom a e _Enter',echo = False)
    rs.Command('_SetActiveViewport Perspective _Enter',echo = False)
    rs.ViewDisplayMode(view = 'Perspective', mode = 'Rendered')
    rs.ViewDisplayMode(view = 'Top', mode = 'Ghosted')
    rs.ViewDisplayMode(view = 'Front', mode = 'Ghosted')
    rs.ViewDisplayMode(view = 'Right', mode = 'Ghosted')
    rs.Command('_-MaxViewport _Enter',echo = False)
    rs.LayerVisible(curLay,True)
    printLnDelay(4,0.1)
    timeEnd = time.time()
    timeRun = timeEnd-timeStart
    print('---------------------------------------------------------------------------------------')
    print('          cal_couches.py  ---  manu_fakto  ---  2017      '+str(int(timeRun))+' sec.')
    print('---------------------------------------------------------------------------------------')
    chdir("C:\Users\MC\Box Sync")
    logTxt = open('CAL_COUCHES_LOG.TXT','a')
    logTxt.write(str(version)+' '+docName+' '+str(nbLays)+' ')
    logTxt.write(str(thikLays)+' '+str(nbIntLays)+' '+str(int(timeRun))+' sec.\n')
    logTxt.close()