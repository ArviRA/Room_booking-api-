from flask import Flask,request,jsonify,url_for,redirect
from werkzeug.utils import secure_filename
import requests
#from flask_cors import CORS
import os
import json
import pyrebase
from  uuid import uuid4
from datetime import datetime
api='' #add your google api key
 
app = Flask(__name__)

config2 = {
  "apiKey": "", #add your google api key
  "authDomain": "",#add your credentials
  "databaseURL": "",#add your credentials
  "storageBucket": "",#add your credentials
  
}
firebase = pyrebase.initialize_app(config2)  #FOR INITIALIZING FIREBASE

db = firebase.database()   #FOR CONFIGURING THE FIREBASE DB
#db.child("RoomData").child("23-empty").update({'jvg':'htfth'})
storage = firebase.storage()  #FOR CONFUGURING STORAGE
try:
    userData = dict(db.child("Userdata").get().val())
except:
    pass
auth  = firebase.auth()
def check_uname(name):
    #print(userData.keys())
    try:
        userData = dict(db.child("Userdata").get().val())
        keys = list(userData.keys())
        if name in keys:
            return "500"
        else: return "200"    
    except:
        return "200"

@app.route("/login",methods=['POST','GET'])   #LOGIN URL  
def login():
    if request.method=='POST':
        if len(request.args) != 0:
            details = dict(request.args)
        if len(request.form) != 0:
            details = dict(request.form)
        if len(request.data) != 0:
            details = dict(request.data) 
        print(dict(request.args))
        #details = dict(request.args)
        data = dict(db.child('Userdata').get().val())
        password = details['password']
        keys = details.keys()
        flag = 0
        if "email" not in keys:
            flag = 1
            print(flag,"fr")
            if "phoneNo" not in keys:
                return "400,Enter email or phone number"
        elif "password" not in keys:
            return "400,please enter password" 
        if flag == 0:
            email = details["email"]
        elif flag == 1:
            phone = details["phoneNo"]    
        keys = data.keys()
        print(flag)
        for key in keys:
            if flag == 0:
                try:
                    if data[key]['email']  == email and data[key]['password']  == password:
                        return "Login succesfull, your token::"+str(data[key]['token'])
                except:
                    pass        
            if flag == 1:
                try:
                    print("yess")
                    if data[key]['phoneNo']  == phone and data[key]['password']  == password:
                        return "Login succesfull, your token::"+str(data[key]['token'])        
                except:
                    pass            

        #db.child("Userdata").child(details['name']).update(details)
        return 'Login failed ,check the username and password'
    else:
        return 'Wrong method'    

@app.route("/signup_owner",methods=['POST','GET'])  #SIGNUP URL FOR HOUSE OWNERS
def signup_owner():
    if request.method=='POST':
        if len(request.args) != 0:
            details = dict(request.args)
        if len(request.form) != 0:
            details = dict(request.form)
        if len(request.data) != 0:
            details = dict(request.data) 
        print(dict(request.args))
        #details = dict(request.args)
        details['type'] = 'owner'
        keys = details.keys()
        flag = 0
        if "email" not in keys:
            flag = 1
            if "phoneNo" not in keys:
                return "400,Enter email or phone number"
        elif "password" not in keys:
            return "400,please enter password" 
        if flag == 0:    
            details['uname'] = details['email'].replace(".","_")
        if flag == 1:
             details['uname'] = details['phoneNo']  
        if check_uname(details['uname']) == "200":
            temp = details['uname']
            token = uuid4()
            del details['uname']
            details['token'] = str(token)
            db.child("Userdata").child(temp).update(details)
            
            db.child("id").child('owner').child(str(token)).update({str(token):temp})
            
            return 'Your Token is :: '+str(token) 
        else:
            return '400,the account is already available'
    else:
        return 'Wrong method'

@app.route("/signup_rent",methods=['POST','GET'])   #SIGNUP URL FOR RENTERS
def signup_rent():
    if request.method=='POST':
        if len(request.args) != 0:
            details = dict(request.args)
        if len(request.form) != 0:
            details = dict(request.form)
        if len(request.data) != 0:
            details = dict(request.data) 
        print(dict(request.args))
        #details = dict(request.args)
        details['type'] = 'tenet'
        keys = details.keys()
        flag = 0
        if "email" not in keys:
            flag = 1
            if "phoneNo" not in keys:
                return "400,Enter email or phone number"
        elif "password" not in keys:
            return "400,please enter password" 
        if flag == 0:    
            details['uname'] = details['email'].replace(".","_")
        if flag == 1:
             details['uname'] = details['phoneNo']    
        if check_uname(details['uname']) == "200":
            temp = details['uname']
            token = uuid4()
            del details['uname']
            details['token'] = str(token)
            db.child("Userdata").child(temp).update(details)
            
            db.child("id").child('rent').child(str(token)).update({str(token):temp})
            return 'Your Token is :: '+str(token)   
        else:
            return '400,the account is already available'
    else:
        return 'Wrong method'


