import type { QualityControlModel } from "../../../api";
import Button from "../../../components/lib/button";
import { pyBridgeService } from "../../../core/pybridge";
import { useQC } from "../../../core/QCContext";
import "./toolbar.css";

const Toolbar: React.FC<{
}> = () => {
    const { qc, loadQC } = useQC();

    return (
        <div className="toolbar">
            <div>
                {!qc ? <Button onClick={loadQC}>Load</Button> : <Button onClick={loadQC}>Reload</Button>}
                <Button onClick={() => { }} disabled={!qc?.has_changed}>Save</Button>
                <Button onClick={() => { }} disabled={!qc?.has_changed}>Save As...</Button>
                <Button onClick={() => { }} disabled={!qc?.is_cancellable}>Cancel</Button>
                <Button onClick={() => { }} disabled={!qc?.is_redoable}>Redo</Button>
                <Button onClick={() => { }} disabled={!qc}>Export</Button>
                <Button onClick={() => { pyBridgeService.closeApplication() }}>Close</Button>
                <Button onClick={() => { }} >Settings</Button>
            </div>
            <div>
                <h2 style={{ margin: 0, marginRight: qc?.filename ? 8 : 0 }}>{qc?.title || 'Untitled'}</h2>
            </div>
            <div>
                {qc?.filename && <h3 style={{ margin: 0 }}>{qc.filename}</h3>}
            </div>
        </div>
    );
};

export default Toolbar;