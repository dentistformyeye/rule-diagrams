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
scale=25 #Minimum value to ensure all final widths/heights are >1.0
cm=37 #Half should be > the default height of an svgwrite text char
hu=0.5*cm #Half unit. Should be 0.5*cm
keyH=0.7*hu #Size of blocks for the key. Should be < hu
fillOpacity=0.66 #Fill opacity for overlapping blocks. Should be >0 and <1
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

def keyRow(d,keyY,material,comment="",mult=1,x=0,opacity=1.0):
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
    keyRow(d,keyY,material,mComment)
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
    d.add(d.text(name,insert=(x,y+height+3*hu)))
    arrow(d,x+width+1*hu,y,x+width+1*hu,y+height)
    arrow(d,x+width+1*hu,y+height,x+width+1*hu,y)
    descTextH=f"height >= {valueH}µm"
    if "exact" in rule:
        descTextH+=f", height <= {valueH}µm"
    d.add(d.text(descTextH,insert=(x+width+2*hu,y+1*hu)))
    keyY=y+height+4*hu
    keyRow(d,keyY,materials,mComment)
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
    if "#" in first or "&" in first:
        first,mExtraRule1,mComment1=parseM(first)
    if "#" in second or "&" in second:
        second,mExtraRule2,mComment2=parseM(second)
    width,height,first,second,x2,y2=drawSpacing(d,first,second,value,x1,y1,orientation,width,height)
    if orientation=="v":
        arrow(d,x1+width,y1+height,x2+width,y2)
        arrow(d,x2+width,y2,x1+width,y1+height)
    else:
        arrow(d,x1+width,y1+height,x2,y2+height)
        arrow(d,x2,y2+height,x1+width,y1+height)
    descText=f"space >= {value}µm"
    d.add(d.text(descText,insert=(x1+width+mu,y1+height+mu+1*hu)))
    d.add(d.text(name,insert=(x1+width+mu,y1+mu+height+mu+2*hu)))
    keyY=y2+height+(1 if orientation=="v" else 3)*hu
    keyY=keyRow(d,keyY,first,mComment1)
    if first != second:
        keyRow(d,keyY,second,mComment2)
    d.save()
    tree=etree.parse(fn)
    svgTag=tree.getroot()
    w=max(x2+width,x1+width+textW(descText),keyH+mu+textW(first),keyH+mu+textW(second))
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
    d.add(d.text(name,insert=(x1+widthS+mu,y1+heightS+2*hu+mu)))
    keyY=y+height+2*hu
    keyY=keyRow(d,keyY,main,mCommentM,2)
    if extension != main:
        keyRow(d,keyY,extension,mCommentE)
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
    d.add(d.text(name,insert=((x+width+mu,height/2+1*hu))))
    keyY=y+height+1*hu
    keyRow(d,keyY,materials)
    d.save()
    tree=etree.parse(fn)
    svgTag=tree.getroot()
    w=max(x+width+mu+textW(descText),keyH+mu+textW(materials))
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
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            x=0
            y=0
            area=float(value)
            width=sqrt(area)*0.25*scale*cm
            height=width*1.5
            d.add(d.rect(insert=(x,y),size=(width,height),class_=materials))
            
            
        elif "hole" in rule:
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            xOut=0
            yOut=0
            xIn=sqrt(value)*0.2*scale*cm
            yIn=xIn
            widthIn=sqrt(value)*0.4*scale*cm
            heightIn=widthIn
            widthOut=widthIn*2
            heightOut=widthOut
            d.add(d.rect(insert=(xOut,yOut),size=(widthOut,heightOut),class_=materials))
            d.add(d.rect(insert=(xIn,yIn),size=(widthIn,heightIn),class_="background"))
            arrow(d,xOut+widthOut+1*hu,yOut+1*hu,(xIn+widthIn)/2,(yIn+heightIn)/2)
            descText=f"area >= {value}µm2"
            d.add(d.text(descText,insert=(xOut+widthOut+1*hu+mu,yOut+1*hu)))
            d.add(d.text(name,insert=(xOut+widthOut+1*hu+mu,yOut+2*hu)))
            keyY=yOut+heightOut+1*hu
            keyRow(d,keyY,materials)
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=max(xOut+widthOut+1*hu+mu+textW(descText),keyH+mu+textW(materials))
            h=keyY+mu
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)
            
    elif "enclosure" in rule:
        if " " in rule and rules.split(" ")[1]=="a":
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            inner,outer=materials.split(" ")
            valueA=lines[lineNum+int(rules.split(" ")[2])][5]
            nameA=lines[lineNum+int(rules.split(" ")[2])][0]
            xOut=0
            yOut=0
            xIn=xOut+float(value)*scale*cm
            yIn=yOut+float(valueA)*scale*cm
            widthIn=float(value)*scale*2*cm
            heightIn=widthIn
            widthOut=widthIn*2
            heightOut=float(valueA)*scale*2*cm+heightIn
            d.add(d.rect(insert=(xOut,yOut),size=(widthOut,heightOut),class_=outer))
            d.add(d.rect(insert=(xIn,yIn),size=(widthIn,heightIn),class_=inner))
            dashedLine(d,xOut,yIn+heightIn,xOut,yOut+heightOut)
            dashedLine(d,xIn,yIn+heightIn,xIn,yOut+heightOut)
            arrow(d,xOut,yOut+heightOut+mu,xIn,yOut+heightOut+mu)
            arrow(d,xIn,yOut+heightOut+mu,xOut,yOut+heightOut+mu)
            descText=f"space >= {value}µm"
            d.add(d.text(descText,insert=(xOut,yOut+heightOut+1*hu+mu)))
            d.add(d.text(name,insert=(xOut,yOut+heightOut+2*hu+mu))) #Horizontal margin complete
            dashedLine(d,xIn+widthIn,yOut,xOut+widthOut,yOut)
            dashedLine(d,xIn+widthIn,yIn,xOut+widthOut,yIn)
            arrow(d,xOut+widthOut+mu,yOut,xOut+widthOut+mu,yIn)
            arrow(d,xOut+widthOut+mu,yIn,xOut+widthOut+mu,yOut)
            descTextA=f"space >= {valueA}µm"
            d.add(d.text(descTextA,insert=(xOut+widthOut+1*hu+mu,yOut+1*hu)))
            nameTextA=f"{nameA}"
            d.add(d.text(nameTextA,insert=(xOut+widthOut+1*hu+mu,yOut+2*hu))) #Vertical margin complete
            keyY=yOut+heightOut+3*hu+mu
            keyY=keyRow(d,keyY,outer)
            if inner != outer:
                keyRow(d,keyY,inner)
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=max(xOut+widthOut+1*hu+mu+textW(descTextA),keyH+mu+textW(outer),keyH+mu+textW(inner))
            h=keyY+mu
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)
            
    elif "noOverlap" in rule:
        if " " not in rule or "innerCorner" in rule:
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            top,bottom=materials.split(" ")
            widthT=0.100*scale*cm
            heightT=widthT*3
            widthB=heightT
            heightB=widthT
            xB=0
            yB=heightT/3
            xT=widthB/3
            yT=0
            d.add(d.rect(insert=(xB,yB),size=(widthB/2,heightB),class_=bottom))
            classB=bottom
            if "innerCorner" in rule:
                classB="background"
            d.add(d.rect(insert=(xB+widthB/2,yB),size=(widthB/2,heightB),class_=classB))
            d.add(d.rect(insert=(xB,yB+heightB/2),size=(widthB,heightB/2),class_=bottom))
            if "rectOnly" not in top:
                print()
            d.add(d.rect(insert=(xT,yT),size=(widthT,heightT),class_=top,style=f"fill-opacity:{fillOpacity};"))
            d.add(d.text(no,insert=(xB,heightT+3*hu),class_="no"))
            descText=f"{top} cannot overlap {bottom}"
            d.add(d.text(descText,insert=(xB,heightT+4*hu)))
            d.add(d.text(name,insert=(xB,heightT+5*hu)))
            keyY=yT+heightT+6*hu
            keyY=keyRow(d,keyY,top,"",fillOpacity)
            if bottom != top:
                keyRow(d,keyY,bottom)
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=max(widthB,textW(descText),keyH+mu+textW(top),keyH+mu+textW(bottom))
            h=keyY+mu
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)

