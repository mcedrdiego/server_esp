'use strict'
var WebSocketServer = require('websocket').server
var _http = require('http')
const { InfluxDB, Point } = require('@influxdata/influxdb-client')
const { username, password, database, host_url, retentionPolicy } = require('./env.js')
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
	let t = Date.now() - 100 //100 for test purpose ???
	for (var i = 0; i < data.length; i = i + 2) {
		let point = new Point(device)
			.stringField('device', device) //to be replaced by mesure stage(reveil, second)
			.floatField('mesure', (data[i + 1] << 8) + data[i])
			.timestamp(1e6 * (t + i))
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
