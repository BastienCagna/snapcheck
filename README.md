# SnapCheck
SnapCheck is a tool to annotate data displayed by graphical boards. Its main goal is to provides an interface to assign ratings to data observed throughout sets of screenshots.


## Quick Start


## Main Concepts

### Elements
Any piece of data displayed throughou web frontend. Exemple: images (JPEG, PNG, GIF...)

### Ratings
A rating is an annotation based on a scale wich may be accompagnied by a comment.

### Board
A set of elements which are displayed together. Each board can refer to several ratings.

### Snaps
The set of ratings and boards plus a general comment.


## Make a snap

### First create a rating scale
```python
from snapcheck.snap.rating import RatingScale, RatingScaleItem

generic_scale = RatingScale(
    description="Generic Scale",
    ratings=[
        RatingScaleItem(name="Bad", value=0, description="Too bad data", color="red"),
        RatingScaleItem(name="Ok", value=1, description="Good enough data", color="lightgreen"),
        RatingScaleItem(name="Excellent", value=2, description="Outstanding sample", color="green")
    ]
)
```

### Create some ratings
```python
from snapcheck.snap.rating import Rating

fa_rating = Rating(
    id="tracto_fa",
    name="Carte de FA",
    description="Qualité de la carte de FA",
    scale=generic_scale
)
md_rating = Rating(
    id="tracto_md",
    name="Carte de MD",
    description="Qualité de la carte de MD",
    scale=generic_scale
)
```

### Create a board
```python
from snapcheck.snap import Board, ImageElement

metrics_board = Board(
    title="Cartes de métriques",
    description="Vérifiez la qualité des cartes de métriques.",
    elements=[
        ImageElement(title="Carte de FA", src=".local/demo_sources/CST_FA_and_bundles_masks.png", intended_ratings=[fa_rating]),
        ImageElement(title="Carte de MD", src=".local/demo_sources/CST_MD_and_bundles_masks.png", intended_ratings=[md_rating])
    ]
)

```


### And save it in a new snap file
```python
from snapcheck.snap.io import load_snap

qc = Snap(
    title="Tractométrie",
    description=f"Tractométrie du CST (Corticospinal Tract) pour le sujet {visit.subject}/{visit.visit}",
    metadata=visit.__dict__,
    ratings=[subject_observations, b0_rating, mni_registration_rating, fa_rating, md_rating] + bundles_ratings,
    boards=[preproc_board, cst_board, metrics_board],
)

f = ".local/demo.snpk"
# qc.to_json(f)
qc.save(f)

```


## The GUI Framework
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

* add more displayable elements (graphs, medical imaging viewer, ...)
* make it usable throughout internet (adding user, security...)


## Install

### For development
The project use [Pixi](https://pixi.sh/latest/) (Conda) to manage depencies and build.

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




# TODO

Back
~~~~
* jsonpatch + websocket pour update des snaps
* numéro de session dans le JWT, possible?
    => réouverture d'une session GUI en l'état?

* save sidebar sections heights in user settings
* make each section hiddable

GUI
~~~
* debouncing + websocket + patchs
* changement de fichier marche pas
* affichage de la première board à l'ouverture du fichier
* nom du fichier n'apparait pas
* les notes et metadonnées ne s'affiche pas?
* pas de mouvement au clics (gauche et droit, seulement molette)
* scroll sur les planches
* navigation avecles flêches aussi
* grossiessement du menu lors du dezoom sur les boards
* transformation des boards board/board
* lorsqu'un fichier est ouvert, afficher le dossier du fichier dans le broswer de fichiers
* clear le champs de recherche du broswer lorsqu'on change de fichier
