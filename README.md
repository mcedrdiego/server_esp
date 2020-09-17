# Node-Websocket Server for ESP32

## Introduction
> Npm package to run on server-side, it will receive binary data from ESP32 and writes them on InfluxDB to be later visualized on Grafana.

## Installation
> Clone project ...

## Dependecies 
- Nodemon
- @influxdata/influxdb-client

## Useful commands
```shell
	forever start /server_esp/index.js
	forever restart /server_esp/index.js
	forever stop /server_esp/index.js
``
> also uses nodemon
