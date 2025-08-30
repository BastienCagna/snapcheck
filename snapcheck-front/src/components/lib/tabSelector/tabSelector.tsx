import React from 'react';
import { Close } from '@mui/icons-material';
import "./tabSelector.css"

type TabSelectorItem = {
    label: string;
    onClick: () => void;
    isActive: boolean;
};

type TabSelectorProps = {
    onClick?: () => void;
    items: TabSelectorItem[];
};

const TabSelector: React.FC<TabSelectorProps> = ({ onClick, items }) => {
    return <div
        onClick={onClick}
        className={`tab-selector`}
    >
        {items.map(item => (
            <div className={`tab-selector-item ${item.isActive ? 'active' : ''}`} key={item.label} onClick={item.onClick}>
                {item.label}
                <span className='close-icon'><Close className='fb-item-icon' fontSize='xsmall' /></span>
            </div>
        ))}
    </div>;
};

export default TabSelector;