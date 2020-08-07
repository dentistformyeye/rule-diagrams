import csv
import svgwrite
from svgwrite import rgb
import math
import os
import sys
from lxml import etree

cm=37
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
    .huge_met1 {fill:rgb(190,144,217);}
    .via {fill:rgb(59,0,246);}
    .checkmark {fill:rgb(0,192,0);font-size:74px;}
    .no {fill:rgb(179,0,0);font-size:74px;}
    
"""

def sqrt(x):
    xF=float(x)
    return math.sqrt(xF) if (xF>=0) else -math.sqrt(-xF)

def arrow(d,x1,y1,x2,y2,s="black",sw=1):
    cos=0.866
    sin=0.5
    dx=sqrt(x2-x1)
    dy=sqrt(y2-y1)
    d.add(d.line((x1,y1),(x2,y2),stroke=s,stroke_width=sw))
    d.add(d.line((x2,y2),(x2-(dx*cos+dy*-sin),y2-(dx*sin+dy*cos)),stroke=s,stroke_width=sw))
    d.add(d.line((x2,y2),(x2-(dx*cos+dy*sin),y2-(dx*-sin+dy*cos)),stroke=s,stroke_width=sw))

folderPath=os.getcwd()
def draw():
    print(f"{name} {ruleType}")
    fn=name[1:-1]+".svg"
    fp=folderPath+fn
    nameText=f"{name}"
    if "width" in ruleType:
        if " " not in ruleType:
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            x1=0
            y1=0
            width=float(value)*25*cm
            height=width*1.5
            d.add(d.rect(insert=(x1,y1),size=(width,height),class_=materials))
            arrow(d,x1,height+0.5*cm,x1+width,height+0.5*cm)
            arrow(d,x1+width,height+0.5*cm,x1,height+0.5*cm)
            descText=f"width >= {value}µm"
            d.add(d.text(descText,insert=(x1,height+1*cm)))
            d.add(d.text(nameText,insert=(x1,height+1.5*cm)))
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=max(width,len(descText)*7.25)
            h=height+1.5*cm+5
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)
            
        elif "exact" in ruleType:
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            x1=0
            y1=0
            width=float(value)*25*cm
            height=width*1.5
            d.add(d.rect(insert=(x1,y1),size=(width,height),class_=materials))
            arrow(d,x1,height+0.5*cm,x1+width,height+0.5*cm)
            arrow(d,x1+width,height+0.5*cm,x1,height+0.5*cm)
            descText=f"width >= {value}µm, width <= {value}µm"
            d.add(d.text(descText,insert=(x1,height+1*cm)))
            d.add(d.text(nameText,insert=(x1,height+1.5*cm)))
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=max(width,len(descText)*7.25)
            h=height+1.5*cm+5
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)
            
    if "size" in ruleType:
        if "exact" in ruleType:
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            valueW,valueH=value.split(" ")
            x1=0
            y1=0
            width=float(valueW)*25*cm
            height=float(valueH)*25*cm
            d.add(d.rect(insert=(x1,y1),size=(width,height),class_=materials))
            arrow(d,x1,height+0.5*cm,x1+width,height+0.5*cm)
            arrow(d,x1+width,height+0.5*cm,x1,height+0.5*cm)
            descTextW=f"width >= {valueW}µm, width <= {valueW}µm"
            d.add(d.text(descTextW,insert=(x1,height+1*cm)))
            d.add(d.text(nameText,insert=(x1,height+1.5*cm)))
            arrow(d,x1+width+0.5*cm,y1,x1+width+0.5*cm,y1+height)
            arrow(d,x1+width+0.5*cm,y1+height,x1+width+0.5*cm,y1)
            descTextH=f"height >= {valueH}µm, height <= {valueH}µm"
            d.add(d.text(descTextH,insert=(x1+width+1*cm,y1+0.5*cm)))
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=x1+width+1*cm+len(descTextH)*7.25
            h=height+1.5*cm+5
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)
            
    elif "spacing" in ruleType:
        if " " not in ruleType:
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            x1=0
            y1=0
            width=float(value)*25*cm
            height=width*1.5
            x2=width*2
            y2=0
            d.add(d.rect(insert=(x1,y1),size=(width,height),class_=materials))
            d.add(d.rect(insert=(x2,y2),size=(width,height),class_=materials))
            arrow(d,x1+width,y1+height,x2,y1+height)
            arrow(d,x2,y1+height,x1+width,y1+height)
            descText=f"space >= {value}µm"
            d.add(d.text(descText,insert=(x1+width,y1+height+0.5*cm)))
            d.add(d.text(nameText,insert=(x1+width,y1+height+1*cm)))
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=max(x2+width,x1+width+len(descText)*7.25)
            h=height+1*cm+5
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)
            
        if "extend" in ruleType:
            if "extend" not in ruleType:
                d=svgwrite.Drawing(filename=fn)
                d.defs.add(d.style(classes))
                x=0
                y=0
                width=3*5*cm #Huge metal1 width is at least 3µm
                height=width
                widthS=float(value)*5*cm
                heightS=widthS*.75
                x1=x+width
                y1=0
                x2=x+width
                y2=y1+heightS+widthS
                d.add(d.rect(insert=(x,y),size=(width,height),class_=materials))
                d.add(d.rect(insert=(x1,y1),size=(widthS,heightS),class_=materials))
                d.add(d.rect(insert=(x2,y2),size=(widthS,heightS),class_=materials))
                arrow(d,x1+widthS,y1+heightS,x2+widthS,y2)
                arrow(d,x2+widthS,y2,x1+widthS,y1+heightS)
                descText=f"space >= {value}µm"
                d.add(d.text(descText,insert=(x1+widthS+5,y1+heightS+0.5*cm)))
                d.add(d.text(nameText,insert=(x1+widthS+5,y1+heightS+1*cm)))
                d.save()
                tree=etree.parse(fn)
                svgTag=tree.getroot()
                w=x1+width+5+len(descText)*7.25
                h=height
                svgTag.set("viewBox",f"0 0 {w} {h}")
                tree.write(fn)
            
    elif "area" in ruleType:
        if " " not in ruleType:
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            x=0
            y=0
            area=float(value)
            width=sqrt(area)*12.5*cm
            height=width*1.5
            d.add(d.rect(insert=(x,y),size=(width,height),class_=materials))
            descText=f"area >= {value}µm2"
            d.add(d.text(descText,insert=(x+width+5,height/2)))
            d.add(d.text(nameText,insert=((x+width+5,height/2+0.5*cm))))
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=x+width+5+len(descText)*7.25
            h=height
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)
            
        elif "hole" in ruleType:
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            xOut=0
            yOut=0
            xIn=sqrt(value)*6.25*cm
            yIn=xIn
            widthIn=sqrt(value)*6.25*2*cm
            heightIn=widthIn
            widthOut=widthIn*2
            heightOut=widthOut
            d.add(d.rect(insert=(xOut,yOut),size=(widthOut,heightOut),class_=materials))
            d.add(d.rect(insert=(xIn,yIn),size=(widthIn,heightIn),class_="background"))
            arrow(d,xOut+widthOut+0.5*cm,yOut+0.5*cm,(xIn+widthIn)/2,(yIn+heightIn)/2)
            descText=f"area >= {value}µm2"
            d.add(d.text(descText,insert=(xOut+widthOut+0.5*cm+5,yOut+0.5*cm)))
            d.add(d.text(nameText,insert=(xOut+widthOut+0.5*cm+5,yOut+1*cm)))
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=xOut+widthOut+0.5*cm+5+len(descText)*7.25
            h=heightOut
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)
            
    elif "enclosure" in ruleType:
        if " " in ruleType and ruleType.split(" ")[1]=="a":
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            inner,outer=materials.split(" ")
            valueA=lines[lineNum+int(ruleType.split(" ")[2])][5]
            nameA=lines[lineNum+int(ruleType.split(" ")[2])][0]
            xOut=0
            yOut=0
            xIn=float(value)*50*cm
            yIn=float(valueA)*50*cm
            widthIn=float(value)*50*2*cm
            heightIn=widthIn
            widthOut=widthIn*2
            heightOut=float(valueA)*50*2*cm+heightIn
            d.add(d.rect(insert=(xOut,yOut),size=(widthOut,heightOut),class_=outer))
            d.add(d.rect(insert=(xIn,yIn),size=(widthIn,heightIn),class_=inner))
            #d.add(d.line((xIn,yIn),(xIn+widthIn,yIn+heightIn),stroke="black"))
            #d.add(d.line((xIn,yIn+heightIn),(xIn+widthIn,yIn),stroke="black")) #Contact complete
            d.add(d.line((xOut,yOut+heightOut),(xOut,yOut+heightOut+1*cm),stroke="black"))
            d.add(d.line((xIn,yOut+heightOut),(xIn,yOut+heightOut+1*cm),stroke="black"))
            arrow(d,xOut,yOut+heightOut+0.5*cm,xIn,yOut+heightOut+0.5*cm)
            arrow(d,xIn,yOut+heightOut+0.5*cm,xOut,yOut+heightOut+0.5*cm)
            descText=f"space >= {value}µm"
            d.add(d.text(descText,insert=(xOut,yOut+heightOut+1.5*cm)))
            d.add(d.text(nameText,insert=(xOut,yOut+heightOut+2*cm))) #Enclosure complete
            d.add(d.line((xOut+widthOut,yOut),(xOut+widthOut+1*cm,yOut),stroke="black"))
            d.add(d.line((xOut+widthOut,yIn),(xOut+widthOut+1*cm,yIn),stroke="black"))
            arrow(d,xOut+widthOut+0.5*cm,yOut,xOut+widthOut+0.5*cm,yIn)
            arrow(d,xOut+widthOut+0.5*cm,yIn,xOut+widthOut+0.5*cm,yOut)
            descTextA=f"space >= {valueA}µm"
            d.add(d.text(descTextA,insert=(xOut+widthOut+1*cm,yOut+0.5*cm+5)))
            nameTextA=f"{nameA}"
            d.add(d.text(nameTextA,insert=(xOut+widthOut+1*cm,yOut+1*cm+5))) #Enclosure adjacent complete
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=xOut+widthOut+1*cm+len(descTextA)*7.25
            h=yOut+heightOut+2*cm+5
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)
            
    elif "noOverlap" in ruleType:
        if " " not in ruleType:
            d=svgwrite.Drawing(filename=fn)
            d.defs.add(d.style(classes))
            top,bottom=materials.split(" ")
            widthT=0.100*25*cm
            heightT=widthT*3
            widthB=heightT
            heightB=widthT
            xB=0
            yB=heightT/3
            xT=widthB/3
            yT=0
            d.add(d.rect(insert=(xB,yB),size=(widthB,heightB),class_=bottom,style="fill-opacity:0.8;"))
            d.add(d.rect(insert=(xT,yT),size=(widthT,heightT),class_=top))
            d.add(d.text(no,insert=(xB,heightT+1.5*cm),class_="no"))
            descText=f"{top} cannot overlap {bottom}"
            d.add(d.text(descText,insert=(xB,heightT+2*cm)))
            d.add(d.text(nameText,insert=(xB,heightT+2.5*cm)))
            d.save()
            tree=etree.parse(fn)
            svgTag=tree.getroot()
            w=max(widthB,len(descText)*7.25)
            h=heightT+2.5*cm+5
            svgTag.set("viewBox",f"0 0 {w} {h}")
            tree.write(fn)


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
                    global ruleType
                    global materials
                    global value
                    name=row[0]
                    ruleType=row[1]
                    materials=row[3]
                    value=row[5]
                    draw()
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
    
