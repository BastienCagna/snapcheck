import React, { useRef, useState } from 'react';
import type { NoteModel } from '../api/models/NoteModel';
import type { NoteScaleModel } from '../api/models/NoteScaleModel';
import type { NoteScaleItem } from '../api';


interface NoteInputProps {
    note: NoteModel;
    onChange?: (note: NoteModel) => void;
}

const NoteInput: React.FC<NoteInputProps> = ({ note, onChange }) => {
    const [selectedValue, setSelectedValue] = useState<number | undefined | null>(note.value);
    const [comment, setComment] = useState<string>(note.comment || '');
    const commentInputRef = useRef<HTMLInputElement>(null);

    const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedValue(Number(event.target.value));
        if (commentInputRef.current) {
            commentInputRef.current.focus();
        }
        if (onChange) {
            onChange({ ...note, value: Number(event.target.value) });
        }
    };

    const handleCommentChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setComment(event.target.value);
        if (onChange) {
            onChange({ ...note, comment: event.target.value });
        }
    };

    const name = note.name || 'Unnamed (#' + note.id + ')';
    return (
        <div style={{ display: 'flex', gap: '1rem' }}>
            <div>
                <label>{name}</label>
            </div>
            <div style={{display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
                <select 
                        value={(selectedValue == undefined || isNaN(selectedValue)) ? undefined : selectedValue} 
                        onChange={handleSelectChange} 
                        disabled={note.scale==undefined}
                >
                    <option value={undefined}>
                        --
                    </option>
                    {note.scale?.notes &&
                        note.scale.notes.map((nt: NoteScaleItem, idx: number) => (
                            <option key={idx+1} value={nt.value}>
                                {nt.value} - {nt.name} 
                            </option>
                        ))}
                </select>
                {/* <input
                    type="text"
                    ref={commentInputRef}
                    placeholder="Comment..."
                    value={comment}
                    onChange={handleCommentChange}
                    style={{ visibility: 'collapse' }}
                /> */}
            </div>
        </div>
    );
};

export default NoteInput;