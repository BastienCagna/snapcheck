/**
 * SnapSessionContext.tsx
 * 
 * Centralized state management for the entire Snap application session.
 * Handles:
 * - Backend session lifecycle (creation, error handling)
 * - Multiple open Snap files with independent loading/error states
 * - Board navigation and selection per Snap
 * - Global GUI settings (sidebar visibility, sync settings)
 * - Optimistic updates (update before backend confirmation) with rollback on failure
 * 
 * Pattern: useReducer + Context API with async action wrapper.
 * All async operations (API calls) are wrapped with START/SUCCESS/ERROR actions.
 */

import { createContext, useCallback, useContext, useEffect, useReducer, type Dispatch } from 'react';
import type { DefaultProps } from '../core/types';
import { SnapService, type BoardModel, type SnapCheckSessionModel, type SnapModel } from '../api';

/** GUI settings that affect the overall application interface behavior */
type GUISettings = {
    showSidebar: boolean;
    syncBoards: boolean;
}
const defaultGUISettings: GUISettings = {
    showSidebar: true,
    syncBoards: false,
};

/**
 * Generic async state wrapper for any remote data.
 * Standardizes loading/error handling across session and individual snaps.
 * - data: the actual fetched/cached data
 * - loading: true during API call
 * - error: error message if fetch failed
 * - lastUpdated: timestamp of last successful fetch
 */
type AsyncState<T> = {
    data: T | null;
    loading: boolean;
    error: string | null;
    lastUpdated?: number;
};

/**
 * State for a single opened Snap file.
 * Extends AsyncState with board-specific UI state.
 * - currentBoardIndex: index of the board shown to the user (-1 if none selected)
 * - currentBoard: the actual board object (derived from boards array)
 */
type SnapState = AsyncState<SnapModel> & {
    currentBoardIndex: number;
    currentBoard: BoardModel | null;
};

/** Initial state for each newly opened Snap */
const defaultSnapState: SnapState = {
    data: null,
    loading: false,
    error: null,
    currentBoardIndex: -1,
    currentBoard: null,
};

/**
 * Root state for the entire session.
 * - session: backend session (created on app mount)
 * - snaps: all open Snap files, keyed by file path
 * - currentSnapPath: which Snap file is currently displayed
 * - guiSettings: global UI preferences
 * - loading: legacy flag for overall loading state (synced with session.loading)
 */
type SnapSessionState = {
    session: AsyncState<SnapCheckSessionModel>;
    snaps: Record<string, SnapState>;
    currentSnapPath: string | null;
    guiSettings: GUISettings;
    loading: boolean;
};

/** Initial application state (no session, no snaps open) */
const defaultSnapSessionState: SnapSessionState = {
    session: { data: null, loading: false, error: null },
    snaps: {},
    currentSnapPath: null,
    guiSettings: defaultGUISettings,
    loading: false,
};

/**
 * Action types for the reducer.
 * Generic async pattern: START/SUCCESS/ERROR for any async operation.
 * - SESSION_*: backend session initialization
 * - ASYNC_*: Snap file loading/updating (works for open, updateRating, etc.)
 * - SET_CURRENT: switch active Snap
 * - SET_BOARD: change active board within current Snap
 * - REMOVE: close a Snap file
 * - SET_GUI_SETTINGS: update GUI preferences
 * 
 * The reducer is pure: it only transforms state, never calls APIs.
 * All async orchestration happens in useSnapSessionActions hooks.
 */
type SnapSessionAction =
    | { type: 'SESSION_START' }
    | { type: 'SESSION_SUCCESS'; payload: SnapCheckSessionModel }
    | { type: 'SESSION_ERROR'; error: string }
    | { type: 'ASYNC_START'; path: string }
    | { type: 'ASYNC_SUCCESS'; path: string; payload: SnapModel }
    | { type: 'ASYNC_ERROR'; path: string; error: string }
    | { type: 'SET_CURRENT'; path: string }
    | { type: 'SET_BOARD'; boardIndex: number }
    | { type: 'REMOVE'; path: string }
    | { type: 'SET_GUI_SETTINGS'; settings: Partial<GUISettings> };

/**
 * Pure reducer function for the entire session state.
 * Transforms state immutably based on action type.
 * Handles:
 * - Session lifecycle (start/success/error)
 * - Snap CRUD (open, close, update)
 * - Board navigation with bounds checking
 * - GUI settings persistence
 */
