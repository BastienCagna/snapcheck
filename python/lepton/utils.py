from fastapi import Request
import typing

if typing.TYPE_CHECKING:
    from lepton.app import LeptonApp


def get_lepton_app(request: Request) -> "LeptonApp":
    return request.app.state.lepton_app
