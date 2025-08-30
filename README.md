# snapcheck
QC tool for neuroimaging pipelines

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
