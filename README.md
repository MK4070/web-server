# Web Server

A simple, customizable web server implementation in Python. This project demonstrates how to build and enhance a web server, with various improvements published across different versions.

## Table of Contents

- [Description](#description)
- [Usage](#usage)
- [Configuration](#configuration)

## Description

This project implements a basic web server using Python's built-in libraries. In the latest version it supports 
- HTTP requests
- Handles routing
- Serving static files
- Directory listings
- Loading CGI files
- Reverse Proxy Load Balancing
- Server Logging

## Usage

To get started with this project, you can clone the repository and install the necessary dependencies.

1. Clone the repository:
```bash
git clone https://github.com/MK4070/web-server.git
```
\
2. Navigate to the Project Directory:
```bash
cd web-server
python main.py
```

## Configuration 
The server can be customized by modifying the `config.ini` file. This file allows you to set parameters such as the host, port, and other server settings.

Serving Static Files and CGI: 
Place any static files or CGI scripts you wish to serve in the `static` directory. The server is configured to serve files from this directory.

Server logs are stored in the `logs` directory. You can monitor this directory to review server logs.