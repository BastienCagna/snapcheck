import { useAppData } from "../../contexts/AppDataContext";
import { useSnapSession } from "../../contexts/SnapSessionContext";

const DebugPage: React.FC<{}> = () => {
    // const {session} = useSnapSession();
    const data = useAppData();

    return <div>        
        <h1>Debug</h1>
        <h2>Session</h2>
        {/* <pre>{JSON.stringify(session, null, 2)}</pre> */}
        <h2>App Data</h2>
        <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
}

export default DebugPage;