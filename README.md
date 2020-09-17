# Node-Websocket Server for ESP32

## Introduction
> Npm package to run on server-side, it will receive binary data from ESP32 and writes them on InfluxDB to be later visualized on Grafana.

## Installation
> Clone project ...

## Dependecies 
- Nodemon
- @influxdata/influxdb-client

## Useful commands
###Run app in background
> Install forever and run the following cmds
```shell
 forever start /server_esp/index.js
 forever restart /server_esp/index.js
 forever stop /server_esp/index.js
```
> Can also uses nodemon
```shell
 npm start
```
