from snapcheck.snap.annotation import ArrowAnnotation
from snapcheck.snap.board import ImageElement
from snapcheck.snap import Snap, Board, Element
from snapcheck.snap.io import load_snap
from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem



colors = ["#330C00", "#5f3c00", "#5A5400", "#364900"]

generic_scale = RatingScale(
    description="Quality Rating",
    ratings=[
        RatingScaleItem(name="Too bad", value=0, description="", color=colors[0]),
        RatingScaleItem(name="Bad", value=1, description="", color=colors[1]),
        RatingScaleItem(
            name="Good",
            value=2,
            description="",
            color=colors[2],
        ),
        RatingScaleItem(name="Perfect", value=3, description="", color=colors[3]),
    ],
)


###########################
# Axial and Coronal board #
###########################
first_board = Board(
    title="Axial & Coronal Views",
    description=".",
    elements=[
        ImageElement(
            title="Axial View", 
            src="./tests/test_data/mni_axial.png",
            intended_ratings=[Rating(id="coronal", name="Coronal", description="Quality of coronal view", scale=generic_scale)]
        ),
        ImageElement(
            title="Coronal View", 
            src="./tests/test_data/mni_coronal.png",
            intended_ratings=[Rating(id="axial", name="Axial", description="Quality of axial view", scale=generic_scale)]
        ),
    ],
)

##################
# Sagittal board #
##################
sag = ImageElement(
    title="Sagittal View", 
    src="./tests/test_data/mni_lightbox.png",
    intended_ratings=[Rating(id="sagittal", name="Sagittal", description="Quality of sagittal view", scale=generic_scale)]
)
sag.annotations.append(ArrowAnnotation(x=150, y=200, width=50, length=0, color="blue", text="Check this area"))
second_board = Board(
    title="Sagittal View",
    description="",
    elements=[sag],
)


##########################
# Create Quality Control #
##########################
qc = Snap(
    title="MNI Quality Check",
    description=f"",
    ratings=first_board.all_intended_ratings + second_board.all_intended_ratings,
    boards=[first_board, second_board],
    metadata={
        "source": "MNI Template",
        "version": "1.0",
    }
)

f = ".local/mni.snpk"
qc.save(f)

qc_r = load_snap(f)
