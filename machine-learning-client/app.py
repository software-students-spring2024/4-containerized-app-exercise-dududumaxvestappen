import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import base64
import numpy as np
from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from flask_cors import CORS
import os
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

'''try:
    uri = "mongodb://mongodb:27017/"
    client = MongoClient(uri)
    db = client["gestures"]
    gestureDB = db["emoji"]
    print("Connected!")

except Exception as e:
    print(e)'''

try:
    mongo_client = MongoClient('mongodb+srv://bcdy:BPoOlpuLgv3WKJ62@coffeeshops.5kr79yv.mongodb.net/')
    db = mongo_client['gestures']
    gestureDB = db['emoji']
    print("CONNECTED!!!")
except:
    print("ERROR CONNECTING TO MONGODB")

#base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
base_options = python.BaseOptions(model_asset_path='machine-learning-client/gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options)
recognizer = vision.GestureRecognizer.create_from_options(options)


def emoji(hand):
    if hand == 'Closed_Fist':
        return "\u270A"
        #print("\u270A")  
    elif hand == 'Open_Palm':
        return "\u270B"
        #print("\u270B")  
    elif hand == 'Pointing_Up':
        return "\U0001F446"
        #print("\U0001F446")  
    elif hand == 'Thumb_Down':
        return "\U0001F44E"
        #print("\U0001F44E")  
    elif hand == 'Thumb_Up':
        return "\U0001F44D"
        #print("\U0001F44D")  
    elif hand == 'Victory':
        return "\u270C"
        #print("\u270C")  
    elif hand == 'ILoveYou':
        return "\U0001F91F"
        #print("\U0001F91F")
    # if no gesture detected then return question mark emoji
    else:
        return "\U00002753"


@app.route('/process_img', methods=['POST'])
def process_img(): 
    data = request.json.get('image')
    if not data:
        print('No image data provided')
        #return abort(400, 'No image data provided')
    
    try:
        # Attempt to split and decode the image
        parts = data.split(",", 1)
        #parts = data.split(",")[1]
        if len(parts) != 2:
            print("Invalid image data format")
            #return jsonify({'error': 'Invalid image data format'}), 400
        
        header, encoded = parts
        #data.split(",")[1]
        img_data = base64.b64decode(encoded)
        img_path = 'captured.jpeg'
        with open(img_path, 'wb') as file:
            file.write(img_data)
        # for testing
        print("Image saved!!!!")
        
        try:
            image = mp.Image.create_from_file(img_path)
            recognition_result = recognizer.recognize(image)
            # top_gesture gives: Category(index=-1, score=0.7499747276306152, display_name='', category_name='Open_Palm')
            top_gesture = recognition_result.gestures[0][0]  # Assuming only one gesture is recognized
            ges_name = top_gesture.category_name    # gives the name, ex: Open_Palm
            ges_emoji = emoji(ges_name)     # get emoji unicode
            print("GOT GESTUREEEEE: " + ges_name + ges_emoji)     # this is giving the enture category
            
            gesturetolandmark = {
                                 "timestamp": datetime.now(),
                                 "result": { "top_gesture": ges_name, "emoji": ges_emoji }
                                 }
            print("saved to dict")
            gestureDB.insert_one(gesturetolandmark)
            # for testing
            print("saved to db")
            
            #return jsonify(gesturetolandmark), 200
            return "FINISH PROCESS!!"      # or return None

        except Exception as e:
            print(e)
            return jsonify({"error": "Error processing the image"}), 500
        
        
        #return gesture(img_path)
    
    except Exception as e:
        print("ERRORRRRR")
        return jsonify({'error': 'Error processing the image'}), 500
        
    

@app.route('/test', methods=['GET', 'POST'])
def test_route():
    return 'Test route is working', 200



'''
def gesture(image_path):
    try:
        image = mp.Image.create_from_file(image_path)
        recognition_result = recognizer.recognize(image)
        top_gesture = recognition_result.gestures[0][0]  # Assuming only one gesture is recognized
        ges_emoji = emoji(top_gesture)
        
        gesturetolandmark = {"result": {"top_gesture": top_gesture, "emoji": ges_emoji}}
        gestureDB.insert_one(gesturetolandmark)
        # for testing
        print(top_gesture)
        return jsonify(gesturetolandmark), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error processing the image"}), 500
'''
    
"""
    image = mp.Image.create_from_file(image_path)
    recognition_result = recognizer.recognize(image)

    # Process the result.
    top_gesture = recognition_result.gestures[0][0] # The top recognized gesture
    hand_landmarks = recognition_result.hand_landmarks # Detected hand landmarks
    ges_emoji = emoji(top_gesture)

    # insert the gesture to the database
    gesturetolandmark = { "result": { "top_gesture": top_gesture, "emoji" : ges_emoji }}
    gestureDB.insert_one(gesturetolandmark)
"""

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


if __name__ == '__main__':
    app.run(debug=True, port=5002)