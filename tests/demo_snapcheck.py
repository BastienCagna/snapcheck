from snapcheck.qc.board import ImageElement
from snapcheck.qc.cati import CATIVisit
from snapcheck.qc import QualityControl, Board, Element
from snapcheck.qc.io import load_quality_control
from snapcheck.qc.note import Note, NoteScale, NoteScaleItem


visit = CATIVisit(
    protocol="protocol_demo",
    study="study1",
    center="center1",
    subject="001XM02",
    visit="M0"
)


generic_scale = NoteScale(
    description="Notation générique",
    notes=[
        NoteScaleItem(name="Mauvais", value=0, description="Incontestablement inexploitable"),
        NoteScaleItem(name="Limite", value=1, description="Défauts notables. Utilisation peu recommandée."),
        NoteScaleItem(name="Presque ok", value=2, description="Défauts mineurs. Utilisation recommandée avec précautions."),
        NoteScaleItem(name="Ok", value=3, description="Standard. Utilisation approuvée sans réserve."),
        NoteScaleItem(name="Excellent", value=4, description="Aucun défaut. Mieux que la moyenne."),
    ]
)

fibre_scale = NoteScale(
    description="Répartition des fibres",
    notes=[
        NoteScaleItem(name="KO", value=0, description="Donnée manquante ou inexploitable."),
        NoteScaleItem(name="Mauvaise", value=1, description="Au moins une des zones ne contient aucune fibre (ou très peu)."),
        NoteScaleItem(name="Limite", value=2, description="Au moins quelques fibres présentes dans toutes les zones."),
        NoteScaleItem(name="Bien", value=3, description="Toutes les zones présentnt un nombre nombre concéquent de fibres."),
        NoteScaleItem(name="Excellente", value=4, description="Répartition très homogène."),
    ]
)


subject_observations = Note(
    name="Sujet",
    description="Observations"
    # No scale as it is only a comment note
)

#######################
# Preprocessing board #
#######################
b0_note = Note(
    id="tracto_b0",
    name="b=0",
    description="Qualité de l'image b=0",
    scale=generic_scale
)

mni_registration_note = Note(
    id="tracto_registration",
    name="MNI Registration",
    description="Réussite de l'alignement de la FA sur l'espace MNI",
    scale=generic_scale
)

preproc_board = Board(
    title="Pré-traitements",
    description="Vérifiez la b=0 et le bon alignement de la FA sur l'espace modèle MNI.",
    intended_notes=[b0_note, mni_registration_note],
    elements=[
        ImageElement(title="Input DWI (b=0)", src="./.local/demo_sources/input_dwi.png"),
        ImageElement(title="FA & MNI", src=".local/demo_sources/FA_and_MNI_template.gif"),
    ]
)

#################
# Bundles board #
#################
bundles_notes = []
bundles = ["CST Left", "CST Right"]
for bundle in sorted(bundles):
    bundle_nickname = bundle.lower().replace(" ", "_")
    b_mask_note = Note(
        id="tracto_bundle_mask_" + bundle_nickname,
        name=f"Masque {bundle}",
        description=f"Qualité des masques du bundle {bundle}",
        scale=generic_scale
    )
    b_fibers_note = Note(
        id="tracto_bundle_fibers_" + bundle_nickname,
        name=f"Fibres {bundle}",
        description=f"Répartition homogène des fibres du bundle",
        scale=fibre_scale
    )
    bundles_notes.extend([b_mask_note, b_fibers_note])

cst_board = Board(
    title="Faisceau CST",
    description="Vérifiez la qualité des masques et la répartition des fibres du bundle CST.",
    intended_notes=bundles_notes,
    elements=[
        ImageElement(title="Masques du faisceau sur la FA (espace MNI)", src=".local/demo_sources/bundles_on_subject_FA_MNI_axial.png"),
        ImageElement(src=".local/demo_sources/bundles_on_subject_FA_MNI_coronal.png"),
        ImageElement(title="Tract Orientation Maps", src=".local/demo_sources/bundles_TOM.png"),
        ImageElement(title="Tractographie", src=".local/demo_sources/tractography.gif")
    ]
)

dev_board = Board(
    title="Développement",
    description="Board de développement pour tester des éléments.",
    intended_notes=[],
    elements=[
        ImageElement(title="Image de test", src=".local/demo_sources/test_image.png"),
        Element(title="Texte de test", content="Ceci est un texte de test pour le board de développement.")
    ]
)

#################
# Metrics board #
#################
metrics = ["FA", "MD"]
fa_note = Note(
    id="tracto_fa",
    name="Carte de FA",
    description="Qualité de la carte de FA",
    scale=generic_scale
)
md_note = Note(
    id="tracto_md",
    name="Carte de MD",
    description="Qualité de la carte de MD",
    scale=generic_scale
)

metrics_board = Board(
    title="Cartes de métriques",
    description="Vérifiez la qualité des cartes de métriques.",
    intended_notes=[fa_note, md_note],
    elements=[
        ImageElement(title="Carte de FA", src=".local/demo_sources/CST_FA_and_bundles_masks.png"),
        ImageElement(title="Carte de MD", src=".local/demo_sources/CST_MD_and_bundles_masks.png")
    ]
)

##########################
# Create Quality Control #
##########################
qc = QualityControl(
    title="Tractométrie",
    description=f"Tractométrie du CST (Corticospinal Tract) pour le sujet {visit.subject}/{visit.visit}",
    metadata=visit.__dict__,
    notes=[subject_observations, b0_note, mni_registration_note, fa_note, md_note] + bundles_notes,
    boards=[preproc_board, cst_board, metrics_board],
)

f = ".local/demo.snpk"
# qc.to_json(f)
qc.save(f)

qc_r = load_quality_control(f)