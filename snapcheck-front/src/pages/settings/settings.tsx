import { useEffect, useState } from "react";
import "./settings.css"
import { useSettings } from "../../contexts/SettingsContext";


const SettingsPage: React.FC<{}> = () => {
    const { settings } = useSettings();

    return <div>        
        <h1>Settings</h1>
        {settings.map((group) => (
        <div key={group.id} className="settings-group">
            <h2>{group.title}</h2>
            <table>
                <tbody>
                {group.settings.map((setting) => (
                    <tr key={setting.id}>
                        <th>{setting.label}</th>
                        <td>
                            <input type="text" value={setting.value || ""} />
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
        ))}
    </div>
}

export default SettingsPage;