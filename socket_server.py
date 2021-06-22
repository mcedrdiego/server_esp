import asyncio
import websockets

f = open('data.txt', 'w')

async def consumer(data):
	for x in list(data):
		f.write(str(x))
		f.write(',  \n')

async def consumer_handler(websocket, path):
	message = await websocket.recv()
	await consumer(message)

async def handler(websocket, path):
	#data = await websocket.recv()	
	#print(f"<<< {list(data)}")
	consumer_task = asyncio.ensure_future(
		consumer_handler(websocket, path))
	
	done, pending = await asyncio.wait(
		[consumer_task], 
		return_when=asyncio.FIRST_COMPLETED,
	)
	
	for task in pending:
		task.cancel()

async def main():
	async with websockets.serve(handler, "172.31.0.160", 8080):
		await asyncio.Future()  # run forever
		
asyncio.run(main()) 
