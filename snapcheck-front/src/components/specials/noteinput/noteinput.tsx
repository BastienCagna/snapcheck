import React, { useRef, useState } from 'react';
import type { NoteScaleModel } from '../../../api/models/NoteScaleModel';
import type { NoteModel_Input, NoteScaleItem } from '../../../api';
import './noteinput.css';
import Button from '../../lib/button';
import { InfoOutline } from '@mui/icons-material';
import { useModal } from '../../../contexts/ModalContext';

interface NoteInputProps {
    note: NoteModel_Input;
    onChange?: (note: NoteModel_Input) => void;
    highlight?: boolean;
}

const NoteInput: React.FC<NoteInputProps> = ({ note, onChange, highlight }) => {
    const [selectedValue, setSelectedValue] = useState<number | undefined | null>(note.value);
    const [comment, setComment] = useState<string>(note.comment || '');
    const commentInputRef = useRef<HTMLInputElement>(null);

    const { showModal } = useModal();

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
    const selectedNoteScale = note.scale?.notes.find((nt: NoteScaleItem) => nt.value === selectedValue);

    return <div className={`note-input ${highlight ? 'highlight' : ''}`}>
        <div>
            <span className="note-name">{name}</span>
            <select
                className="note-select"
                value={(selectedValue == undefined || isNaN(selectedValue)) ? undefined : selectedValue}
                onChange={handleSelectChange}
                disabled={note.scale == undefined}
                style={(selectedNoteScale && selectedNoteScale.color) ? { backgroundColor: selectedNoteScale.color } : {}}
            >
                <option value={undefined}>
                    --
                </option>
                {note.scale?.notes &&
                    note.scale.notes.map((nt: NoteScaleItem, idx: number) => (
                        <option
                            key={idx + 1}
                            value={nt.value}
                        >
                            {nt.value} - {nt.name}
                        </option>
                    ))}
            </select>
        </div>
        <div className='rating-second-line'>
            <div className='rating-infos-btn' onClick={()=>showModal(<div><h1>{name}</h1><p>{note.description}</p></div>)}>
                <InfoOutline fontSize='xxsmall' />
            </div>
            <input
                type="text"
                className='note-comment'
                ref={commentInputRef}
                placeholder="No comment"
                value={comment}
                onChange={handleCommentChange}
            />
        </div>
    </div>;
};

export default NoteInput;