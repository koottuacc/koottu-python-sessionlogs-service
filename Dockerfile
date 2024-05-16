FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /SessionLogs
WORKDIR /SessionLogs
ADD . /SessionLogs/
RUN pip3.6 install --upgrade virtualenv
RUN virtualenv -p python3.6 enve
RUN . /SessionLogs/enve/bin/activate
RUN pip3.6 install -r requirement.txt
CMD ["python", "sessionlogs_server.py"]
