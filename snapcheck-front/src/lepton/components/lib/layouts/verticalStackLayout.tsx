import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import "./verticalStackLayout.css";
import { CloseFullscreen, OpenInFull } from "@mui/icons-material";

// Constants for layout sizing
const HEADER_MIN_HEIGHT = 36; // Minimum height of section headers in pixels
const DEFAULT_MIN_CONTENT_HEIGHT = 30; // Default minimum content area height when not specified
const RESIZER_THICKNESS = 6; // Height of the resizable separator between sections in pixels

/**
 * Represents a single collapsible section in the stack layout.
 */
type StackSection = {
    /** Unique identifier for the section */
    id: string;
    /** Title displayed in the section header */
    title: React.ReactNode;
    /** Content rendered inside the scrollable area */
    content: React.ReactNode;
    /**
     * Relative weight used when distributing the extra vertical space on init.
     * Sections keep at least their header and minimal content height.
     */
    initialSize?: number;
    /**
     * Minimal content height in pixels (header height is guaranteed separately).
     */
    minContentHeight?: number;
    /**
     * Optional actions displayed in the header, placed before the maximize toggle.
     */
    actions?: React.ReactNode;
};

/**
 * Configuration props for the VerticalStackLayout component.
 */
type VerticalStackLayoutProps = {
    /** Array of sections to display in the stack */
    sections: StackSection[];
    /**
     * Height of the whole stack container. Defaults to 100% of the parent.
     */
    height?: number | string;
    /**
     * Minimal content height applied to all sections when not overridden per section.
     */
    minContentHeight?: number;
    /** Additional CSS class names to apply to the container */
    className?: string;
};

/**
 * Converts a size value to a valid CSS size string.
 * @param value - A number (converted to pixels), string (used as-is), or undefined (defaults to 100%)
 * @returns A CSS-compatible size string
 */
const toCssSize = (value: number | string | undefined) => {
    if (value === undefined) return "100%";
    return typeof value === "number" ? `${value}px` : value;
};

/**
 * Normalizes pixel heights into proportional values (0 to 1 range).
 * Used internally to maintain section proportions during height changes.
 * @param pixels - Array of pixel heights
 * @param total - Total available space in pixels
 * @param fallbackCount - Number of sections to fall back to if needed
 * @returns Array of normalized proportional heights
 */
const normalizeHeightsFromPixels = (
    pixels: number[],
    total: number,
    fallbackCount: number
): number[] => {
    const count = fallbackCount || pixels.length || 1;
    if (total <= 0 || pixels.length === 0) {
        return Array.from({ length: count }, () => 1 / count);
    }

    const sum = pixels.reduce((acc, value) => acc + value, 0);
    if (sum === 0) {
        return Array.from({ length: count }, () => 1 / count);
    }
    return pixels.map((value) => value / sum);
};

/**
 * VerticalStackLayout: A resizable, multi-section sidebar component.
 * 
 * Features:
 * - Drag handles between sections to resize them
 * - Maximize/restore sections with a header button
 * - Automatic content scrolling when it exceeds available space
 * - Each section maintains minimum height constraints
 * - Responsive to container resize
 */
