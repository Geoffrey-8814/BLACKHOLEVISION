from flask import Flask, send_file, render_template, request, jsonify
import os
import logging
#This program does NOT work. To test other functions, simply dump this piece into the bin and delete relevant code in main.py.
class appp:
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)

# Folder where frames are stored
    FRAME_FOLDER = 'static/frames'
    UPLOAD_FOLDER = 'uploads'
    os.makedirs(FRAME_FOLDER, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Default resolution and frame rate for each camera
    camera_settings = {
        'camera1': {'resolution': (1600, 1200), 'frame_rate': 50},
        'camera2': {'resolution': (640, 480), 'frame_rate': 30}
    }

    layout_settings = "Default"
    marker_size = 666.66
    barvalue = 50   
    exposure = 20
    autoexposure =False
    contrast = 0
    family = 0
    teamNumber = 1001
    x=0
    y=0
    z=0
    roll=0
    pitch=0
    yaw=0


# Function to update resolution for a camera
    def update_resolution(self,camera, new_resolution):
        self.camera_settings[camera]['resolution'] = tuple(map(int, new_resolution.split('x')))
        logging.info(f"Resolution for {camera} updated to {self.camera_settings[camera]['resolution']}")

# Function to update frame rate for a camera
    def update_frame_rate(self,camera, new_frame_rate):
        self.camera_settings[camera]['frame_rate'] = int(new_frame_rate)
        logging.info(f"Frame rate for {camera} updated to {self.camera_settings[camera]['frame_rate']} fps")

# Function to update layout
    def update_layout(self,new_layout):
        self.layout_settings = new_layout
        logging.info(f"Layout updated to {self.layout_settings}")

    def update_marker(self,new_marker):
        self.marker_size = new_marker
        logging.info(f"Marker updated to {self.marker_size}")

    def update_barvalue(self,new_barvalue):
        self.barvalue = new_barvalue
        logging.info(f"Barvalue updated to {self.barvalue}")


    # Route to update resolution
    @app.route('/update-resolution', methods=['POST'])
    def update_resolution_route(self):
        data = request.get_json()
        camera = data.get('camera')
        new_resolution = data.get('resolution')
        if camera and new_resolution:
            self.update_resolution(camera, new_resolution)
            return jsonify(message=f"Resolution for {camera} updated to {new_resolution}"), 200
        else:
            return jsonify(error="Invalid camera or resolution"), 400

# Route to update frame rate
    @app.route('/update-frame-rate', methods=['POST'])
    def update_frame_rate_route(self):
        data = request.get_json()
        camera = data.get('camera')
        new_frame_rate = data.get('frame_rate')
        if camera and new_frame_rate:
            self.update_frame_rate(camera, new_frame_rate)
            return jsonify(message=f"Frame rate for {camera} updated to {new_frame_rate}"), 200
        else:
            return jsonify(error="Invalid camera or frame rate"), 400

# Route to update layout
    @app.route('/update-layout', methods=['POST'])
    def update_layout_route(self):
        data = request.get_json()
        new_layout = data.get('layout')
        if new_layout:
            self.update_layout(new_layout)
            return jsonify(message=f"Layout updated to {new_layout}"), 200
        else:
            return jsonify(error="Invalid layout"), 400
    
# Route to update layout
    @app.route('/update-marker', methods=['POST'])
    def update_marker_route(self):
        data = request.get_json()
        new_marker = data.get('marker')
        if new_marker:
            self.update_marker(new_marker)
            return jsonify(message=f"Marker updated to {new_marker}"), 200
        else:
            return jsonify(error="Invalid marker"), 400
    

# Route to update layout
    @app.route('/update-barvalue', methods=['POST'])
    def update_barvalue_route(self):
        data = request.get_json()
        new_barvalue = data.get('barvalue')
        if new_barvalue:
            self.update_barvalue(new_barvalue)
            return jsonify(message=f"Barvalue updated to {new_barvalue}"), 200
        else:
            return jsonify(error="Invalid bar"), 400

    @app.route('/get-latest-frame-camera1')
    def get_latest_frame_camera1(self):
        latest_frame = self.get_latest_frame('camera1')
        if latest_frame:
            return send_file(latest_frame, mimetype='image/jpeg')
        else:
            return jsonify(error="No frames found for camera1"), 404

    @app.route('/get-latest-frame-camera2')
    def get_latest_frame_camera2(self):
        latest_frame = self.get_latest_frame('camera2')
        if latest_frame:
            return send_file(latest_frame, mimetype='image/jpeg')
        else:
            return jsonify(error="No frames found for camera2"), 404

# Helper function to get the latest frame for a camera
    def get_latest_frame(self,camera):
        frame_files = sorted([f for f in os.listdir(self.FRAME_FOLDER) if f.startswith(camera)], key=lambda x: int(x.split(camera + 'frame')[1].split('.')[0]), reverse=True)
        if frame_files:
            return os.path.join(self.FRAME_FOLDER, frame_files[0])
        return None

# Route for the main index page
    @app.route('/')
    def index(self):
        return render_template('index.html',
                           camera1_resolution='x'.join(map(str, self.camera_settings['camera1']['resolution'])),
                           camera1_frame_rate=self.camera_settings['camera1']['frame_rate'],
                           camera2_resolution='x'.join(map(str, self.camera_settings['camera2']['resolution'])),
                           camera2_frame_rate=self.camera_settings['camera2']['frame_rate'],
                           layout=self.layout_settings,marker = self.marker_size)              
    def runn(self):
        self.app.run(debug=True)
