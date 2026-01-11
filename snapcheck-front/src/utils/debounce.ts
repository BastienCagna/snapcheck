/**
 * Debounce utility for delaying function execution until after a specified delay.
 * Useful for optimizing frequent API calls (e.g., text input changes).
 * 
 * @param func - The function to debounce
 * @param delay - Delay in milliseconds before executing the function
 * @returns A debounced version of the function with a cancel method
 * 
 * @example
 * const saveField = debounce((value: string) => {
 *   api.updateField(value);
 * }, 500);
 * 
 * // Call multiple times - only the last call will execute after 500ms
 * saveField("a");
 * saveField("ab");
 * saveField("abc"); // Only this will execute
 * 
 * // Cancel pending execution
 * saveField.cancel();
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number = 500
): T & { cancel: () => void } {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  const debounced = ((...args: Parameters<T>) => {
    // Clear existing timeout
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }

    // Set new timeout
    timeoutId = setTimeout(() => {
      func(...args);
      timeoutId = null;
    }, delay);
  }) as T & { cancel: () => void };

  // Add cancel method to clear pending execution
  debounced.cancel = () => {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };

  return debounced;
}


/**
 * Hook-friendly debounce using useCallback and useRef.
 * Use this in React components to maintain stable debounced function identity.
 * 
 * @example
 * import { useCallback, useRef } from 'react';
 * import { createDebouncedCallback } from './debounce';
 * 
 * function MyComponent() {
 *   const debouncedSave = useRef(
 *     createDebouncedCallback((value: string) => {
 *       api.save(value);
 *     }, 500)
 *   ).current;
 *   
 *   useEffect(() => {
 *     return () => debouncedSave.cancel(); // Cleanup on unmount
 *   }, []);
 * }
 */
export function createDebouncedCallback<T extends (...args: any[]) => any>(
  func: T,
  delay: number = 500
): T & { cancel: () => void } {
  return debounce(func, delay);
}
