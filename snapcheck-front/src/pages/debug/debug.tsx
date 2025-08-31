import { useSnapSession } from "../../contexts/SnapSessionContext";

const DebugPage: React.FC<{}> = () => {
    const {session} = useSnapSession();

    return <div>        
        <h1>Debug</h1>
        <h2>Session</h2>
        <pre>{JSON.stringify(session, null, 2)}</pre>

    </div>
}

export default DebugPage;