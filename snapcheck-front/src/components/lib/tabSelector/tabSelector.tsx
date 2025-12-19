import React from 'react';
import { Close } from '@mui/icons-material';
import "./tabSelector.css"
import { ContextualMenu } from '../contextualMenu/contextualMenu';

type TabSelectorItem = {
    label: string;
    onSelect?: () => void;
    onClose?: () => void;
    isActive: boolean;
};

type TabSelectorProps = {
    items: TabSelectorItem[];
};

const TabSelector: React.FC<TabSelectorProps> = ({ items }) => {
    return <div className="tab-selector">
        {items.map((item, index) => (
            <ContextualMenu parentClass="tab-selector" items={[{label: "Close"}, {label: "Save"}]} key={index}>
                <div className={`tab-selector-item ${item.isActive ? 'active' : ''}`} key={item.label} onClick={item.onSelect}>
                    {item.label}
                    <span className='close-icon' onClick={item.onClose}><Close className='fb-item-icon' fontSize='xsmall' /></span>
                </div>
            </ContextualMenu>
        ))}
    </div>;
};

export default TabSelector;