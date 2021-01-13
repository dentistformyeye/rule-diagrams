import csv
import svgwrite
from svgwrite import rgb
import math
import os
import sys
from lxml import etree

folderPath=os.getcwd()

charW=7.25 #Approximate default width of an svgwrite text char
mu=8 #Minimum unit. The min margin around text
scale=30 #Value to ensure most final widths/heights are >1.0
cm=37 #Half should be > the default height of an svgwrite text char
hu=0.5*cm #Half unit. Should be 0.5*cm
keyH=0.7*hu #Size of blocks for the key. Should be < hu
fillOpacity=0.66 #Fill opacity for overlapping blocks. Should be >0 and <1
mwm=0.030 #Minimum width in microns. In case arrows become indistinct
checkmark=u"\u2713"
no=u"\u20E0"
classes="""
    .background {fill:white;}
    .default {fill:grey;}
    .diff {fill:rgb(196,157,113);}
    .tap {fill:rgb(121,196,113);}
    .poly {fill:rgb(212,90,92);}
    .mcon {fill:rgb(204,202,204);stroke-width:1;stroke:black;}
    .met1 {fill:rgb(190,144,217);}
    .huge_met1 {fill:rgb(160,114,187);}
    .via {fill:rgb(59,0,246);}
    .checkmark {fill:rgb(0,192,0);font-size:74px;}
    .no {fill:rgb(179,0,0);font-size:74px;}
    
"""

def sqrt(x):
    xF=float(x)
    return math.sqrt(xF) if (xF>=0) else -math.sqrt(-xF)

def textW(string):
    return len(string)*charW

def arrow(d,x1,y1,x2,y2,sc="black",sw=1):
    cos=0.866
    sin=0.5
    dx=sqrt(x2-x1)
    dy=sqrt(y2-y1)
    d.add(d.line((x1,y1),(x2,y2),stroke=sc,stroke_width=sw))
    d.add(d.line((x2,y2),(x2-(dx*cos+dy*-sin),y2-(dx*sin+dy*cos)),stroke=sc,stroke_width=sw))
    d.add(d.line((x2,y2),(x2-(dx*cos+dy*sin),y2-(dx*-sin+dy*cos)),stroke=sc,stroke_width=sw))

def solidLine(d,x1,y1,x2,y2,sc="black",sw=1):
    d.add(d.line((x1,y1),(x2,y2),stroke=sc,stroke_width=sw))

def dashedLine(d,x1,y1,x2,y2,da="8,8",sc="black",sw=1):
    d.add(d.line((x1,y1),(x2,y2),stroke=sc,stroke_width=sw,style=f"stroke-dasharray:{da};"))

def keyRow(d,keyY,material,comment="",x=0,mult=1,opacity=1.0):
    keyHL=keyH*mult
    d.add(d.rect(insert=(x,keyY-keyHL),size=(keyHL,keyHL),class_=material,style=f"fill-opacity:{opacity};"))
    m=material
    if comment:
        m+=comment
    d.add(d.text(m,insert=(x+keyHL+mu,keyY)))
    return keyY+hu

def parseR(r):
    rule=r
    comment=""
    extraRule=""
    if "#" in rule:
        i=1
        notHash=True
        while notHash and i<=len(r):
            if(r[-i]=="#"):
                notHash=False
                rule=r[:-i]
                comment=r[len(r)-i+1:]
            i+=1
    if "&" in rule:
        rule,extraRule=rule.split("&",1)
    return [rule,extraRule,comment]

def parseM(m):
    material=m
    comment=""
    extraRule=""
    if "#" in material:
        i=1
        notHash=True
        while notHash and i<=len(m):
            if(m[-i]=="#"):
                notHash=False
                material=m[:-i]
                comment=m[len(m)-i+1:]
            i+=1
        comment=comment.replace("_"," ")
    if "&" in material:
        material,extraRule=material.split("&",1)
    return [material,extraRule,comment]

def drawRectExact(d,material,x,y,exactWidth,exactHeight):
    d.add(d.rect(insert=(x,y),size=(exactWidth,exactHeight),class_=material))

