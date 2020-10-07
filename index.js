'use strict'
var WebSocketServer = require('websocket').server
var _http = require('http')
const { InfluxDB, Point } = require('@influxdata/influxdb-client')
const { username, password, database, host_url, retentionPolicy, Moyenne } = require('./env.js')
const bucket = `${database}/${retentionPolicy}`
const PORT = 8080
const DB = new InfluxDB({
	url: host_url,
	token: `${username}:${password}`
})

function sendDataToInfDB(device, data) {
	console.log('Sending to DB')
	const writeAPI = DB.getWriteApi('', bucket)
	let points = []
	let t = Date.now() * 1e3 //to µs
	let ecart = 0 //ecart entre deux points en (µs)
	/* Check if MCP or ADS from url */
	if (device.slice(device.length - 3, device.length) == "MCP") { 
		ecart = 7.5
		t = t - (225 * 1e3)
	} else { //use else if in future
		ecart = 2325
		t = t - (69768 * 1e3) 
	}

	device = device.substring(0, device.length - 4)  //reconstruct url
	
	for (var i = 0; i < data.length; i = i + (2*Moyenne)) {
		let j = i
		let value = 0
		while(j-i < 2*Moyenne){
			value += (data[j + 1] << 8) + data[j]  //accumulator
			j +=2
		}
		let point = new Point(device)
			.stringField('device', device) //to be replaced by mesure stage(reveil, second)
			.floatField('mesure', value/Moyenne)
			.timestamp(1e3* (t+(i*ecart/(2*Moyenne)))) //timestamp to nanosecs
		points.push(point)
	}
	
	writeAPI.writePoints(points)
	writeAPI
		.close()
		.then(
			console.log("Points successfully written.")
		)
		.catch(err => {
			console.error(err)
		})
}

var Server = _http.createServer((req, res) => {
	console.log('>>> New request: ' + req.url)
	res.writeHead(404)
	res.end()
})

Server.listen(PORT, () => {
	console.log('Listenning port: ' + PORT)
})

var wsServer = new WebSocketServer({
	httpServer: Server,
	autoAcceptConnections: false
})

var originIsAllowed = (origin) => {
	console.log(origin)
	return true
}

wsServer.on('request', (request) => {
	if (!originIsAllowed(request.origin)) {
		request.reject()
		console.log(`** Request from ${request.origin} Rejected. **`)
		return
	}
	var connection = request.accept('arduino', request.origin)
	console.log((new Date()) + ' Connection accepted ' + request.resource)
	connection.on('message', (message) => {
		if (message.type === 'utf8') {
			console.log(`>>> ${message.utf8Data}`)
		} else if (message.type === 'binary') {
			console.log(`>>> Binary data Size: ${message.binaryData.length} bytes`)
			sendDataToInfDB(request.resource.substring(1), message.binaryData)
		}
	})
	connection.on('close', (reasonCode, description) => {
		console.log(`** Peer ${connection.remoteAddress} disconnected **`)
		console.log(`** Reason code: ${reasonCode} : ${description}`)
	})
})