@app.route("/create",methods=["POST","GET"])    #CREATE URL FOR HOUSE OWNERS
def create():
    if request.method == "POST":
        if len(request.args) != 0:
            details = dict(request.args)
        if len(request.form) != 0:
            details = dict(request.form)
        if len(request.data) != 0:
            details = dict(request.data)    
        keys_de = list(details.keys())
        print("tocreate")
        if "token" not in keys_de:
            return "400,please enter token"

        token = details["token"]
        data = dict(db.child("id").child("owner").get().val())
        keys = list(data.keys())
        print("\n\ndata::",data)
        if token not in keys:
            return "400,You are not authenticated to carry out this task!"
        try:
            room_id = str(uuid4())
            print("\n\ntoken::",token)
            print(keys_de,"fuyfuyf")
            if "room_name" not in keys_de:
                    return "400,Please enter room name"
            if "floor_size" not in keys_de:
                    return "400,Please enter floor size"
            if "no_of_beds" not in keys_de:
                    return "400,Please enter no of beds"
            if "rent" not in keys_de:
                    return "400,Please enter rent"    
            if "availability" not in keys_de:
                    details["availability"] = True
            if "booked" not in keys_de:
                    details["booked"] = False
            print("roomm")
            #except:
                #return "Something went wrong!"
            temp_Data = db.child("RoomData").get().val()
            print(temp_Data)   
            if temp_Data == None:
                print("none baby") 
            else:
                room = dict(temp_Data)
                print(room)
                
                room_check = room.keys()
                print(room_check,"vgbyhnjmk")
                for i in room_check:
                        if room[i]['room_name'] == details['room_name']:
                            return "Room name already Exist!!"
                
            for key in keys_de:
                    if details[key] == "true" or details[key] == "True": 
                        details[key] = True
                    if details[key] == "false" or details[key] == "False": 
                        details[key] = False 

            ffile = request.files['file']
            print(ffile,"file:::") 
            if 1:
                    print("file_name")
                    extention = ffile.filename.split(".")[-1]
                    file_name = str(uuid4()).replace("-","_") +"."+ extention
                    print(file_name)
                    ffile.save(secure_filename(file_name))
                    details["Label"] = file_name  
                    print("::::file_uploading::::") 
                    storage.child(file_name).put(file_name)
                    print("::::file_uploaded::::")
                    os.remove(file_name) 

            db.child("RoomData").child(room_id).update(details)   
            return "Room created successfully!!"
        except:
            return "Something went wrong!"
    else:
        return "Only supports post method"


@app.route('/edit',methods=["POST","GET"])   #EDIT URL FOR HOUSE OWNERS
def edit():
    if request.method == "POST":
        if len(request.args) != 0:
            details = dict(request.args)
        if len(request.form) != 0:
            details = dict(request.form)
        if len(request.data) != 0:
            details = dict(request.data) 

        keys_de = list(details.keys())
        if "token" not in keys_de:
            return "400,please enter token"
        token = details["token"]
        for key in keys_de:
                if details[key] == "true" or details[key] == "True": 
                    details[key] = True
                if details[key] == "false" or details[key] == "False": 
                    details[key] = False 
        data = dict(db.child("id").child("owner").get().val())
        keys = list(data.keys())
        if token not in keys:
            return "400,You are not authenticated to carry out this task!"
        if 'room_name' not in keys_de:
            return "Enter the room name"
        room_name = details['room_name']
        room = dict(db.child("RoomData").get().val())
        room_id = room.keys()
        for i in room_id:
            if room[i]['room_name'] == room_name:
                db.child("RoomData").child(i).update(details)
                return "Updated Sucessfully!!!"
        return "Room doesn't exist!!!"
    else:
        return 'Wrong method'

@app.route('/delete',methods=["POST","GET"])   #DELETE URL FOR HOUSE OWNERS
def delete():
    if request.method == "POST":
        if len(request.args) != 0:
            details = dict(request.args)
        if len(request.form) != 0:
            details = dict(request.form)
        if len(request.data) != 0:
            details = dict(request.data) 

        keys_de = list(details.keys())
        if "token" not in keys_de:
            return "400,please enter token"
        token = details["token"]
        data = dict(db.child("id").child("owner").get().val())
        keys = list(data.keys())
        if token not in keys:
            return "400,You are not authenticated to carry out this task!"
        if 'room_name' not in keys_de:
            return "Enter the room name"
        room_name = details['room_name']
        room = dict(db.child("RoomData").get().val())
        room_id = room.keys()
        for i in room_id:
            if room[i]['room_name'] == room_name:
                db.child("RoomData").child(i).remove()
                return "Removed Sucessfully!!!"
        return "Room doesn't exist!!!"
    else:
        return 'Wrong method' 

