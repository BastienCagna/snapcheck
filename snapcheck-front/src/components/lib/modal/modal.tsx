import React, { useState } from "react";
import "./modal.css";
import { Close } from "@mui/icons-material";
import { useModal } from "../../../contexts/ModalContext";


type ModalProps = {
};

const Modal: React.FC<ModalProps> = () => {
    const { content, hideModal } = useModal()
    const [width, setWidth] = useState<number>(600);
    const [isDraggingWidth, setIsDraggingWidth] = useState<boolean>(false);

    return <div className="modal" style={{ width, visibility: content !== null ? "visible" : "hidden" }}>
        <div 
            className="modal-separator" 
            onMouseDown={() => setIsDraggingWidth(true)}
            onMouseUp={() => setIsDraggingWidth(false)}
            onMouseMove={(e) => { 
                if (!isDraggingWidth) return 
                const rect = (e.target as HTMLElement).getBoundingClientRect();
                const dist = e.clientX - rect.right
                setWidth(width + dist) 
            }}
            onMouseLeave={(e) => {
                const rect = (e.target as HTMLElement).getBoundingClientRect();
                if (Math.abs(e.clientX - rect.right) > 10) {
                    // The mouse is more than 10px away from the right border
                    setIsDraggingWidth(false)
                }
            }}
        />
        <div className="modal-content">
            <div style={{ textAlign: "right" }} onClick={() => hideModal()}><Close className='fb-item-icon'/></div>
            {content}
        </div>
    </div>
};

export default Modal;