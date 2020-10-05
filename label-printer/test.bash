#!/bin/bash

curl -d 'model=lf0350&mac=00:0e:84:33:44:55:66&hostname=&serial=' -X POST http://localhost:8082/
curl -d 'model=lf0350&mac=00:00' -X POST http://localhost:8082/
