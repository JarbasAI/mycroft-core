import face_recognition
import os
import urllib
from os.path import dirname
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from mycroft.util.jarbas_services import FaceRecognitionService

__author__ = 'jarbas'


class FaceRecService(MycroftSkill):

    def __init__(self):
        super(FaceRecService, self).__init__(name="FaceRecogSkill")
        self.reload_skill = False
        self.known_faces = {}
        # load known faces
        faces = os.listdir(os.path.dirname(__file__) + "/known faces")
        # Load the jpg files into numpy arrays
        for face in faces:
            # Get the face encodings for each face in each image file
            # Since there could be more than one face in each image, it returns a list of encordings.
            # But since i assume each image only has one face, I only care about the first encoding in each image, so I grab index 0.
            self.log.info("loading face encodings for " + face)
            self.known_faces[face] = face_recognition.face_encodings(face_recognition.load_image_file(os.path.dirname(__file__) + "/known faces/" + face))[0]

    def initialize(self):
        self.emitter.on("face.recognition.request", self.handle_recog)
        # TODO test face recog intent

    def handle_recog(self, message):
        if message.context is not None:
            self.context.update(message.context)
        face = message.data.get("file")
        if face is None:
            self.log.error("no file!")
            face = "missing file"
        user_id = message.context.get("source", "all")
        self.log.info(user_id + " request facerecog for " + face)

        if user_id == "unknown":
            user_id = "all"

        if user_id == "all":
            self.log.warning("no user/destinatary specified")

        result = "unknown person"
        # read unknown image
        self.log.info("loading unknown image")
        try:
            unknown_image = face_recognition.load_image_file(face)
        except:
            self.log.error("loading file failed")
        self.log.info("getting face encodings of unknown image")
        try:
            encoding = face_recognition.face_encodings(unknown_image)[0]
            for person in self.known_faces.keys():
                self.log.info("comparing to person " + person)
                # check if unknown person is this face, by comparing face encodings
                match = face_recognition.compare_faces([self.known_faces[person]], encoding)
                # match is an array of True/False telling if the unknown face matched anyone in the known_faces array
                if match[0]:
                    result = person.replace(".jpg", "")
                    self.log.info("match found, unknown image is " + result)
                    break
        except:
            self.log.error("no face detected in provided image")

        self.context["destinatary"] = user_id
        self.emitter.emit(Message("face.recognition.result",
                                  {"result": result}, self.context))
        if ":" in user_id:
            if user_id.split(":")[1].isdigit():
                self.emitter.emit(Message("message_request",
                                          {"context": self.context, "data": {"result": result}, "type": "face.recognition.result"}, self.context))


    def stop(self):
        pass


def create_skill():
    return FaceRecService()
