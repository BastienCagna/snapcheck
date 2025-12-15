from snapcheck.snap.board import ImageElement
from snapcheck.snap.cati import CATIVisit
from snapcheck.snap import Snap, Board, Element
from snapcheck.snap.io import load_snap
from snapcheck.snap.rating import Rating, RatingScale, RatingScaleItem


visit = CATIVisit(
    protocol="protocol_demo",
    study="study1",
    center="center1",
    subject="001XM02",
    visit="M0"
)

colors = [
    "#330C00",
    "#5f3c00",
    "#5A5400",
    "#364900",
    "#003002"
]

generic_scale = RatingScale(
    description="Notation générique",
    ratings=[
        RatingScaleItem(name="Mauvais", value=0, description="Incontestablement inexploitable", color=colors[0]),
        RatingScaleItem(name="Limite", value=1, description="Défauts notables. Utilisation peu recommandée.", color=colors[1]),
        RatingScaleItem(name="Presque ok", value=2, description="Défauts mineurs. Utilisation recommandée avec précautions.", color=colors[2]),
        RatingScaleItem(name="Ok", value=3, description="Standard. Utilisation approuvée sans réserve.", color=colors[3]),
        RatingScaleItem(name="Excellent", value=4, description="Aucun défaut. Mieux que la moyenne.", color=colors[4]),
    ]
)

fibre_scale = RatingScale(
    description="Répartition des fibres",
    ratings=[
        RatingScaleItem(name="KO", value=0, description="Donnée manquante ou inexploitable.", color=colors[0]),
        RatingScaleItem(name="Mauvaise", value=1, description="Au moins une des zones ne contient aucune fibre (ou très peu).", color=colors[1]),
        RatingScaleItem(name="Limite", value=2, description="Au moins quelques fibres présentes dans toutes les zones.", color=colors[2]),
        RatingScaleItem(name="Bien", value=3, description="Toutes les zones présentnt un nombre nombre concéquent de fibres.", color=colors[3]),
        RatingScaleItem(name="Excellente", value=4, description="Répartition très homogène.", color=colors[4]),
    ]
)


subject_observations = Rating(
    name="Sujet",
    description="Observations"
    # No scale as it is only a comment rating
)

#######################
# Preprocessing board #
#######################
b0_rating = Rating(
    id="tracto_b0",
    name="b=0",
    description="Qualité de l'image b=0",
    scale=generic_scale
)

mni_registration_rating = Rating(
    id="tracto_registration",
    name="MNI Registration",
    description="Réussite de l'alignement de la FA sur l'espace MNI",
    scale=generic_scale
)

preproc_board = Board(
    title="Pré-traitements",
    description="Vérifiez la b=0 et le bon alignement de la FA sur l'espace modèle MNI.",
    elements=[
        ImageElement(title="Input DWI (b=0)", src="./.local/demo_sources/input_dwi.png", intended_ratings=[b0_rating]),
        ImageElement(title="FA & MNI", src=".local/demo_sources/FA_and_MNI_template.gif", intended_ratings=[mni_registration_rating]),
    ]
)

#################
# Bundles board #
#################
bundles_ratings = []
bundles = ["CST Left", "CST Right"]
for bundle in sorted(bundles):
    bundle_nickname = bundle.lower().replace(" ", "_")
    b_mask_rating = Rating(
        id="tracto_bundle_mask_" + bundle_nickname,
        name=f"Masque {bundle}",
        description=f"Qualité des masques du bundle {bundle}",
        scale=generic_scale
    )
    b_fibers_rating = Rating(
        id="tracto_bundle_fibers_" + bundle_nickname,
        name=f"Fibres {bundle}",
        description=f"Répartition homogène des fibres du bundle",
        scale=fibre_scale
    )
    bundles_ratings.extend([b_mask_rating, b_fibers_rating])

cst_board = Board(
    title="Faisceau CST",
    description="Vérifiez la qualité des masques et la répartition des fibres du bundle CST.",
    elements=[
        ImageElement(title="Masques du faisceau sur la FA (espace MNI)", src=".local/demo_sources/bundles_on_subject_FA_MNI_axial.png"),
        ImageElement(src=".local/demo_sources/bundles_on_subject_FA_MNI_coronal.png"),
        ImageElement(title="Tract Orientation Maps", src=".local/demo_sources/bundles_TOM.png"),
        ImageElement(title="Tractographie", src=".local/demo_sources/tractography_all.gif", intended_ratings=bundles_ratings)
    ]
)

dev_board = Board(
    title="Développement",
    description="Board de développement pour tester des éléments.",
    elements=[
        ImageElement(title="Image de test", src=".local/demo_sources/test_image.png"),
        Element(title="Texte de test", content="Ceci est un texte de test pour le board de développement.")
    ]
)

#################
# Metrics board #
#################
metrics = ["FA", "MD"]
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

metrics_board = Board(
    title="Cartes de métriques",
    description="Vérifiez la qualité des cartes de métriques.",
    elements=[
        ImageElement(title="Carte de FA", src=".local/demo_sources/CST_FA_and_bundles_masks.png", intended_ratings=[fa_rating]),
        ImageElement(title="Carte de MD", src=".local/demo_sources/CST_MD_and_bundles_masks.png", intended_ratings=[md_rating])
    ]
)

##########################
# Create Quality Control #
##########################
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

qc_r = load_snap(f)