function qcReducer(state: SnapSessionState, action: SnapSessionAction): SnapSessionState {
    // Helper: get the currently active Snap state or undefined
    const currentSnapState = state.currentSnapPath ? state.snaps[state.currentSnapPath] : undefined;

    // Helper: safely get or initialize Snap state for a given path
    const getOrCreateSnapState = (path: string): SnapState => state.snaps[path] ?? { ...defaultSnapState };

    switch (action.type) {
        // Backend session creation initiated
        case 'SESSION_START':
            return { ...state, session: { ...state.session, loading: true, error: null }, loading: true };
        // Backend session created successfully, record timestamp
        case 'SESSION_SUCCESS':
            return { ...state, session: { data: action.payload, loading: false, error: null, lastUpdated: Date.now() }, loading: false };
        // Session creation failed, store error message
        case 'SESSION_ERROR':
            return { ...state, session: { ...state.session, loading: false, error: action.error }, loading: false };
        // Switch to a different Snap file. Create placeholder if not yet loaded.
        case 'SET_CURRENT':
            if (state.snaps[action.path]) {
                return { ...state, currentSnapPath: action.path };
            }
            return {
                ...state,
                snaps: { ...state.snaps, [action.path]: { ...defaultSnapState } },
                currentSnapPath: action.path
            };
        // Async operation (e.g., loading Snap) started
        case 'ASYNC_START': {
            const snapState = getOrCreateSnapState(action.path);
            return {
                ...state,
                snaps: {
                    ...state.snaps,
                    [action.path]: { ...snapState, loading: true, error: null }
                }
            };
        }
        // Snap data loaded/updated successfully. Auto-select first valid board.
        case 'ASYNC_SUCCESS': {
            const snapState = getOrCreateSnapState(action.path);
            const boards = action.payload.boards;
            // Determine initial board selection: if none selected and boards exist, select first
            const boardsCount = boards?.length ?? 0;
            const initialIndex = snapState.currentBoardIndex;
            const nextIndex = initialIndex < 0 && boardsCount > 0
                ? 0
                : (boardsCount > 0 ? Math.min(initialIndex, boardsCount - 1) : initialIndex);
            const currentBoard = boardsCount > 0 && nextIndex >= 0 ? boards![nextIndex] || null : null;

            return {
                ...state,
                snaps: {
                    ...state.snaps,
                    [action.path]: {
                        ...snapState,
                        data: action.payload,
                        loading: false,
                        error: null,
                        lastUpdated: Date.now(),
                        currentBoardIndex: nextIndex,
                        currentBoard,
                    }
                }
            };
        }
        // Snap operation failed, record error message
        case 'ASYNC_ERROR': {
            const snapState = getOrCreateSnapState(action.path);
            return {
                ...state,
                snaps: {
                    ...state.snaps,
                    [action.path]: { ...snapState, loading: false, error: action.error }
                }
            };
        }
        // Close a Snap file with unsaved-changes confirmation
        case 'REMOVE':
            if (!state.snaps[action.path]) return state;

            const removeCurrent = action.path == state.currentSnapPath;
            const { [action.path]: removedQc, ...remainingQcs } = state.snaps;
            // Warn if Snap has unsaved changes
            if (removedQc?.data?.has_changed) {
                if (!window.confirm("Are you sure you want to close this quality control? Unsaved changes will be lost.")) {
                    return state;
                }
            }
            const remainingKeys = Object.keys(remainingQcs);
            // If closed Snap was active, switch to the most recently open one
            const newCurrent = removeCurrent ? remainingKeys.length > 0 ? remainingKeys[remainingKeys.length - 1] : null : state.currentSnapPath;
            return { ...state, snaps: remainingQcs, currentSnapPath: newCurrent };
        // Change active board within the current Snap. Auto-select and clamp.
        case 'SET_BOARD':
            if (!currentSnapState) return { ...state };
            // Deselect board
            if (action.boardIndex < 0) {
                return { ...state, snaps: { ...state.snaps, [state.currentSnapPath!]: { ...currentSnapState, currentBoardIndex: -1, currentBoard: null } } };
            }
            if (!currentSnapState.data || !currentSnapState.data.boards) return { ...state };
            // Ensure boardIndex doesn't exceed the number of available boards
            const idx = Math.min(action.boardIndex, currentSnapState.data.boards.length! - 1);
            return {
                ...state,
                snaps: { ...state.snaps, [state.currentSnapPath!]: { ...currentSnapState, currentBoardIndex: action.boardIndex, currentBoard: currentSnapState.data.boards[idx] || null } }
            };
        // Update GUI preferences (sidebar, sync, etc.)
        case 'SET_GUI_SETTINGS':
            return {
                ...state,
                guiSettings: {
                    ...state.guiSettings,
                    ...action.settings
                }
            }
        default:
            return state;
    }
}

