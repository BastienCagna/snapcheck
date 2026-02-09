import React, { useRef, useState } from 'react';
import type { NoteScaleItem, QualityControlModel } from '@lepton/api-client';
import './notestatbar.css';

interface NoteStatBarProps {
    qc: QualityControlModel;
}

const NoteStatBar: React.FC<NoteStatBarProps> = ({ qc }) => {
    const noteCounts = qc.notes?.length || 0;
    const colors = ['#4caf50', '#3b3a38ff'];

    const noteElements = qc.notes?.map((note, idx) => (
        <span
            key={idx}
            className="note-dot"
            style={{
                backgroundColor: colors[note.value ? 0 : 1],
                display: 'block',
                width: '100%',
                height: '100%',
                borderRadius: ".2em",
            }}
        />
    ));

    return (
        <div
            className="note-stat-bar"
            style={{ gridTemplateColumns: `repeat(${noteCounts}, 1fr)` }}
        >
            {noteElements}
        </div>
    );
};

export default NoteStatBar;