import React from 'react';
import "./lib.css"

type InlineToggleProps = {
    off: string;
    on: string;
    value: boolean;
    onChange?: (value: boolean) => void;
    className?: string;
};

const InlineToggle: React.FC<InlineToggleProps> = ({ off, on, value, onChange, className = '' }) => {
    const handleClick = (bool: boolean) => {
        if (onChange) {
            onChange(bool);
        }
    };
    return <div className={`inline-toggle ${className}`}>
        <span className={`toggle-label ${!value ? 'active' : ''}`} onClick={() => { if (value) handleClick(false) }}>{off}</span>
        <span className={`toggle-label ${value ? 'active' : ''}`} onClick={() => { if (!value) handleClick(true) }}>{on}</span>
    </div>;
};

export default InlineToggle;