const VerticalStackLayout: React.FC<VerticalStackLayoutProps> = ({
    sections,
    height,
    minContentHeight = DEFAULT_MIN_CONTENT_HEIGHT,
    className = "",
}) => {
    // Refs
    const containerRef = useRef<HTMLDivElement | null>(null);
    const lastSectionKey = useRef<string>(""); // Track section configuration changes

    // State: Container and section sizing
    const [containerHeight, setContainerHeight] = useState<number>(0); // Current container height in pixels
    const [heights, setHeights] = useState<number[]>([]); // Normalized heights (0-1) for each section

    // State: Resize interaction
    const [dragState, setDragState] = useState<{
        index: number; // Index of the resizer being dragged
        startY: number; // Initial Y position when drag started
        startHeights: number[]; // Heights at drag start
    } | null>(null);

    // State: Maximize/minimize
    const [maximizedId, setMaximizedId] = useState<string | null>(null); // ID of currently maximized section
    const [heightsBeforeMax, setHeightsBeforeMax] = useState<number[] | null>(null); // Heights before maximization

    // Computed: Space taken by resizers
    const resizersHeight = useMemo(
        () => RESIZER_THICKNESS * Math.max(sections.length - 1, 0),
        [sections.length]
    );

    // Computed: Vertical space available for sections (total - resizers)
    const availableHeight = useMemo(() => {
        if (!sections.length) return 0;
        return Math.max(containerHeight - resizersHeight, 0);
    }, [containerHeight, sections.length, resizersHeight]);

    /**
     * Gets the minimum total height for a section (header + minimum content).
     */
    const getMinHeightPx = useCallback(
        (section: StackSection) => HEADER_MIN_HEIGHT + (section.minContentHeight ?? minContentHeight),
        [minContentHeight]
    );

    // Computed: String key representing current section configuration
    const sectionKey = useMemo(() => sections.map((s) => s.id).join("|"), [sections]);

    /**
     * Calculates initial normalized heights for all sections based on:
     * 1. Minimum height constraints
     * 2. Available space after minimums are satisfied
     * 3. Initial size weights for distribution
     */
    const buildInitialHeights = useCallback(() => {
        if (!sections.length) return [];
        if (availableHeight <= 0) {
            return Array.from({ length: sections.length }, () => 1 / sections.length);
        }

        // Calculate minimum heights for each section
        const minHeights = sections.map((section) => getMinHeightPx(section));
        const minTotal = minHeights.reduce((acc, value) => acc + value, 0);
        const extra = Math.max(availableHeight - minTotal, 0);

        // Distribute extra space according to initialSize weights
        const weights = sections.map((section) => section.initialSize ?? 1);
        const totalWeight = weights.reduce((acc, value) => acc + value, 0) || sections.length;

        const pixels = sections.map((section, index) => {
            const weightRatio = weights[index] / totalWeight;
            return minHeights[index] + extra * weightRatio;
        });

        return normalizeHeightsFromPixels(pixels, availableHeight, sections.length);
    }, [sections, availableHeight, getMinHeightPx]);

    /**
     * Calculates heights when one section is maximized.
     * The target section gets all extra space, others get only their minimum height.
     * @param targetId - ID of the section to maximize
     */
    const computeMaximizedHeights = useCallback(
        (targetId: string) => {
            if (!sections.length) return [];
            if (availableHeight <= 0) {
                return Array.from({ length: sections.length }, () => 1 / sections.length);
            }
            const minHeights = sections.map((section) => getMinHeightPx(section));
            const minTotal = minHeights.reduce((acc, value) => acc + value, 0);
            const extra = Math.max(availableHeight - minTotal, 0);

            // Target section gets minimum + extra space; others get only minimum
            const pixels = sections.map((section, index) =>
                section.id === targetId ? minHeights[index] + extra : minHeights[index]
            );

            return normalizeHeightsFromPixels(pixels, availableHeight, sections.length);
        },
        [availableHeight, getMinHeightPx, sections]
    );

    // Effect: Monitor container resize changes
    useEffect(() => {
        const node = containerRef.current;
        if (!node || typeof ResizeObserver === "undefined") return;

        setContainerHeight(node.getBoundingClientRect().height);

        const observer = new ResizeObserver((entries) => {
            const entry = entries[0];
            if (entry) {
                // Only update if height changed significantly (avoid floating point micro-changes)
                setContainerHeight(prev => {
                    const newHeight = Math.round(entry.contentRect.height);
                    return Math.abs(prev - newHeight) >= 1 ? newHeight : prev;
                });
            }
        });

        observer.observe(node);
        return () => observer.disconnect();
    }, []);

    // Effect: Update heights when sections or available space changes
    // Recalculates only if section configuration has actually changed
    useEffect(() => {
        if (!sections.length || availableHeight <= 0) return;
        const hasSameSections = lastSectionKey.current === sectionKey;
        const hasValidHeights = heights.length === sections.length;
        if (hasSameSections && hasValidHeights) return;

        const newHeights = buildInitialHeights();
        // Only update if heights actually changed (not just array reference)
        setHeights(prev => {
            if (prev.length === newHeights.length && prev.every((h, i) => Math.abs(h - newHeights[i]) < 0.001)) {
                return prev;
            }
            return newHeights;
        });
        setMaximizedId(null);
        setHeightsBeforeMax(null);
        lastSectionKey.current = sectionKey;
    }, [sectionKey, sections.length, availableHeight, buildInitialHeights]);

    /**
     * Initiates resize operation when user presses down on a resizer.
     * Stores the current state to enable proportional dragging.
     */
    const startResize = useCallback(
        (index: number, event: React.MouseEvent<HTMLDivElement>) => {
            event.preventDefault();
            if (availableHeight <= 0) return;
            const baseHeights = heights.length === sections.length ? heights : buildInitialHeights();
            setDragState({ index, startY: event.clientY, startHeights: baseHeights });
        },
        [availableHeight, heights, sections.length, buildInitialHeights]
    );

    // Effect: Handle mouse drag for resizing sections
    // Dragging a resizer adjusts the heights of the two adjacent sections
    useEffect(() => {
        if (!dragState) return;

        const handleMove = (event: MouseEvent) => {
            if (availableHeight <= 0) return;

            // Calculate vertical movement since drag started
            const delta = event.clientY - dragState.startY;
            const startPixels = dragState.startHeights.map((value) => value * availableHeight);
            
            // The two adjacent sections share a fixed total height
            const totalPair = startPixels[dragState.index] + startPixels[dragState.index + 1];

            // Calculate minimum heights respecting constraints
            const minUpper = Math.min(getMinHeightPx(sections[dragState.index]), totalPair);
            const minLower = Math.min(getMinHeightPx(sections[dragState.index + 1]), totalPair - minUpper);

            // Apply drag and clamp within valid bounds
            const rawUpper = startPixels[dragState.index] + delta;
            const upperBound = totalPair - minLower;
            const clampedUpper = Math.min(Math.max(rawUpper, minUpper), upperBound);
            const clampedLower = totalPair - clampedUpper;

            // Update only the two affected sections
            const nextPixels = [...startPixels];
            nextPixels[dragState.index] = clampedUpper;
            nextPixels[dragState.index + 1] = clampedLower;

            setHeights(normalizeHeightsFromPixels(nextPixels, availableHeight, sections.length));
            // Exit maximize mode when resizing
            setMaximizedId(null);
            setHeightsBeforeMax(null);
        };

        const stopDragging = () => setDragState(null);

        window.addEventListener("mousemove", handleMove);
        window.addEventListener("mouseup", stopDragging);

        return () => {
            window.removeEventListener("mousemove", handleMove);
            window.removeEventListener("mouseup", stopDragging);
        };
    }, [dragState, availableHeight, sections, getMinHeightPx]);

    /**
     * Toggles maximize state for a section.
     * Clicking maximize expands that section to consume all extra space.
     * Clicking again restores the previous layout.
     */
    const toggleMaximize = useCallback(
        (targetId: string) => {
            if (!sections.length) return;
            // Restore previous layout if clicking the same maximized section
            if (maximizedId === targetId && heightsBeforeMax) {
                setHeights(heightsBeforeMax);
                setMaximizedId(null);
                setHeightsBeforeMax(null);
                return;
            }

            // Maximize the target section
            const baseHeights = heights.length === sections.length ? heights : buildInitialHeights();
            setHeightsBeforeMax(baseHeights);
            setHeights(computeMaximizedHeights(targetId));
            setMaximizedId(targetId);
        },
        [sections.length, maximizedId, heightsBeforeMax, heights, buildInitialHeights, computeMaximizedHeights]
    );

    // Computed: Ensure heights are valid, fall back to equal distribution if needed
    const effectiveHeights = useMemo(() => {
        if (heights.length === sections.length) return heights;
        return normalizeHeightsFromPixels([], availableHeight, sections.length);
    }, [heights, sections.length, availableHeight]);

    // Computed: Convert normalized heights to actual pixel values for rendering
    const sectionHeightsPx = useMemo(() => {
        if (availableHeight <= 0) return sections.map(() => 0);
        return effectiveHeights.map((value) => value * availableHeight);
    }, [availableHeight, effectiveHeights, sections]);

    return (
        <div
            ref={containerRef}
            className={`vertical-stack-layout ${dragState ? "is-dragging" : ""} ${className}`.trim()}
            style={{ height: toCssSize(height) }}
        >
            {/* Render each section with its header and scrollable content */}
            {sections.map((section, index) => (
                <React.Fragment key={section.id}>
                    <div
                        className={`vsl-section ${maximizedId === section.id ? "vsl-section--maximized" : ""}`.trim()}
                        style={availableHeight > 0 ? { height: `${sectionHeightsPx[index]}px` } : undefined}
                    >
                        {/* Section header with title and action buttons */}
                        <div className="vsl-header">
                            <div className="vsl-title">{section.title}</div>
                            <div className="vsl-actions">
                                {/* Custom actions provided by the section */}
                                {section.actions}
                                {/* Maximize/restore button */}
                                <button
                                    type="button"
                                    className="vsl-icon-button"
                                    aria-label={
                                        maximizedId === section.id
                                            ? "Réduire la section"
                                            : "Maximiser la section"
                                    }
                                    onClick={() => toggleMaximize(section.id)}
                                >
                                    {maximizedId === section.id ? (
                                        <CloseFullscreen fontSize="inherit" />
                                    ) : (
                                        <OpenInFull fontSize="inherit" />
                                    )}
                                </button>
                            </div>
                        </div>
                        {/* Scrollable content area */}
                        <div
                            className="vsl-content"
                            style={{ 
                                flex: 1,
                                overflow: "auto"
                            }}
                        >
                            {section.content}
                        </div>
                    </div>
                    {/* Resizer between sections (not after the last section) */}
                    {index < sections.length - 1 && (
                        <div
                            className={`vsl-resizer ${dragState?.index === index ? "dragging" : ""}`.trim()}
                            onMouseDown={(event) => startResize(index, event)}
                        />
                    )}
                </React.Fragment>
            ))}
        </div>
    );
};

export default VerticalStackLayout;
export type { StackSection };


