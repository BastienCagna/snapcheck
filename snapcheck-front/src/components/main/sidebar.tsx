import React from 'react';
import './sidebar.css';
import type { QualityControlModel } from '../../api';
import Button from '../lib/button';
import NoteInput from './components/noteinput';


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
            <Button onClick={() => { }}>Save</Button>
            <Button onClick={() => { }}>Export</Button>

            <h2>{qc?.title}</h2>
            <h3>Metadata</h3>
            <DictionaryTable dictionary={qc?.metadata || {}} />

            <h3>Boards</h3>
            {
                qc?.boards?.length ? (
                    <ul>
                        {qc.boards.map((board, index) => (
                            <li key={index}>
                                <strong>{board.title}</strong>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className='default-text'>No boards available.</p>
                )
            }

            <h3>Notes</h3>
            {qc?.notes?.map((note) => (<NoteInput key={note.name} note={note} />))}
        </div >
    );
};

export default Sidebar;