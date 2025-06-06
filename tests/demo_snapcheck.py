from snapcheck.qc.board import ImageElement
from snapcheck.qc.cati import CATIVisit
from snapcheck.qc import QualityControl, Board, Element
from snapcheck.qc.io import load_quality_control
from snapcheck.qc.note import Note, NoteScale


visit = CATIVisit(
    protocol="protocol_demo",
    study="study1",
    center="center1",
    subject="001XM02",
    visit="M0"
)


note1 = Note(
    id="note1",
    description="This is the first note",
    scale=NoteScale(
        description="Scale for note 1",
        notes={
            1: "Poor",
            2: "Fair",
            3: "Good",
            4: "Very Good",
            5: "Excellent"
        }
    ),
)

board1 = Board(
    title="Board 1",
    description="This is the first board",
    intended_notes=[note1.id],
    style={"background-color": "lightblue"},
    elements=[
        ImageElement(src="input_dwi.png"),
        # Element(component="image", props={"src": "image1.png"}, style={"width": "100px", "height": "100px"})
    ]
)

qc = QualityControl(
    data_coordinates=visit,
    notes=[note1],
    boards=[board1]
)

f = ".local/demo_snapcheck.json"
qc.save(f)

qc_r = load_quality_control(f)