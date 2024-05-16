from concurrent import futures
import logging
import grpc
import session_logs_pb2_grpc
import session_logs_pb2
import time
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import ast
import os

mongo_url = os.getenv("MONGO_URL")
db_name = os.getenv("DATABASENAME")
port = os.getenv("GRPC_PORT")

client = MongoClient(mongo_url)
db = client[db_name]

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class SessionLogs(session_logs_pb2_grpc.SessionLogsServicer):
    def GetSessionLogs(self, request, context):
        try:
            print("try")
            print(request.body_data," Request Data")
            data_data = ast.literal_eval(request.body_data)  # data['data'] in string
            if "userId" not in data_data and data_data["userid"] == "":
                response = "UserId Should be Non-Empty....!!!!"
                return session_logs_pb2.SessionLogsResponse(message=response)
            if "deviceId" not in data_data and data_data['deviceId'] == "":
                response = "deviceId Should be Non-Empty....!!!!"
                return session_logs_pb2.SessionLogsResponse(message=response)
            user_logs = db.sessionLogs.find_one({"userid":data_data['userid'],"deviceId":data_data['deviceId'],"status":1})
            if user_logs:
                print("User Not Found for Device Active Session so enter New Session")
                if 'sessionEnd' in data_data:
                    db.sessionLogs.update({"_id":ObjectId(str(user_logs['_id']))},{"$set":{
                        "status":2,"statusMsg":"inactive","sessionEnd":int(time.time())}})
                    print("session end")
                    return session_logs_pb2.SessionLogsResponse(message="session is ended succesfully",sessionId=str(user_logs['_id']))
                else:
                    db.sessionLogs.update({"_id": ObjectId(str(user_logs['_id']))},{
                        "$set": {"status": 2,"statusMsg":"inactive","sessionEnd": int(time.time())}})
                    starttime = datetime.datetime.fromtimestamp(int(data_data['sessionStart']))
                    user_data = {
                        "userid": data_data["userid"],
                        "usertype": data_data["usertype"] if 'usertype' in data_data else "",
                        "device": data_data["Device"] if 'Device' in data_data else "",
                        "sessionStart": data_data['sessionStart'],
                        "sessionEnd": int((datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp()),
                        "deviceId": data_data['deviceId'] if 'deviceId' in data_data else "",
                        "ipAddress": data_data["ipAddress"] if 'ipAddress' in data_data else "",
                        "latitude": data_data["latitude"] if 'latitude' in data_data else 0,
                        "longitude": data_data["longitude"] if 'longitude' in data_data else 0,
                        "city": data_data["City"] if 'City' in data_data else "",
                        "status": 1,
                        "statusMsg": "active",
                        "country": data_data["Country"] if 'Country' in data_data else "",
                        "make": data_data['Make'] if 'Make' in data_data else "",
                        "osVersion": data_data['OSVersion'] if 'OSVersion' in data_data else "",
                        "appVersion": data_data['appVersion'] if 'appVersion' in data_data else "",
                        "deviceModel": data_data['deviceModel'] if 'deviceModel' in data_data else "",
                    }
                    print(data_data,"another session")
                    inserted_id = db.sessionLogs.insert_one(user_data)
                    print(str(inserted_id.inserted_id))
                    return session_logs_pb2.SessionLogsResponse(message="session added successfully",
                                                                sessionId=str(inserted_id.inserted_id))
            else:
                print("User Not Found for Device Active Session so enter New Session")
                starttime = datetime.datetime.fromtimestamp(int(data_data['sessionStart']))
                user_data = {
                    "userid": data_data["userid"],
                    "usertype": data_data["usertype"] if 'usertype' in data_data else "",
                    "device": data_data["Device"] if 'Device' in data_data else "",
                    "sessionStart": data_data['sessionStart'],
                    "sessionEnd": int((datetime.datetime.now() + datetime.timedelta(minutes=30)).timestamp()),
                    "deviceId": data_data['deviceId'] if 'deviceId' in data_data else "",
                    "ipAddress": data_data["ipAddress"] if 'ipAddress' in data_data else "",
                    "latitude": data_data["latitude"] if 'latitude' in data_data else 0,
                    "longitude": data_data["longitude"] if 'longitude' in data_data else 0,
                    "city": data_data["City"] if 'City' in data_data else "",
                    "status": 1,
                    "statusMsg": "active",
                    "country": data_data["Country"] if 'Country' in data_data else "",
                    "make": data_data['Make'] if 'Make' in data_data else "",
                    "osVersion": data_data['OSVersion'] if 'OSVersion' in data_data else "",
                    "appVersion": data_data['appVersion'] if 'appVersion' in data_data else "",
                    "deviceModel": data_data['deviceModel'] if 'deviceModel' in data_data else "",
                }
                print(data_data, "new session")
                inserted_id = db.sessionLogs.insert_one(user_data)
                print(str(inserted_id.inserted_id))
                return session_logs_pb2.SessionLogsResponse(message="session added successfully",sessionId=str(inserted_id.inserted_id))
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            return session_logs_pb2.SessionLogsResponse(message=message)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    session_logs_pb2_grpc.add_SessionLogsServicer_to_server(SessionLogs(), server)
    server.add_insecure_port('[::]:'+str(port))
    server.start()
    print("Grpc Server Start on port",str(port))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig()
    serve()