def drawRect(d,material,x,y,valueW,valueH):
    width=float(valueW)*scale*cm
    height=float(valueH)*scale*cm
    d.add(d.rect(insert=(x,y),size=(width,height),class_=material))
    return width,height

def drawWidth(d,material,value,x=0,y=0):
    width=float(value)*scale*cm
    height=width*1.5
    if "#" in material or "&" in material:
        material=parseM(material)[0]
    d.add(d.rect(insert=(x,y),size=(width,height),class_=material))
    return [width,height]

def drawWidthF(x=0,y=0):
    d=svgwrite.Drawing(filename=fn)
    d.defs.add(d.style(classes))
    material=materials
    mExtraRule=""
    mComment=""
    if "#" in material or "&" in material:
        material,mExtraRule,mComment=parseM(materials)
    width,height=drawWidth(d,material,value,x,y)
    arrow(d,x,x+height+1*hu,x+width,y+height+1*hu)
    arrow(d,x+width,y+height+1*hu,x,y+height+1*hu)
    descText=f"width >= {value}µm"
    if "exact" in rule:
        descText+=f", width <= {value}µm"
    d.add(d.text(descText,insert=(x,y+height+2*hu)))
    d.add(d.text(nameC,insert=(x,y+height+3*hu)))
    keyY=y+height+4*hu
    keyRow(d,keyY,material,mComment,x)
    d.save()
    tree=etree.parse(fn)
    svgTag=tree.getroot()
    w=max(width,textW(descText),keyH+mu+textW(material))
    h=keyY+mu
    svgTag.set("viewBox",f"0 0 {w} {h}")
    tree.write(fn)

def drawSize(d,material,values,x=0,y=0):
    valueW,valueH=values.split(" ")
    width,height=drawRect(d,material,x,y,valueW,valueH)
    return valueW,valueH,width,height

def drawSizeF(x=0,y=0,width=0.100,height=0.100):
    d=svgwrite.Drawing(filename=fn)
    d.defs.add(d.style(classes))
    material=materials
    mExtraRule=""
    mComment=""
    if "#" in material or "&" in material:
        material,mExtraRule,mComment=parseM(materials)
    valueW,valueH,width,height=drawSize(d,material,value,x,y)
    arrow(d,x,y+height+1*hu,x+width,y+height+1*hu)
    arrow(d,x+width,y+height+1*hu,x,y+height+1*hu)
    descTextW=f"width >= {valueW}µm"
    if "exact" in rule:
        descTextW+=f", width <= {valueW}µm"
    d.add(d.text(descTextW,insert=(x,y+height+2*hu)))
    d.add(d.text(nameC,insert=(x,y+height+3*hu)))
    arrow(d,x+width+1*hu,y,x+width+1*hu,y+height)
    arrow(d,x+width+1*hu,y+height,x+width+1*hu,y)
    descTextH=f"height >= {valueH}µm"
    if "exact" in rule:
        descTextH+=f", height <= {valueH}µm"
    d.add(d.text(descTextH,insert=(x+width+2*hu,y+1*hu)))
    keyY=y+height+4*hu
    keyRow(d,keyY,materials,mComment,x)
    d.save()
    tree=etree.parse(fn)
    svgTag=tree.getroot()
    w=max(x+width+2*hu+textW(descTextH),keyH+mu+textW(materials))
    h=keyY+mu
    svgTag.set("viewBox",f"0 0 {w} {h}")
    tree.write(fn)

def drawSpacing(d,first,second,value,x1=0,y1=0,orientation="h",width=0,height=0):
    space=float(value)*scale*cm
    if not width:
        width=space
        height=width
    x2=x1
    y2=y1
    if(orientation=="v"):
        y2+=height+space
    else:
        x2+=width+space
    drawRectExact(d,first,x1,y1,width,height)
    drawRectExact(d,second,x2,y2,width,height)
    return width,height,first,second,x2,y2

