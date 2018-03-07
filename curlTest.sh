#!/bin/bash
echo "GET"
curl -XGET localhost:8080
echo "POST"
curl -d "param=value" -XPOST localhost:8080
echo "HEAD"
curl -I localhost:8080
echo "OPTIONS"
curl -i -XOPTIONS localhost:8080
