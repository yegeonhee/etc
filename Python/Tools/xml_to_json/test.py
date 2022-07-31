import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageFilter
from PIL.ExifTags import TAGS
import json
import piexif
import shutil

def get_xml(Xml):
    Xml = ET.parse(Xml)
    xmlroot = Xml.getroot()

    return xmlroot


def get_origin(name):
    if name == '11':
        origin = 'coast'
    elif name == '21':
        origin = 'aquafarm'
    elif name == '22':
        origin = 'fising'
    elif name == '31':
        origin = 'foreign'
    else:
        origin = 'none'
    return origin


def makeblur(xmin, xmax, ymin, ymax):
    global Img
    crop_Img = Img.crop((xmin, ymin, xmax, ymax))
    blur_Img = crop_Img.filter(ImageFilter.GaussianBlur(10))
    Img.paste(blur_Img, (xmin, ymin))
    return Img


def make_json(xmlroot):
    global Img, exif
    file = {}

    file['version'] = "4.5.9"
    file['flags'] = {}
    
    object = xmlroot.findall("object")
    
    num_object = len(object)
    file['shapes'] = []
    for n in range(num_object):
        raw_name = object[n].find("name").text
        xmin = int(object[n].find("bndbox").find("xmin").text)
        xmax = int(object[n].find("bndbox").find("xmax").text)
        ymin = int(object[n].find("bndbox").find("ymin").text)
        ymax = int(object[n].find("bndbox").find("ymax").text)
        
        if raw_name == "Blur":
            Img = makeblur(xmin, xmax, ymin, ymax)
            
        else:
            name = raw_name.split(")")[1]
            file['shapes'].append({})
            
            file['shapes'][-1]["label"] = name
            file['shapes'][-1]["points"] = [[xmin, ymin], [xmax, ymax]]
            
            origin = get_origin(raw_name[1:3])
            file['shapes'][-1]["origin"] = origin
            file['shapes'][-1]["group_id"] = None
            file['shapes'][-1]["shape_type"] = "rectangle"
            file['shapes'][-1]["flags"] = {}
    
    file['imagePath'] = image_name
    file['imageData'] = None
    file['imageHeight'] = int(xmlroot.find("size").find('height').text)
    file['imageWidth'] = int(xmlroot.find("size").find('width').text)
    file['date'] = xmlroot.find("date").text
    file['time'] = xmlroot.find("time").text
    file['device'] = xmlroot.find("device").text
    file['camera'] = xmlroot.find("camera").text
    file['shutter'] = float(xmlroot.find("shutter").text)
    file['altitude'] = float(xmlroot.find("altitude").text)
    file['lat'] = float(xmlroot.find("lat").text)
    file['lon'] = float(xmlroot.find("lon").text)
    file['gtype'] = xmlroot.find("gtype").text


    return file
    
def checkerror():
    global error
    if len(xmlroot) - len(xmlroot.findall("object")) != 15:
        print("generate error")
        shutil.move(os.path.join(root, image_name), "I:/json_to_xml/Error/" + image_name)
        shutil.move(os.path.join(root, xml_name), "I:/json_to_xml/Error/" + xml_name)
        error = True

        return error 

    object = xmlroot.findall("object")
    num_object = len(object)

    for n in range(num_object):
        name = object[n].find("name").text
        if name != "Blur":
            try:
                name = name.split(")")[1]
            except:
                print("generate error")
                shutil.move(os.path.join(root, image_name), "I:/json_to_xml/Error/" + image_name)
                shutil.move(os.path.join(root, xml_name), "I:/json_to_xml/Error/" + xml_name)
                error = True
                break
        
    return error

    
foldernum = 100
count = 0

saveroot = "I:/NIA/" + str(foldernum)
os.makedirs(saveroot, exist_ok=True)
for idx, (root, dirs, files) in enumerate(os.walk("piexif_error")):
    Image_list = [Img for Img in files if Img.lower().endswith(".jpg")]
    Xml_list = [Xml for Xml in files if Xml.lower().endswith(".xml")]
    for i in range(len(Image_list)):
        error = False
        if count == 10000:
            foldernum += 1
            saveroot = "I:/NIA/" + str(foldernum)
            os.makedirs(saveroot, exist_ok=True)
            count = 0
        
        image_name = Image_list[i]
        xml_name = Xml_list[i]
        print(image_name)
        
        Img = os.path.join(root, image_name)
        Xml = os.path.join(root, xml_name)
    
        xmlroot = get_xml(Xml)
        error =  checkerror()
        if error:
            continue

        Img = Image.open(Img)
        
        exif = piexif.load(Img.info['exif'])
        
        file = make_json(xmlroot)
        with open(saveroot + "/" + image_name[:-4] + ".json", 'w') as f:
            json.dump(file, f, indent=2)
        # 썸네일 용량이 너무 크면 오류 발생 
        
        del exif['thumbnail']
        exif = piexif.dump(exif)

            
        Img.save(saveroot + "/" + image_name, exif=exif)
    
        count += 1
        
        


        
        