def drawSpacingF(x1=0,y1=0,mList="",orientation="h",width=0,height=0):
    d=svgwrite.Drawing(filename=fn)
    d.defs.add(d.style(classes))
    if not mList:
        mList=materials.split(" ")
    first="default"
    second="default"
    if len(mList)>=2:
        first,second=mList[0],mList[1]
    elif len(materials)==1:
        first,second=mList[0],mList[0]
    mExtraRule1,mComment1,mExtraRule2,mComment2="","","",""
    width,height,first,second,x2,y2=drawSpacing(d,first,second,value,x1,y1,orientation,width,height)
    if orientation=="v":
        arrow(d,x1+width,y1+height,x2+width,y2)
        arrow(d,x2+width,y2,x1+width,y1+height)
    else:
        arrow(d,x1+width,y1+height,x2,y2+height)
        arrow(d,x2,y2+height,x1+width,y1+height)
    descText=f"space >= {value}µm"
    d.add(d.text(descText,insert=(x1+width+mu,y1+height+mu+1*hu)))
    d.add(d.text(nameC,insert=(x1+width+mu,y1+mu+height+mu+2*hu)))
    keyY=y2+height+(1 if orientation=="v" else 3)*hu
    keyY=keyRow(d,keyY,first,mComment1,x1)
    if first != second:
        keyRow(d,keyY,second,mComment2,x1)
    d.save()
    tree=etree.parse(fn)
    svgTag=tree.getroot()
    w=max(x2+mu+width,x1+width+textW(descText),keyH+mu+textW(first),keyH+mu+textW(second))
    h=keyY+mu
    svgTag.set("viewBox",f"0 0 {w} {h}")
    tree.write(fn)

def drawWideSpacing(d,main,extension,value,x=0,y=0):
    width=float(value)*scale*cm
    height=width
    widthS=float(value)*0.2*scale*cm
    heightS=widthS*.75
    x1=x+width
    y1=y
    x2=x+width
    y2=y1+heightS+widthS
    d.add(d.rect(insert=(x,y),size=(width,height),class_=main))
    d.add(d.rect(insert=(x1,y1),size=(widthS*2,heightS),class_=extension))
    d.add(d.rect(insert=(x2,y2),size=(widthS*2,heightS),class_=extension))
    d.add(d.rect(insert=(x1+widthS,y1),size=(widthS,heightS+mu),class_=extension))
    return width,height,widthS,heightS,x1,y1,x2,y2

def drawWideSpacingF(x=0,y=0,mList=""):
    d=svgwrite.Drawing(filename=fn)
    d.defs.add(d.style(classes))
    if not mList:
        mList=materials.split(" ")
    main="default"
    extension="default"
    if len(mList)>=2:
        main,extension=mList[0],mList[1]
    mExtraRuleM,mCommentM,mExtraRuleE,mCommentE="","","",""
    if "#" in main or "&" in main:
        main,mExtraRuleM,mCommentM=parseM(main)
    if "#" in extension or "&" in extension:
        extension,mExtraRuleE,mCommentE=parseM(extension)
    width,height,widthS,heightS,x1,y1,x2,y2=drawWideSpacing(d,main,extension,value,x,y)
    dashedLine(d,x1+widthS,y1,x2+widthS,y2+heightS)
    arrow(d,x1+widthS-mu,y1+heightS,x2+widthS-mu,y2)
    arrow(d,x2+widthS-mu,y2,x1+widthS-mu,y1+heightS)
    descText=f"space >= {value}µm"
    d.add(d.text(descText,insert=(x1+widthS+mu,y1+heightS+1*hu+mu)))
    d.add(d.text(nameC,insert=(x1+widthS+mu,y1+heightS+2*hu+mu)))
    keyY=y+height+2*hu
    keyY=keyRow(d,keyY,main,mCommentM,x,2)
    if extension != main:
        keyRow(d,keyY,extension,mCommentE,x)
    d.save()
    tree=etree.parse(fn)
    svgTag=tree.getroot()
    w=max(x1+width+mu+textW(descText),keyH+mu+textW(main),keyH+mu+textW(extension))
    h=keyY+mu
    svgTag.set("viewBox",f"0 0 {w} {h}")
    tree.write(fn)

def drawArea(d,material,value,x=0,y=0):
    area=float(value)
    width=sqrt(area)*0.25*scale*cm
    height=width*1.5
    d.add(d.rect(insert=(x,y),size=(width,height),class_=materials))
    return width,height

