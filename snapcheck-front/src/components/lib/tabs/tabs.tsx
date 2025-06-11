import React from 'react';
import './tabs.css';

type Tab = {
    title: React.ReactNode | string;
    content: React.ReactNode;
};

const Tabs: React.FC<{
    tabs: Tab[];
    initTabIndex?: number;
    // onTabChange?: (id: number) => void;
}> = ({ tabs, initTabIndex }) => {
    const [activeTab, setActiveTab] = React.useState<number>(initTabIndex || 0);

    return <div className="sc-tabs">
        <div className="sc-tabs-header">
            {tabs.map((tab, index) => (
                <div
                    key={index}
                    className={`sc-tab-header ${activeTab === index ? 'active' : ''}`}
                    onClick={() => { setActiveTab(index) }}
                >
                    {tab.title}
                </div>
            ))}
        </div>
        <div className='sc-tabs-content'>
            {tabs[activeTab].content}
        </div>
    </div>
}

export { type Tab, Tabs };