def drawComplex(rulesList):
    d=svgwrite.Drawing(filename=fn)
    d.defs.add(d.style(classes))
    materialsList=[]
    for ruleFormatted in rulesList:
        ruleI,materialsI,valuesI,displacementI,full=ruleFormatted.split("*")
        if ruleI=="rectangle":
            if materialsI not in materialsList:
                materialsList+=materialsI
            valueIList=valuesI.split(" ")
            displacementIList=displacementI.split(" ")
            x=0
            y=0
            width=0.100
            height=0.100
            if len(valueIList)>=4:
                x,y,width,height=float(valueIList[0]),float(valueIList[1]),float(valueIList[2]),float(valueIList[3])
            elif len(displacementIList)>=2 and len(valueIList)>=2:
                x,y,width,height=float(displacementIList[0]),float(displacementList[1]),float(valueIList[0]),float(valueIList[1])
            drawRect(d,materialsI,x,y,width,height)
        elif ruleI=="spacing":
            if full:
                for material in materialsList:
                    if material not in materialsList:
                        materialsList+=materail
                #drawSpacingF(x,y,"h",materialsI,width,height)
                return

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
                    else:
                        ruleFormatted=f"{rule}*{materials}*{value}*0 0*"
                        rulesList=[ruleFormatted]
                        rulesList.extend(extraRule.split("&"))
                        drawComplex(rulesList)
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
