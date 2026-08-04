import { useState } from "react";
import FilesBrowser from "../../components/files/browser/browser";


const ExportHTMLPage: React.FC<{ onSubmit: (path: string) => string | boolean }> = ({ onSubmit }) => {
    const [currentPath, setCurrentPath] = useState<string>("");
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const submit = () => {
        const res = onSubmit(currentPath)
        if (!res) hideModal();
        else {
            setErrorMsg(typeof res === "string" ? res : "An error occurred while exporting.");
        }
    }

    return <div>
        <h1>Export</h1>
        <h2>HTML</h2>

        <FilesBrowser
            path={currentPath}
            onPathChange={(p) => setCurrentPath(p || "")}
            // onFileSelect={(path: string) => submit()}
            extensions={[".snpk"]}
        />
        {errorMsg && <p className="error-message">{errorMsg}</p>}
        <button onClick={submit}>Export</button>
    </div>
}

export default ExportHTMLPage;

function hideModal() {
    throw new Error("Function not implemented.");
}
