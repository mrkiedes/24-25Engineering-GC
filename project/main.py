import asyncio
import websockets
import ssl
import json
import os
from aiohttp import web

# SSL/TLS configuration
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")  # Replace with your paths

# Authentication token
AUTH_TOKEN = "secure_token_1234"  # Replace with your token

# WebSocket handler
async def handler(websocket, path):
    # Step 1: Authenticate Client
    try:
        token = await websocket.recv()
        if token != AUTH_TOKEN:
            await websocket.send(json.dumps({"status": "error", "message": "Invalid token"}))
            await websocket.close()
            return
        await websocket.send(json.dumps({"status": "ok", "message": "Authenticated"}))
        print(f"Client authenticated: {websocket.remote_address}")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    # Step 2: Handle Incoming Data
    try:
        async for message in websocket:
            data = json.loads(message)  # Parse incoming JSON data
            print(f"Received data from {websocket.remote_address}: {data}")

            # Example: Process GPS data
            if "gps" in data:
                gps = data["gps"]
                print(f"GPS Data - Latitude: {gps['lat']}, Longitude: {gps['lon']}")

            # Respond to the client
            response = {"status": "ok", "message": "Data received"}
            await websocket.send(json.dumps(response))

    except websockets.ConnectionClosed as e:
        print(f"Connection closed: {websocket.remote_address}, Reason: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Create a minimal HTTP server
async def http_handler(request):
    return web.Response(text="WebSocket server is running!")

async def start_servers():
    # Dynamically get the assigned port
    PORT = int(os.environ.get("PORT", 8080))
    # Start WebSocket server
    websocket_server = websockets.serve(handler, "0.0.0.0", PORT, ssl=ssl_context)
    # Start HTTP server
    app = web.Application()
    app.router.add_get("/", http_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    http_server = web.TCPSite(runner, "0.0.0.0", PORT)
    # Run both servers concurrently
    await asyncio.gather(websocket_server, http_server.start())
    print(f"Servers running at https://{os.environ.get('REPLIT_URL')}:{PORT}")

# Run both servers
asyncio.run(start_servers())