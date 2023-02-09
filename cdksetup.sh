#!/bin/bash

# cdk install - NodeJS
sudo apt-get install curl
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - &&\
sudo apt-get install nodejs

# cdk install - cdk
npm install -g aws-cdk