@app.route('/browse',methods=["GET","POST"])  #BROWSE URL FOR BOTH HOUSE OWNER AND RENTERS
def browse():
    if request.method== "GET":
        if len(request.args) != 0:
            details = dict(request.args)
        if len(request.form) != 0:
            details = dict(request.form)
        if len(request.data) != 0:
            details = dict(request.data) 
        
        #details = dict(request.args)
        
        print(details)
        owner_id  = db.child("id").child("owner").get().val()
        rent_id  = db.child("id").child("rent").get().val()
        owner_id = list(owner_id.keys())
        rent_id = list(rent_id.keys())
        print("id::",owner_id,"rent::",rent_id)
        
        if "token" not in list(details.keys()):
            return "400!!!,please enter token"
        
        if details['token'] in owner_id or details['token'] in rent_id:
            temp_Data = db.child("RoomData").get().val()
            if temp_Data == None:
                return "No Rooms are available:::"
            room_details=dict(temp_Data)
            room_num = room_details.keys()
            print(list(room_num))
            room_list = []
            
            for i in list(room_num):
                if room_details[i]["booked"] == True:
                    booked_date = datetime.strptime(room_details[i]["book_date"], '%Y-%m-%d').date()
                    booked_days = int(room_details[i]["no_of_days"])
                    curr_date = datetime.now().date()
                    if str(curr_date - booked_date) == "0:00:00":
                        diff = 0     
                    else:    
                        diff = int(str(curr_date - booked_date).split(" ")[0])
                        print(diff,"difference")
                    if int(booked_days - diff) <= 0:
                        room_details[i]["booked"] = False
                        del room_details[i]["no_of_days"]
                        del room_details[i]["book_date"]
                        db.child("RoomData").child(i).update(room_details[i])            


            for i in list(room_num):
                if room_details[i]['availability'] == True and room_details[i]['booked'] == False:
                    room_list.append(room_details[i]['room_name'])
        
            return "Rooms available:::"+str(room_list)
        else:
            return "400!! Wrong Token"
    else:
        return 'Wrong method'

@app.route('/view',methods=["GET","POST"])   #VIEW URL FOR HOUSE OWNERS AND RENTERS
def view():
    if request.method== "GET":
        if len(request.args) != 0:
            details = dict(request.args)
        if len(request.form) != 0:
            details = dict(request.form)
        if len(request.data) != 0:
            details = dict(request.data) 
        #details = dict(request.args)
        
        print(details)
        owner_id  = db.child("id").child("owner").get().val()
        rent_id  = db.child("id").child("rent").get().val()
        owner_id = list(owner_id.keys())
        rent_id = list(rent_id.keys())
        print("id::",owner_id,"rent::",rent_id)
        
        if "token" not in list(details.keys()):
            return "400!!!,please enter token"
        if "room_name" not in list(details.keys()):
            return "400!!,please enter room name"
        if details['token'] in owner_id or details['token'] in rent_id:
            temp_Data = db.child("RoomData").get().val()
            if temp_Data == None:
                return "No Rooms are available:::"
            room_details=dict(temp_Data)
            room_num = room_details.keys()
            print(list(room_num))
            for i in list(room_num):
                if room_details[i]["booked"] == True:
                    booked_date = datetime.strptime(room_details[i]["book_date"], '%Y-%m-%d').date()
                    booked_days = int(room_details[i]["no_of_days"])
                    curr_date = datetime.now().date()
                    if str(curr_date - booked_date) == "0:00:00":
                        diff = 0     
                    else:    
                        diff = int(str(curr_date - booked_date).split(" ")[0])
                        print(diff,"difference")
                    if int(booked_days - diff) <= 0:
                        room_details[i]["booked"] = False
                        del room_details[i]["no_of_days"]
                        del room_details[i]["book_date"]
                        db.child("RoomData").child(i).update(room_details[i])
            for i in list(room_num):
                if room_details[i]['availability'] == True and room_details[i]['booked'] == False and details["room_name"] == room_details[i]["room_name"]:
                    del room_details[i]["token"]
                    if "Label" in list(room_details[i].keys()):
                        myfile = storage.child(room_details[i]["Label"])
                        url = myfile.get_url(None)
                        room_details[i]["url"] = url
                    return "Rooms Details:::"+ str(room_details[i])
        
            return "room not available"
        else:
            return "400!! Wrong Token"    
    else:
        return 'Wrong method'

