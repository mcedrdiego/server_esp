'use strict'
const {InfluxDB, Point} = require('@influxdata/influxdb-client')
const {username, password, database,host_url, retentionPolicy} = require('./env.js')
const bucket = `${database}/${retentionPolicy}`
const DB = new InfluxDB({
	url:host_url, 
    token:`${username}:${password}`
}) 

const writeAPI = DB.getWriteApi('', bucket)

function sendDataToInfDB(device){
	console.log('Sending to DB')
	let points=[]
	//let t = process.hrtime() //replace this by constant time between points
	let t = Date.now()-100 //100 for test purpose
	for(var i=0; i<100; i++){
		//let timestap=Date.now()
		let point = new Point('dummy')
            .tag('device', device)
			.floatField('field_1', Math.random()*100)
			.timestamp(1e6*(t+i))
		//	.timestamp(process.hrtime(t)[1]+(1e6*(Date.now()-(30*1000))))
		points.push(point)
	}
//	console.log(points)
	writeAPI.writePoints(points)
		writeAPI
			.close()
			.then(
                console.log("Points written successfully")
            )
			.catch(err=>{
				console.error(err)
			})

}

sendDataToInfDB("NodeJs")

