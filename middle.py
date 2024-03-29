import asyncio, json

async def main():
    client_ip = "127.0.0.1"
    client_port = 64055
    
    # İstemciye bağlan
    reader, writer = await asyncio.open_connection(client_ip, client_port)
    print(f"Connected to {client_ip}:{client_port}")
    
    # Yetkilendirme anahtarı gönder
    writer.write("zfNw62bzhk1ak2yjRxQCCSEKNvJ0L6KigeeUs5cdJvSTFiAyA6ml6M3AYxioqE6EiI79kOCf0L4kIUdGLhUvkRnwlAqlrthG4QuM1cX6FduMYWp5dsjKE7CtvlUepENe".encode('utf-8'))
    await writer.drain()
    
    # Yetkilendirme sonucunu al
    auth_response = await reader.read(100)
    print(f"Received from client: {auth_response.decode('utf-8')}")
    
    # Yetkilendirme başarılıysa iletişime devam et
    if auth_response.decode('utf-8') == "AuthKey?Authorized":
        data = {
            "type": "stop",
            "command": "dir"
        }
        writer.write(json.dumps(data).encode('utf-8'))
        await writer.drain()
        
        # İstemciden gelecek yanıtı bekleyin (isteğe bağlı)
        response = await reader.read(100)
        print(f"Received from client: {response.decode('utf-8')}")
    else:
        print("Authorization failed. Closing connection.")
    
    # İletişimi sonlandır
    writer.close()
    await writer.wait_closed()

asyncio.run(main())