/** Context for reading session state throughout the app */
const SnapSessionContext = createContext<SnapSessionState | undefined>(undefined);
/** Context for dispatching actions to the reducer */
export const SnapSessionDispatchContext = createContext<Dispatch<SnapSessionAction> | null>(null);

export function SnapSessionProvider(props: DefaultProps) {
    const [state, dispatch] = useReducer(qcReducer, defaultSnapSessionState);

    // Auto-create backend session on app mount
    useEffect(() => {
        const autoCreateSession = async () => {
            if (!state.session.data && !state.session.loading) {
                dispatch({ type: 'SESSION_START' });
                try {
                    const session = await SnapService.createSession();
                    dispatch({ type: 'SESSION_SUCCESS', payload: session });
                } catch (error) {
                    const message = error instanceof Error ? error.message : 'Session creation failed';
                    dispatch({ type: 'SESSION_ERROR', error: message });
                }
            }
        };
        autoCreateSession();
    }, [state.session.data, state.session.loading])

    // Prevent accidental data loss when leaving the page with unsaved changes
    useEffect(() => {
        const handleBeforeUnload = (e: BeforeUnloadEvent) => {
            // Warn user if any open Snap has unsaved changes
            const hasUnsaved = Object.values(state.snaps).some(snapState => snapState.data?.has_changed);
            if (hasUnsaved) {
                alert("You have unsaved changes. Are you sure you want to leave?");
                e.preventDefault();
                e.returnValue = ''; // Chrome requires returnValue to be set
            }
        };
        window.addEventListener('beforeunload', handleBeforeUnload);
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, [state.snaps]);

    return (
        <SnapSessionContext.Provider value={state}>
            <SnapSessionDispatchContext.Provider value={dispatch}>
                {props.children}
            </SnapSessionDispatchContext.Provider>
        </SnapSessionContext.Provider>
    );
}

/**
 * Hook to access action creators for managing Snaps.
 * All async operations (API calls) are wrapped with START/SUCCESS/ERROR dispatches.
 * 
 * Returns:
 * - openSnap(path): Load a Snap file
 * - setCurrentBoard(index): Switch active board
 * - updateRating(snapId, rating): Update a rating with optimistic update + rollback
 * - closeSnap(path): Close a Snap file
 * - toggleShowSidebar(): Toggle sidebar visibility
 * - toggleSyncBoards(): Toggle board sync setting
 * 
 * Must be used within SnapSessionProvider.
 */
export function useSnapSessionActions() {
    const dispatch = useContext(SnapSessionDispatchContext);
    const state = useContext(SnapSessionContext);

    // Guards to ensure context is available
    const requireDispatch = () => {
        if (!dispatch) throw new Error('useSnapSessionActions must be used within a SnapSessionProvider');
        return dispatch;
    };

    const requireState = () => {
        if (!state) throw new Error('useSnapSessionActions must be used within a SnapSessionProvider');
        return state;
    };

    const withAsync = useCallback(async (path: string, fn: () => Promise<SnapModel>) => {
        const safeDispatch = requireDispatch();

        // Signal operation start
        safeDispatch({ type: 'ASYNC_START', path });
        try {
            const result = await fn();
            safeDispatch({ type: 'ASYNC_SUCCESS', path, payload: result });
            return result;
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Unexpected error';
            // Signal failure and store error message
            safeDispatch({ type: 'ASYNC_ERROR', path, error: message });
            throw error;
        }
    }, [dispatch]);

    /**
     * Load a Snap file.
     * Sets it as current and fetches its data from the backend.
     */
    const openSnap = useCallback(async (path?: string) => {
        const safeDispatch = requireDispatch();
        const safeState = requireState();
        if (!path) { throw new Error('Path is required to open a Snap'); }
        const sid = safeState.session.data?.id || "";

        safeDispatch({ type: 'SET_CURRENT', path });
        await withAsync(path, () => SnapService.openSnap(sid, path));
        setCurrentBoard(0);
    }, [dispatch, state, withAsync]);

    /**
     * Switch the active board within the current Snap.
     * Synchronous action (no API call).
     */
    const setCurrentBoard = useCallback((boardIndex: number) => {
        const safeDispatch = requireDispatch();
        safeDispatch({ type: 'SET_BOARD', boardIndex });
    }, [dispatch]);

    /**
     * Update a rating value with optimistic update.
     * Immediately updates local state, then syncs with backend.
     * On failure, rolls back the local change and stores error.
     */
    const updateRating = useCallback(async (snapId: string, rating: any) => {
        const safeDispatch = requireDispatch();
        const safeState = requireState();
        const path = safeState.currentSnapPath;
        if (!path) return;

        const sid = safeState.session.data?.id || "";
        const currentSnap = safeState.snaps[path]?.data;
        if (!currentSnap) return;

        // Optimistic update: update rating locally before API confirms
        const updatedRatings = currentSnap.ratings?.map(r => r.id === rating.id ? rating : r) || [];
        const optimisticSnap = { ...currentSnap, ratings: updatedRatings };

        safeDispatch({ type: 'ASYNC_START', path });
        // Immediately show the updated rating
        safeDispatch({ type: 'ASYNC_SUCCESS', path, payload: optimisticSnap });

        try {
            await SnapService.updateRating(sid, snapId, rating.id, rating.value);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to update note';
            // Rollback: restore the previous state on API failure
            safeDispatch({ type: 'ASYNC_SUCCESS', path, payload: currentSnap });
            safeDispatch({ type: 'ASYNC_ERROR', path, error: message });
        }
    }, [dispatch, state]);

    /**
     * Save the current Snap to its original file path.
     * Syncs all changes with the backend.
     */
    const saveSnap = useCallback(async (snapId: string) => {
        const safeState = requireState();
        const path = safeState.currentSnapPath;
        if (!path) return;

        const sid = safeState.session.data?.id || "";
        await withAsync(path, () => SnapService.saveSnap(sid, snapId));
    }, [dispatch, state, withAsync]);

    /**
     * Save the current Snap to a new file path.
     * Updates the snap path after successful save.
     */
    const saveSnapAs = useCallback(async (snapId: string, newPath: string) => {
        const safeState = requireState();
        const path = safeState.currentSnapPath;
        if (!path) return;

        const sid = safeState.session.data?.id || "";
        await withAsync(path, () => SnapService.saveSnapAs(sid, snapId, newPath));
    }, [dispatch, state, withAsync]);

    const closeSnap = useCallback((path: string) => {
        const safeDispatch = requireDispatch();
        safeDispatch({ type: 'REMOVE', path });
    }, [dispatch]);

    /**
     * Toggle sidebar visibility.
     */
    const toggleShowSidebar = useCallback(() => {
        const safeDispatch = requireDispatch();
        safeDispatch({ type: 'SET_GUI_SETTINGS', settings: { showSidebar: !state?.guiSettings.showSidebar } });
    }, [dispatch, state?.guiSettings.showSidebar]);

    /**
     * Toggle board sync setting (sync boards across multiple Snaps).
     */
    const toggleSyncBoards = useCallback(() => {
        const safeDispatch = requireDispatch();
        safeDispatch({ type: 'SET_GUI_SETTINGS', settings: { syncBoards: !state?.guiSettings.syncBoards } });
    }, [dispatch, state?.guiSettings.syncBoards]);

    return {
        openSnap,
        setCurrentBoard,
        updateRating,
        saveSnap,
        saveSnapAs,
        closeSnap,
        toggleShowSidebar,
        toggleSyncBoards
    };
}

/**
 * Primary hook for consuming the session state and actions.
 * Combines state and action creators for convenient access.
 * 
 * Returns the current session state merged with all available actions.
 * Also provides convenience methods like closeCurrentSnap().
 * 
 * Example:
 * ```tsx
 * const { snap, session, currentBoard, openSnap, updateRating } = useSnapSession();
 * ```
 * 
 * Must be used within SnapSessionProvider.
 */
export function useSnapSession() {
    const state = useContext(SnapSessionContext);
    const actions = useSnapSessionActions();

    if (!state) {
        throw new Error('useSnapSession must be used within a SnapSessionProvider');
    }

    const currentSnapState = state.currentSnapPath ? state.snaps[state.currentSnapPath] : undefined;

    /**
     * Convenience method: close the currently active Snap without needing to pass the path.
     */
    const closeCurrentSnap = () => {
        if (state.currentSnapPath) {
            actions.closeSnap(state.currentSnapPath);
        }
    }


    return {
        // Full state
        ...state,
        // All action creators
        ...actions,
        // Current Snap state fields (loading, error, currentBoardIndex, currentBoard)
        ...currentSnapState,
        // Session data (for backward compatibility and easy access)
        session: state.session.data,
        // Full session state (with loading/error) if needed
        sessionState: state.session,
        // Current Snap data (alias for currentSnapState?.data)
        snap: currentSnapState?.data ?? null,
        // GUI settings
        ...state.guiSettings,
        // Convenience action
        closeCurrentSnap
    };
}