def drawAreaF(x=0,y=0):
    d=svgwrite.Drawing(filename=fn)
    d.defs.add(d.style(classes))
    material=materials
    mExtraRule=""
    mComment=""
    if "#" in material or "&" in material:
        material,mExtraRule,mComment=parseM(materials)
    width,height=drawArea(d,materials,value,x,y)
    solidLine(d,x,y,x+width*0.2,y)
    solidLine(d,x,y,x,y+width*0.2)
    solidLine(d,x+width,y+height,x+width-width*0.2,y+height)
    solidLine(d,x+width,y+height,x+width,y+height-width*0.2)
    descText=f"area >= {value}µm2"
    d.add(d.text(descText,insert=(x+width+mu,height/2)))
    d.add(d.text(nameC,insert=((x+width+mu,height/2+1*hu))))
    keyY=y+height+1*hu
    keyRow(d,keyY,materials,mComment,x)
    d.save()
    tree=etree.parse(fn)
    svgTag=tree.getroot()
    w=max(x+width+mu+textW(descText),keyH+mu+textW(materials))
    h=keyY+mu
    svgTag.set("viewBox",f"0 0 {w} {h}")
    tree.write(fn)

def drawHole(d,materials,value,x=0,y=0):
    material=materials
    mExtraRule=""
    mComment=""
    if "#" in material or "&" in material:
        material,mExtraRule,mComment=parseM(materials)
    area=float(value)
    xIn=sqrt(value)*0.2*scale*cm
    yIn=xIn
    widthIn=sqrt(value)*0.4*scale*cm
    heightIn=widthIn
    widthOut=widthIn*2
    heightOut=widthOut
    d.add(d.rect(insert=(x,y),size=(widthOut,heightOut),class_=material))
    d.add(d.rect(insert=(xIn,yIn),size=(widthIn,heightIn),class_="background"))
    return widthOut,heightOut,widthIn,heightIn,xIn,yIn,material,mComment

def drawHoleF(x=0,y=0):
    d=svgwrite.Drawing(filename=fn)
    d.defs.add(d.style(classes))
    widthOut,heightOut,widthIn,heightIn,xIn,yIn,material,mComment=drawHole(d,materials,value,x,y)
    arrow(d,x+widthOut+1*hu,y+1*hu,(xIn+widthIn)/2,(yIn+heightIn)/2)
    descText=f"area >= {value}µm2"
    d.add(d.text(descText,insert=(x+widthOut+1*hu+mu,y+1*hu)))
    d.add(d.text(nameC,insert=(x+widthOut+1*hu+mu,y+2*hu)))
    keyY=y+heightOut+1*hu
    keyRow(d,keyY,materials,mComment,x)
    d.save()
    tree=etree.parse(fn)
    svgTag=tree.getroot()
    w=max(x+widthOut+1*hu+mu+textW(descText),keyH+mu+textW(materials))
    h=keyY+mu
    svgTag.set("viewBox",f"0 0 {w} {h}")
    tree.write(fn)

def drawEnclosure(d,materials,value,x=0,y=0):
    mList=materials.split(" ")
    outer="default"
    inner="default"
    inner,outer=mList[0],mList[1]
    mExtraRuleO,mCommentO,mExtraRuleI,mCommentI="","","",""
    if "#" in outer or "&" in outer:
        outer,mExtraRuleO,mCommentO=parseM(outer)
    if "#" in inner or "&" in inner:
        inner,mExtraRuleI,mCommentI=parseM(inner)
    valueA=value
    nameA=""
    hasAdjacencyRule=rule.split(" ")[1]=="a"
    if hasAdjacencyRule:
        valueA=lines[lineNum+int(rule.split(" ")[2])][5]
        nameA=lines[lineNum+int(rule.split(" ")[2])][0]
    practicalVal=float(value)
    practicalValA=float(valueA)
    if practicalVal < mwm:
        practicalVal=mwm
    if practicalValA < mwm:
        practicalValA=mwm
    xIn=x+practicalVal*scale*cm
    yIn=y+practicalValA*scale*cm
    widthIn=practicalVal*scale*2*cm
    heightIn=widthIn
    widthOut=widthIn*2
    heightOut=float(practicalValA)*scale*2*cm+heightIn
    d.add(d.rect(insert=(x,y),size=(widthOut,heightOut),class_=outer))
    d.add(d.rect(insert=(xIn,yIn),size=(widthIn,heightIn),class_=inner))
    return practicalVal,practicalValA,hasAdjacencyRule,valueA,nameA,widthOut,heightOut,widthIn,heightIn,xIn,yIn,outer,mCommentO,inner,mCommentI

