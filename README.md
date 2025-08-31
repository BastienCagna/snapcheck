# SnapCheck
SnapCheck is a tool to annotate data displayed by boards. Its main goal is to provides an interface to assign ratings to data observed throughout sets of screenshots.

## Main Concepts

### Snaps

### Board

### Rating

## The Framework
SnapCheck is made as a Web App. It is composed of a backend written in Python and a frontend, the GUI, written if TypeScript (Javascript).

### The core
The core python package, named "snapcheck", provide all it is need to create and read snap files (.snpk).

### Backend
The backend end use FastAPI to serve the snaps, settings and track some usefull data for the GUI (like the last loaded files paths).

### Frontend
The frontend use the well known React typescript framework.

### The client
Even if the SnapCheck GUI can be displayed by any web browser, a Qt based client is also provided to get a better experience (avoid to lost screen space and get a better focus).

## Install
```
pixi shell
cd snapcheck-front/
npm install
cd ../
```
SASS files must be compiled (ex: using SASS live Compiler is VSCode)

Building the javascript API for the frontend:
```shell
cd snapcheck-front/
npm run api
cd ../
```

## Test

```
pixi run client
// or
python python/snapclient/main.py
```
