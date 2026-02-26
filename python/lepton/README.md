# Lepton

Lepton provides usefull features to create a file editor as a webapp. It facilitate the creation of multi-documents and multi-users application.

This python package build a REST API that can be used by the frontend to open, edit and save documents.

## How to use it

### 1 - Define your main data model
The main data model is the one that represent the file you want to edit. It will be transmitted to the frontend and then edited part by part by the user through the API service.

This class must derives from the LObject.

```python
class MyModel(LObject):
    title: str
    description: str
    a_number: int = 0
```

### 2 - Setup the application


```python
config = LeptonConfig(
    app_name="MyApp",
    frontend_path=Path(__file__).parent.parent.parent / "front",
    settings_f=Path.home() / ".config/myapp/settings.json",
    app_data_f=Path.home() / ".config/myapp/app_data.json",
)
#
app = LeptonApp(config, MyModel)
```

### 3 - Run the app

Start to serve the API:
```python
app.start_uvicorn()
```

## Features

### AppData
Manage internal app data
AppData are data that are use by the app to run properly.

### Settings
Manage user's app settings
Settings are data that can be shared accross several instance of the app


