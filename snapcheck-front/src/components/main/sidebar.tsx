import React from 'react';
import './sidebar.css';
import type { QualityControlModel } from '../../api';
import Button from '../lib/button';


const DictionaryTable: React.FC<{ dictionary: Record<string, string | number> }> = ({ dictionary }) => {
    return (
        <table className="dictionary-table">
            <thead>
            </thead>
            <tbody>
                {Object.entries(dictionary).map(([key, value]) => (
                    <tr key={key}>
                        <td>{key}</td>
                        <td>{value}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

const Sidebar: React.FC<{
    qc: QualityControlModel | null;
    onLoadRequest?: () => void;
}> = ({ qc, onLoadRequest }) => {
    return (
        <div className="sidebar">
            <Button onClick={onLoadRequest}>Load</Button>
            <DictionaryTable dictionary={qc?.data_coordinates || {}} />
        </div>
    );
};

export default Sidebar;