@app.route('/book',methods=["GET","POST"])  #BOOK URL FOR RENTERS
def book():
    if request.method== "POST":
        #details = dict(request.args)
        if len(request.args) != 0:
            details = dict(request.args)
        if len(request.form) != 0:
            details = dict(request.form)
        if len(request.data) != 0:
            details = dict(request.data) 
        #print(details)
        owner_id  = db.child("id").child("owner").get().val()
        rent_id  = db.child("id").child("rent").get().val()
        owner_id = list(owner_id.keys())
        rent_id = list(rent_id.keys())
        print("id::",owner_id,"rent::",rent_id)
        
        if "token" not in list(details.keys()):
            return "400!!!,please enter token"
        if "room_name" not in list(details.keys()):
            return "400!!,please enter room name"
        if "no_of_days" not in list(details.keys()):
            return "400!!,please enter number of days"
        if not(int(details['no_of_days']) >=1 and int(details['no_of_days']) <= 30):
            return "Enter a valid number between 1 to 30"
        if details['token'] in owner_id or details['token'] in rent_id:
            temp_Data = db.child("RoomData").get().val()
            if temp_Data == None:
                return "No Rooms are available:::"
            room_details=dict(temp_Data)
            room_num = room_details.keys()
            print(list(room_num))
            for i in list(room_num):
                if room_details[i]["booked"] == True:
                    booked_date = datetime.strptime(room_details[i]["book_date"], '%Y-%m-%d').date()
                    booked_days = int(room_details[i]["no_of_days"])
                    curr_date = datetime.now().date()
                    if str(curr_date - booked_date) == "0:00:00":
                        diff = 0     
                    else:    
                        diff = int(str(curr_date - booked_date).split(" ")[0])
                        print(diff,"difference")
                    if int(booked_days - diff) <= 0:
                        room_details[i]["booked"] = False
                        del room_details[i]["no_of_days"]
                        del room_details[i]["book_date"]
                        db.child("RoomData").child(i).update(room_details[i])

            for i in list(room_num):
                if room_details[i]['availability'] == True and room_details[i]['booked'] == False and details["room_name"] == room_details[i]["room_name"]:
                    room_details[i]['booked'] = True
                    room_details[i]['book_date'] = str(datetime.now().date())
                    room_details[i]['no_of_days'] = int(details['no_of_days'])
                    print(room_details[i])
                    db.child("RoomData").child(i).update(room_details[i])
                    
                    return "Room Booked Succesfully!!!"
        
            return "room not available for booking"
        else:
            return "400!! Wrong Token"   
    else:
        return 'Wrong method'
 
@app.route('/calender',methods=["GET","POST"])   #TO VIEW THE AVAIALABILITY OF ALL THE ROOMS
def calender():
    if request.method== "GET":
        
        #details = dict(request.args)
        if len(request.args) != 0:
            details = dict(request.args)
        if len(request.form) != 0:
            details = dict(request.form)
        if len(request.data) != 0:
            details = dict(request.data) 
        print(details)
        owner_id  = db.child("id").child("owner").get().val()
        rent_id  = db.child("id").child("rent").get().val()
        owner_id = list(owner_id.keys())
        rent_id = list(rent_id.keys())
        print("id::",owner_id,"rent::",rent_id)
        
        if "token" not in list(details.keys()):
            return "400!!!,please enter token"
        
        if details['token'] in owner_id or details['token'] in rent_id:
            temp_Data = db.child("RoomData").get().val()
            if temp_Data == None:
                return "No Rooms are available:::"
            room_details=dict(temp_Data)
            room_num = room_details.keys()
            print(list(room_num))
            room_dict = {}
            diff_list = []
            count = 0
            for i in list(room_num):
                flag = 1
                if room_details[i]["booked"] == True:
                    booked_date = datetime.strptime(room_details[i]["book_date"], '%Y-%m-%d').date()
                    booked_days = int(room_details[i]["no_of_days"])
                    curr_date = datetime.now().date()
                    if str(curr_date - booked_date) == "0:00:00":
                        diff = 0     
                    else:    
                        diff = int(str(curr_date - booked_date).split(" ")[0])
                        print(diff,"difference")
                    if int(booked_days - diff) <= 0:
                        room_details[i]["booked"] = False
                        del room_details[i]["no_of_days"]
                        del room_details[i]["book_date"]
                        db.child("RoomData").child(i).update(room_details[i])            
                    else:
                        flag = 0
                        diff_list.append("Available in "+ str(int(booked_days - diff)) + " days")
                if flag == 1:
                    diff_list.append("Available")        
                count+=1
            print(count,diff_list)    
            count = 0    
            for i in list(room_num):
                print("vre",count)
                if room_details[i]['availability'] == True:
                    room_dict[str(room_details[i]['room_name'])] = diff_list[count]
                count+=1
            return "Rooms available:::"+str(room_dict)
        else:
            return "400!! Wrong Token"
    else:
        return 'Wrong method'

if __name__ =='__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)),debug=True,use_reloader=True)




