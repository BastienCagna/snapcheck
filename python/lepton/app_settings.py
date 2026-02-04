from lepton.settings.models import Setting, Settings, SettingsGroup
import os.path as op
from os import makedirs


CONFIG_DIR = op.join(op.expanduser("~"), ".config", "snapcheck")
SETTINGS_PATH = op.join(CONFIG_DIR, "lepton.json")


def generate_default_settings(settings_f: str, force=False):
    if op.isfile(settings_f) and not force:
        raise IOError(f"{settings_f} already exists. Use force=True to overwrite.")
    if not op.isdir(op.dirname(settings_f)):
        makedirs(op.dirname(settings_f))

    settings = Settings(groups=[
        SettingsGroup(
            id="files",
            title="Files",
            settings=[
                Setting(
                    id="default_path",
                    label="Default Browser Location",
                    description="Where the file browser opens by default.",
                    type="string",
                    default=op.join(op.expanduser("~"))
                ),
                Setting(
                    id="extensions",
                    label="Filter by extensions",
                    description="Comma-separated list of file extensions to filter by.",
                    type="string",
                    default=".snpk"
                ),
                Setting(
                    id="n_history",
                    label="Files History Length",
                    description="Number of recent files to store",
                    type="int",
                    default=20
                )
            ]
        ),
        SettingsGroup(
            id="core",
            title="Core",
            settings=[
                Setting(
                    id="share_dir",
                    label="Share Directory Path",
                    description="The data sharing directory path. It's use to save persistent data of the app.",
                    type="string",
                    default=op.join(op.expanduser("~"), ".local", "share", "snapcheck")
                ),
            ]
        )
    ])

    settings.to_json(settings_f)


def load_settings() -> Settings:
    if not op.isfile(SETTINGS_PATH):
        generate_default_settings(SETTINGS_PATH)
    return Settings.from_json(SETTINGS_PATH)

APP_SETTINGS: Settings = load_settings()