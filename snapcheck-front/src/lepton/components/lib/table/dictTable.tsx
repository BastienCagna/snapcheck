import React from 'react';

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

export default DictionaryTable;