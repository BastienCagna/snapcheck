from typing import List
from pydantic import BaseModel
from lepton_common.objects import Serializable


SETTINGS_VERSION = "dev.1.0"


NumericalValues = int | float
ValueTypes = str | bool | NumericalValues


class SettingModel(BaseModel):
    id: str
    label: str
    type: str
    choices: List[ValueTypes] | None = None
    min: NumericalValues | None = None
    max: NumericalValues | None = None
    default: ValueTypes | None = None
    value: ValueTypes | None = None
    description: str = ""
    auto_default: bool = True


class SettingsGroupModel(BaseModel):
    id: str
    title: str
    settings: List[SettingModel]


class Setting(Serializable):
    id: str
    label: str
    type: str  # string, int, ...
    choices: List[ValueTypes] | None = None
    min: NumericalValues | None = None
    max: NumericalValues | None = None
    default: ValueTypes | None = None
    value: ValueTypes | None = None
    description: str = ""
    auto_default: bool = True

    _is_getting = False

    def __init__(
        self,
        id: str,
        label: str,
        type: str,
        choices: List[ValueTypes] | None = None,
        min: NumericalValues | None = None,
        max: NumericalValues | None = None,
        default: ValueTypes | None = None,
        value: ValueTypes | None = None,
        description: str = "",
        auto_default: bool = True,
    ):
        super().__init__()
        self.id = id
        self.label = label
        self.type = type
        self.choices = choices
        self.min = min
        self.max = max
        self.default = default
        self.value = value
        self.description = description
        self.auto_default = auto_default

    def __getattribute__(self, name):
        if name == "value" and not self._is_getting and self.auto_default:
            self._is_getting = True
            if self.value is None:
                val = self.default
            self._is_getting = False
            return val
        return super().__getattribute__(name)


class SettingsGroup(Serializable):
    id: str
    title: str
    settings: List[Setting]

    def __init__(self, id: str, title: str, settings: List[Setting]):
        super().__init__()
        self.id = id
        self.title = title
        self.settings = settings


class Settings(Serializable):
    version: str = SETTINGS_VERSION
    groups: List[SettingsGroup]

    def __init__(self, groups: List[SettingsGroup], version=SETTINGS_VERSION):
        super().__init__()
        self.groups = groups
        self.version = version

    def get(self, set_path: str) -> Setting:
        grp_id, set_id = set_path.split(".")
        for group in self.groups:
            if group.id == grp_id:
                for setting in group.settings:
                    if setting.id == set_id:
                        return setting
        raise ValueError(f"Setting not found: {set_path}")

    # def to_dict(self):
    #     return {
    #         "version": self.version,
    #         "groups": [group.to_dict() for group in self.groups]
    #     }

    # def from_dict(cls, data: dict) -> "Settings":
    #     version = data.get("version", SETTINGS_VERSION)
    #     groups = [SettingsGroupModel.from_dict(g) for g in data.get("groups", [])]
    #     return cls(version=version, groups=groups)
