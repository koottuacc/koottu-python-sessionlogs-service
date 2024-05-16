from __future__ import print_function
import logging
import time
import grpc

import session_logs_pb2_grpc
import session_logs_pb2


def run():
	# host = 'localhost'
	# server_port = 8009
	channel = grpc.insecure_channel('0.0.0.0:8009')
	stub = session_logs_pb2_grpc.SessionLogsStub(channel)
	user_data = {
		"userid":"5dd77bcac2fc9c3e38a01b5e",
		"deviceId":"12345",
		"usertype":"admin",
		"Device":"Web",
		"sessionStart":int(time.time()),
		# "sessionEnd":1574142090,
		"ipAddress":"127.0.0.1",
		"latitude":62.541354,
		"longitude":32.682145,
		"City":"banglore",
		"Country":"india",
	}
	response = stub.GetSessionLogs(session_logs_pb2.SessionLogsRequest(body_data=str(user_data)))
	print("client received: " + response.message + response.sessionId)

if __name__ == '__main__':
	logging.basicConfig()
	run()

# "sessionEnd":1574142090,