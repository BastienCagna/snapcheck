import React, { useState, useRef, useEffect, ReactNode, MouseEvent } from 'react';

import './contextualMenu.css'

type ContextualMenuItemProps = {
    label: string;
    icon?: ReactNode;
    onClick?: () => void;
    items?: ContextualMenuItemProps[];
    style?: React.CSSProperties;
};

export const ContextualMenuItem: React.FC<ContextualMenuItemProps> = ({ label, icon, onClick, items, style}) => {
    const [submenuVisible, setSubmenuVisible] = useState(false);

    return  <div
        className="contextual-menu-item"
        onMouseEnter={() => { if (items && items.length > 0) setSubmenuVisible(true); }}
        onMouseLeave={() => { if (items && items.length > 0) setSubmenuVisible(false); }}
        onClick={() => { if (!items && onClick) onClick(); }}
        style={style}
    >
        {icon && <span className="icon">{icon}</span>}
        <span className="label">{label}</span>
        {Array.isArray(items) && items.length > 0 && (
            <span className="submenu-arrow">▶</span>
        )}
        {submenuVisible && items && items.length > 0 && (
            <div className="contextual-submenu" style={{ left: '100%', top: 0, position: 'absolute' }}>
                {items.map((subItem, idx) => (
                    <ContextualMenuItem key={idx} {...subItem} />
                ))}
            </div>
        )}
    </div>
}

type ContextualMenuProps = {
    items: ContextualMenuItemProps[]
    children: ReactNode;
    parentClass?: string | null;
    style?: React.CSSProperties;
};

export const ContextualMenu: React.FC<ContextualMenuProps> = ({ items, children, parentClass, style }) => {
    const [visible, setVisible] = useState(false);
    const [position, setPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClick = (event: MouseEvent | MouseEventInit) => {
            setVisible(false);
        };

        if (visible) {
            document.addEventListener('click', handleClick as any);
        }
        return () => {
            document.removeEventListener('click', handleClick as any);
        };
    }, [visible]);

    const handleContextMenu = (event: React.MouseEvent) => {
        event.preventDefault();
        let rect = null;
        if(parentClass) {
            rect = (event.target as HTMLElement).closest(`.${parentClass}`)?.getBoundingClientRect();
        }
        if(!rect) {
            rect = (event.target as HTMLElement).getBoundingClientRect();
        }
        setPosition({ x: event.pageX - rect.left, y: event.pageY - rect.top });
        setVisible(true);
    };

    const handleMouseLeave = (e: React.MouseEvent) => {
        const menu = menuRef.current;
        if (menu) {
            const rect = menu.getBoundingClientRect();
            const mouseX = e.clientX;
            const mouseY = e.clientY;
            const withinX = mouseX >= rect.left - 10 && mouseX <= rect.right + 10;
            const withinY = mouseY >= rect.top - 10 && mouseY <= rect.bottom + 10;
            if (withinX && withinY) {
                return;
            }
        }
        setVisible(false);
    }

    return (
        <div onContextMenu={handleContextMenu} >
            {children}
            {visible && (
                <div
                    ref={menuRef}
                    className='contextual-menu'
                    style={{
                        ...style,
                        top: position.y - 10,
                        left: position.x - 10
                    }}
                    onMouseLeave={handleMouseLeave}
                >
                    {items.map((item, index) => (
                        <ContextualMenuItem key={index} {...item} />
                    ))}
                </div>
            )}
        </div>
    );
};