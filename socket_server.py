import sys
import asyncio
import websockets

class Server(object):
	def __init__(self, host, port):
		self.host, self.port = host, port
		self.loop = asyncio.get_event_loop()
		
		self.stop = self.loop.create_future()
		
		self.loop.run_until_complete(self.server())
	
	async def server(self):
		async with websockets.serve(self.ws_handler, self.host, self.port):
			await self.stop
	
	async def ws_handler(self, websocket, path):
		msg = await websocket.recv()
		for byte in msg:
			sys.stdout.write(byte)
		sys.stdout.flush()
		sys.stderr.flush()
		
		#await websocket.send(msg)
		#print(f'> {msg}')
		
if __name__ == '__main__':
	server = Server(host='172.31.0.160', port=8080)

