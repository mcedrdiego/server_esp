'use strict'
var WebSocketServer  = require('websocket').server
var _http= require('http')
const {InfluxDB, Point} = require('@influxdata/influxdb-client')
const {username, password, database,host_url, retentionPolicy} = require('./env.js')
const bucket = `${database}/${retentionPolicy}`
const PORT = 8080
const DB = new InfluxDB({
	url:host_url, 
    	token:`${username}:${password}`
}) 

const writeAPI = DB.getWriteApi('', bucket)

async function sendDataToInfDB(device,data){
	console.log('Sending to DB')
	let points=[]
	let t = process.hrtime() //replace this by constant time between points
	for(var i=0; i<data.length; i++){
		let timestap=Date.now()
		let point = new Point('dummy')
			.tag('device', device)
			.floatField('field_1', data[i])
		//	.timestamp(process.hrtime(t)[1]+(1e6*(Date.now()-(30*1000))))
		points.push(point)
	}
	//console.log(points)
	writeAPI.writePoints(points)
		writeAPI
			.close()
			.then()
			.catch(err=>{
				console.error(err)
			})
}

var Server = _http.createServer((req,res)=>{
    console.log('>>> New request: '+req.url)
    res.writeHead(404)
    res.end()
})

Server.listen(PORT, ()=>{
    console.log('Listenning port: '+PORT)
})

var wsServer = new WebSocketServer({
    httpServer: Server,
    autoAcceptConnections: false
})

var originIsAllowed = (origin)=>{
	console.log(origin)
	return true
}

wsServer.on('request', (request)=>{
    if(!originIsAllowed(request.origin)){
        request.reject()
        console.log(`** Request from ${request.origin} Rejected. **`)
        return
    } 
    var connection = request.accept('arduino', request.origin)
    console.log((new Date()) + ' Connection accepted '+ request.resource)
    connection.on('message', (message)=>{
        if(message.type === 'utf8'){
            console.log(`>>> ${message.utf8Data}`)
        } else if(message.type === 'binary'){
            console.log(`>>> Binary data Size: ${message.binaryData.length} bytes`)
            sendDataToInfDB(request.resource.substring(1), message.binaryData)
	}
    })
    connection.on('close', (reasonCode, description)=>{
        console.log(`** Peer ${connection.remoteAddress} disconnected **`)
    })
})

console.log(' *** DB test *** ')
const queryAPI = DB.getQueryApi('')
const query = `from(bucket: "${bucket}") |> range(start:-30m)`
queryAPI.queryRows(query,{
    next(row, tableMeta){
        const o = tableMeta.toObject(row)
        console.log(`${o._time} ${o._measurement} : ${o.device} -> ${o._field} = ${o._value}`)
    },
    error(err){
        console.error(err)
    },
    complete(){
        console.log(' *** Done query *** ')
    }
})


