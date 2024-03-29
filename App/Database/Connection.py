import motor

class Connection:
    def __init__(self, host, port, db_name):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = motor.motor_tornado.MotorClient(self.host, self.port)
        self.db = self.client[self.db_name]

    async def insert(self, collection, document):
        result = await self.db[collection].insert_one(document)
        return result

    async def find_all(self, collection, query):
        result = self.db[collection].find(query)
        return result

    async def find_one(self, collection, query):
        result = await self.db[collection].find_one(query)
        return result

    async def update(self, collection, query, new_values):
        result = await self.db[collection].update_one(query, {"$set": new_values})
        return result

    async def delete(self, collection, query):
        result = await self.db[collection].delete_one(query)
        return result