import cv2
import os
import json

class recordVideo:
    recordingIds:list=[]
    videoOutput: dict = {}
    def __init__(self, save_dir) ->None:

        # Directory to save the videos
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def writeFrame(self, frames: list, record_ids: list):
        def get_video_filename():
            return self.save_dir + "/" + f"{frame.camera_name}.mp4"
        
        for frame in frames:

            if (frame.camera_id in record_ids) and not(frame.frame is None):

                if not frame.camera_id in self.recordingIds: #First time this ID recorded
                    height,width,_=frame.frame.shape
                    self.videoOutput[str(frame.camera_id)]= cv2.VideoWriter(get_video_filename(), cv2.VideoWriter_fourcc(*'MJPG'), 50.0, (width,height))
                    self.recordingIds.append(frame.camera_id)
                
                self.videoOutput[str(frame.camera_id)].write(frame.frame)
                cv2.imshow("record",frame.frame)
                print(self.videoOutput[str(frame.camera_id)])

            else:

                if frame.camera_id in self.recordingIds:
                    self.videoOutput[str(frame.camera_id)].release()
                    self.videoOutput.pop(str(frame.camera_id))
                    self.recordingIds.remove(frame.camera_id)
