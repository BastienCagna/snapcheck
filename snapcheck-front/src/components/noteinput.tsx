import React, { useState } from 'react';
import type { NoteModel } from '../api/models/NoteModel';
import type { NoteScaleModel } from '../api/models/NoteScaleModel';


interface NoteInputProps {
    note: NoteModel;
}

const NoteInput: React.FC<NoteInputProps> = ({ note }) => {
    const [selectedValue, setSelectedValue] = useState<number | undefined>(note.value);
    const [comment, setComment] = useState<string>(note.comment || '');

    const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedValue(Number(event.target.value));
    };

    const handleCommentChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setComment(event.target.value);
    };

    const name = note.name || 'Unnamed (#' + note.id + ')';
    return (
        <div>
            <div>
                <label>{name}</label>
            </div>
            <div style={{ display: 'flex', gap: '1rem' }}>
                <select value={selectedValue || ''} onChange={handleSelectChange}>
                    <option value="" disabled>
                        Select a value
                    </option>
                    {note.scale?.notes &&
                        Object.keys(note.scale.notes).map((key) => (
                            <option key={key} value={key}>
                                {note.scale?.notes[key]}
                            </option>
                        ))}
                </select>
                <input
                    type="text"
                    placeholder="Add a comment"
                    value={comment}
                    onChange={handleCommentChange}
                />
            </div>
        </div>
    );
};

export default NoteInput;