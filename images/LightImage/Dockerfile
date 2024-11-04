FROM kathara/quagga:latest

RUN apt update && apt install -y bc

COPY ./pingingScript-v2.sh /home/pingingScript.sh

RUN chmod +x /home/pingingScript.sh
