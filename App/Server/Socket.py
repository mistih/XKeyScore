import asyncio
import socket
import hashlib
from datetime import datetime
import json, threading

from App.Database.Connection import Connection

class ServerSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = Connection("localhost", 27017, "mistih")
        self.client_info = {}

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        clientHash = ""
        
        try:
            isClientSentInitialData = False
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                if not isClientSentInitialData:
                    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    clientData = json.loads(data.decode('utf-8'))
                    clientHash = hashlib.sha256(f"{str(clientData)}".encode("utf-8")).hexdigest()
                    print(f"Client {addr} sent hash: {clientHash}")
                    task = asyncio.current_task()
                    self.client_info[task] = clientHash
                    isClient = await self.connection.find_one("connections", {"hash": clientHash})
                    if isClient:
                        print(f"Client {addr} reconnected.")
                        await self.connection.update("connections", {"hash": clientHash}, {"status": "connected","lastCommunication": time, "updatedAt": time})
                    else:
                        print(f"New client connected: {addr}, inserting into database.")
                        await self.connection.insert("connections", {
                            "ip": addr[0],
                            "port": addr[1],
                            "data": clientData, 
                            "hash": clientHash, 
                            "status": "connected",
                            "lastCommunication": time,
                            "updatedAt": time, 
                            "createdAt": time
                        })
                    isClientSentInitialData = True
                    continue
                print(f"Received from {addr}: {data.decode('utf-8')}")
                await self.connection.update("connections", 
                {"hash": clientHash}, {
                    "lastCommunication": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                await self.send_data(writer, "Are you still alive?")
                await writer.drain()

                
        except ConnectionResetError as e:
            print(f"Connection with {addr} was forcibly closed by the client.")
        except Exception as e:
            print(f"An error occurred with client {addr}: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            finally:
                await self.update_client_status(clientHash, "disconnected")
                print(f"Connection with {addr} closed.")

    async def send_data(self, writer, data):
        writer.write(data.encode('utf-8'))
        await writer.drain()
    
    async def checkAliveClients(self):
        while True:
            clients = await self.connection.find("connections", {"status": "connected"})
            for client in clients:
                lastCommunication = datetime.strptime(client["lastCommunication"], "%Y-%m-%d %H:%M:%S")
                if (datetime.now() - lastCommunication).seconds > 10:
                    await self.connection.update("connections", {"hash": client["hash"]}, {"status": "disconnected", "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            await asyncio.sleep(5)
    
    async def checkStillConnected(self):
        while True:
            clients = await self.connection.find("connections", {"status": "connected"})
            for client in clients:
                try:
                    reader, writer = await asyncio.open_connection(client["ip"], client["port"])
                    writer.write("Are you still connected?".encode('utf-8'))
                    await writer.drain()
                    data = await reader.read(1024)
                    print(f"Received from {client['ip']}:{client['port']}: {data.decode('utf-8')}")
                    await self.connection.update("connections", {"hash": client["hash"]}, {"status": "connected", "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                except Exception as e:
                    print(f"An error occurred while checking if client {client['ip']}:{client['port']} is still connected: {e}")
                    await self.connection.update("connections", {"hash": client["hash"]}, {"status": "disconnected", "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            await asyncio.sleep(5)
        

    def on_client_task_done(self, task):
        client_hash = self.client_info.pop(task, None)
        if client_hash:
            asyncio.create_task(self.update_client_status("disconnected", clientHash=client_hash))
        else:
            print("Client hash not found for task.")

    async def update_client_status(self, status, clientHash=None):
        if clientHash:
            await self.connection.update("connections", {"hash": clientHash}, {"status": status})
        else:
            raise Exception("Client hash must be provided to update client status.")

    async def client_connection_handler(self, reader, writer):
        client_task = asyncio.create_task(self.handle_client(reader, writer))
        client_task.add_done_callback(self.on_client_task_done)

    async def run(self):
        server = await asyncio.start_server(self.client_connection_handler, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f"Serving on {addr}")
        async with server:
            await server.serve_forever()