def drawEnclosureF(x=0,y=0):
    d=svgwrite.Drawing(filename=fn)
    d.defs.add(d.style(classes))
    vpracticalVal,practicalValA,hasAdjacencyRule,valueA,nameA,widthOut,heightOut,widthIn,heightIn,xIn,yIn,outer,mCommentO,inner,mCommentI=drawEnclosure(d,materials,value,x,y)
    dashedLine(d,x,yIn+heightIn,x,y+heightOut)
    dashedLine(d,xIn,yIn+heightIn,xIn,y+heightOut)
    arrow(d,x,y+heightOut+mu,xIn,y+heightOut+mu)
    arrow(d,xIn,y+heightOut+mu,x,y+heightOut+mu)
    descText=f"space >= {value}µm"
    d.add(d.text(descText,insert=(x,y+heightOut+1*hu+mu)))
    d.add(d.text(nameC,insert=(x,y+heightOut+2*hu+mu))) #Horizontal margin complete
    dashedLine(d,xIn+widthIn,y,x+widthOut,y)
    dashedLine(d,xIn+widthIn,yIn,x+widthOut,yIn)
    arrow(d,x+widthOut+mu,y,x+widthOut+mu,yIn)
    arrow(d,x+widthOut+mu,yIn,x+widthOut+mu,y)
    descTextA,nameTextA="",""
    if hasAdjacencyRule:
        descTextA=f"space >= {valueA}µm"
        d.add(d.text(descTextA,insert=(x+widthOut+1*hu+mu,y+1*hu)))
        nameTextA=f"{nameA}"
        d.add(d.text(nameTextA,insert=(x+widthOut+1*hu+mu,y+2*hu))) #Vertical margin complete
    keyY=y+heightOut+3*hu+mu
    keyY=keyRow(d,keyY,outer,mCommentO,x)
    if inner != outer:
        keyRow(d,keyY,inner,mCommentI,x)
    d.save()
    tree=etree.parse(fn)
    svgTag=tree.getroot()
    w=max(x+widthOut+1*hu+mu+textW(descTextA),keyH+mu+textW(outer),keyH+mu+textW(inner))
    h=keyY+mu
    svgTag.set("viewBox",f"0 0 {w} {h}")
    tree.write(fn)

def drawNoOverlap(d,materials,value,x=0,y=0):
    mList=materials.split(" ")
    bottom="default"
    top="default"
    top,bottom=mList[0],mList[1]
    mExtraRuleB,mCommentB,mExtraRuleT,mCommentT="","","",""
    if "#" in bottom or "&" in bottom:
        bottom,mExtraRuleB,mCommentB=parseM(bottom)
    if "#" in top or "&" in top:
        top,mExtraRuleT,mCommentT=parseM(top)
    widthT=0.100*scale*cm
    heightT=widthT*3
    widthB=heightT
    heightB=widthT
    xB=x
    yB=y+heightT/3
    xT=x+widthB/3
    yT=y
    d.add(d.rect(insert=(xB,yB),size=(widthB/2,heightB),class_=bottom))
    classB=bottom
    noInnerCorners="innerCorners" in rule
    if noInnerCorners:
        classB="background"
    d.add(d.rect(insert=(xB+widthB/2,yB),size=(widthB/2,heightB),class_=classB))
    d.add(d.rect(insert=(xB,yB+heightB/2),size=(widthB,heightB/2),class_=bottom))
    noTurns="turns" in rule
    if noTurns:
        d.add(d.rect(insert=(xT,yT),size=(widthT/2,heightT*3/5),class_=top,style=f"fill-opacity:{fillOpacity};"))
        d.add(d.rect(insert=(xT+widthT/2,yT+heightT*2/5),size=(widthT/2,heightT*3/5),class_=top,style=f"fill-opacity:{fillOpacity};"))
    else:
        d.add(d.rect(insert=(xT,yT),size=(widthT,heightT),class_=top,style=f"fill-opacity:{fillOpacity};"))
    return noInnerCorners,noTurns,widthB,heightB,widthT,heightT,xB,yB,xT,yT,bottom,mCommentB,top,mCommentT

