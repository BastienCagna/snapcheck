# SnapCheck
SnapCheck is a tool to annotate data displayed by boards. Its main goal is to provides an interface to assign ratings to data observed throughout sets of screenshots.

## Main Concepts

### Elements
Any piece of data displayed throughou web frontend. Exemple: images (JPEG, PNG, GIF...)

### Ratings
A rating is an annotation based on a scale wich may be accompagnied by a comment.

### Board
A set of elements which are displayed together. Each board can refer to several ratings.

### Snaps
The set of ratings and boards plus a general comment.


## The Framework
SnapCheck is made as a Web App. It is composed of a backend written in Python and a frontend, the GUI, written if TypeScript (Javascript).

### The core package (python)
The core python package, named "snapcheck", provide all it is need to create and read snap files (.snpk).

### Backend
The backend end use [FastAPI](https://fastapi.tiangolo.com/) to serve the snaps, settings and track some usefull data for the GUI (like the last loaded files paths).

### Frontend
The frontend use the well known [React](https://react.dev/) typescript framework.

The backend and the frontend can communicate thanks to an javascript API automatically generated from the FastAPI backend.

### The client
Even if the SnapCheck GUI can be displayed by any web browser, a Qt based client is also provided to get a better experience (avoid to lost screen space and get a better focus).

## Roadmap

* develop the minimal features to be usabled by the CATI team

Options:

* add more displayable elements (graphs, medical imagin viewer, ...)
* make it usable throughou internet (adding user, security...)

### Short term TODO

* close session when leaving the GUI
* use sessinoId and snapId in all snap controller routes
* add recent files to the GUI


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
