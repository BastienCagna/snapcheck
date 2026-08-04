import React, { useRef, useState } from 'react';
import type { RatingModel, RatingScaleItem } from '@lepton/api-client';
import { InfoOutline } from '@mui/icons-material';
import { useModal } from '../../../contexts/ModalContext';

import './ratinginput.css';
interface RatingInputProps {
    rating: RatingModel;
    onChange?: (rating: RatingModel, field: string, value: any) => void;
    highlight?: boolean;
}

const RatingInput: React.FC<RatingInputProps> = ({ rating, onChange, highlight }) => {
    const [selectedValue, setSelectedValue] = useState<number | undefined | null>(rating.value);
    const [comment, setComment] = useState<string>(rating.comment || '');
    const commentInputRef = useRef<HTMLInputElement>(null);

    // const { showModal } = useModal();

    const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedValue(Number(event.target.value));
        if (commentInputRef.current) {
            commentInputRef.current.focus();
        }
        if (onChange) {
            onChange(rating.id, "value", Number(event.target.value));
        }
    };

    const handleCommentChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setComment(event.target.value);
        if (onChange) {
            onChange(rating.id, "comment", event.target.value);
        }
    };

    const name = rating.name || 'Unnamed (#' + rating.id + ')';
    const selectedRatingScale = rating.scale?.ratings.find((nt: RatingScaleItem) => nt.value === selectedValue);

    return <div className={`rating-input ${highlight ? ' rating-highlight' : ''}`}>
        <div className="rating-state-bar"></div>
        <div className="rating-content">
            <div>
                <span className="rating-name">{name}</span>
                <select
                    className="rating-select"
                    value={(selectedValue == undefined || isNaN(selectedValue)) ? undefined : selectedValue}
                    onChange={handleSelectChange}
                    onBlur={(event: React.FocusEvent<HTMLSelectElement>) => {
                        const newValue = Number(event.target.value);
                        if (newValue !== rating.value) {
                            onChange?.(rating.id, "value", newValue);
                        }
                    }}
                    disabled={rating.scale == undefined}
                    style={(selectedRatingScale && selectedRatingScale.color) ? { backgroundColor: selectedRatingScale.color } : {}}
                >
                    <option value={undefined}>
                        --
                    </option>
                    {rating.scale?.ratings &&
                        rating.scale.ratings.map((nt: RatingScaleItem, idx: number) => (
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
                {/* <div className='rating-infos-btn' onClick={()=>showModal(<div><h1>{name}</h1><p>{rating.description}</p></div>)}>
                    <InfoOutline fontSize='xxsmall' />
                </div> */}
                <input
                    type="text"
                    className='rating-comment'
                    ref={commentInputRef}
                    placeholder="No comment"
                    value={comment}
                    onChange={handleCommentChange}
                    onBlur={(event: React.FocusEvent<HTMLInputElement>) => {
                        const newComment = event.target.value;
                        if (newComment !== rating.comment) {
                            onChange?.(rating.id, "comment", newComment);
                        }
                    }}
                />
            </div>
        </div>
    </div>;
};

export default RatingInput;