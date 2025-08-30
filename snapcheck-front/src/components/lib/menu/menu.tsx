import React, { useState } from "react";
import "./menu.css";

type MenuItem = {
    label: string;
    onClick?: () => void;
    disabled?: boolean;
    children?: MenuItem[];
}| {
    type: "separator";
};



type MenuProps = {
    items: MenuItem[];
};

const Menu: React.FC<MenuProps> = ({ items }) => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    const childs = items.map((item, idx) => (
        <div
            key={item.label}
            className={"menu-item" + (openIndex === idx ? " open" : "")}
            onClick={() => { if (openIndex == idx) setOpenIndex(null); else setOpenIndex(idx) }}
            onMouseOver={() => {if(openIndex !== null) setOpenIndex(idx)}}
            onMouseLeave={() => setOpenIndex(null)}
        >  
            <div
                className="menu-button"
                onClick={item.onClick}
                tabIndex={idx}
            >
                {item.label}
            </div>
            {item.children && openIndex === idx && (
                <div className="menu-dropdown">
                    {item.children.map((child) =>
                        child.type === "separator" ? (
                            <div key="separator" className="menu-separator"></div>
                        ) : (
                            <div
                                key={child.label}
                                className="menu-inner-item"
                                onClick={() => { setOpenIndex(null); if (child.onClick)child.onClick(); }}
                                tabIndex={0}
                                disabled={child.disabled}
                            >
                                <span>{child.label}</span>
                            </div>
                        )
                    )}
                </div>
            )}
        </div>
    ));

    return (
        <nav className='menu'>
            {childs}
        </nav>
    );
};

export type { MenuItem, MenuProps };
export default Menu;