def drawNoOverlapF(x=0,y=0):
    d=svgwrite.Drawing(filename=fn)
    d.defs.add(d.style(classes))
    noInnerCorners,noTurns,widthB,heightB,widthT,heightT,xB,yB,xT,yT,bottom,mCommentB,top,mCommentT=drawNoOverlap(d,materials,value,x,y)
    d.add(d.text(no,insert=(x,heightT+3*hu),class_="no"))
    descText=f"{top+mCommentT} cannot overlap {bottom+mCommentB}"
    if noInnerCorners:
        descText=f"{top+mCommentT} cannot overlap inner corners of {bottom+mCommentB}"
    if noTurns:
        descText=f"{top+mCommentT} cannot make 90 degree turns over {bottom+mCommentB}"
    d.add(d.text(descText,insert=(x,heightT+5*hu)))
    d.add(d.text(nameC,insert=(x,heightT+6*hu)))
    keyY=yT+heightT+7*hu
    keyY=keyRow(d,keyY,top,mCommentT,x,1,fillOpacity)
    if bottom != top:
        keyRow(d,keyY,bottom,mCommentB,x)
    d.save()
    tree=etree.parse(fn)
    svgTag=tree.getroot()
    w=max(widthB,textW(descText),keyH+mu+textW(top),keyH+mu+textW(bottom))
    h=keyY+mu
    svgTag.set("viewBox",f"0 0 {w} {h}")
    tree.write(fn)

def drawSingle():
    print(f"{name} {rules}")
    if "width" in rule:
        if " " not in rule or "exact" in rule:
            drawWidthF()
            
    if "size" in rule:
        if " " not in rule or "exact" in rule:
            drawSizeF()
            
    elif "spacing" in rule:
        if " " not in rule:
            drawSpacingF()
            
        if "extend" in rule:
            drawWideSpacingF()
            
    elif "area" in rule:
        if " " not in rule:
            drawAreaF()
            
            
        elif "hole" in rule:
            drawHoleF()
            
    elif "enclosure" in rule:
        if "adjacentz" not in rule:
            drawEnclosureF()
            
    elif "noOverlap" in rule:
        if " " not in rule or "innerCorners" in rule or "turns":
            drawNoOverlapF()


def usage():
    print("diagram.py <argument> ... -<option> ...")
    return 0

def callback_function(arguments, optionlist):
    for filename in arguments:
        with open(filename) as csvFile:
            csvReader = csv.reader(csvFile,delimiter=',')
            global lineNum
            lineNum=0
            global lines
            lines=[]
            for row in csvReader:
                lines.append(row)
            for row in lines:
                if lineNum>=0:
                    global name
                    global rules
                    global materials
                    global value
                    
                    name=row[0]
                    rules=row[1]
                    materials=row[3]
                    value=row[5]
                    
                    global rule
                    global comment
                    global extraRule
                    rule=rules
                    comment=""
                    extraRule=""
                    if "#" in rule or "&" in rule:
                        rule,extraRule,comment=parseR(rules)
                    global nameC
                    nameC=name
                    if comment:
                        nameC+=comment
                    global singleRule
                    singleRule=True
                    if extraRule:
                        singleRule=False

                    global fn
                    global fp
                    fn=name[1:-1]+".svg"
                    fp=folderPath+fn
                    if singleRule:
                        drawSingle()
                    lineNum+=1
    return 0

if __name__ == '__main__':
    
    if len(sys.argv) == 1:
        usage()
        sys.exit(0)
    
    optionlist = []
    arguments = []


    for option in sys.argv[1:]:
        if option.find('-', 0) == 0:
            optionlist.append(option)
        else:
            arguments.append(option)
    """
    if len(arguments) != 2:
        print("Wrong number of arguments given to boilerplate.py.")
        usage()
        sys.exit(0)
    """
    callback_function(arguments, optionlist)

"""
general_rule | material&rule_for_material*materials*values*x y | values
general rule&extra rule type*materials*values*x y | materials for general rule
"""
