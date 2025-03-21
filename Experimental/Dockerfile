FROM ubuntu:latest

RUN apt update
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN apt install git -y

RUN git clone https://github.com/3LayerPerceptron/FamilyTreeMatcher_ER.git


WORKDIR FamilyTreeMatcher_ER/Experimental

RUN python3 -m pip install -r requirements.txt --break-system-packages

ENTRYPOINT ["python3", "FTM_ER.py"]
