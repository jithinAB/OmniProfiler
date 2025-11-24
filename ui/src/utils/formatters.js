/**
 * Format a number with appropriate decimal precision.
 * For very small numbers, show more decimals.
 */
export const formatNumber = (value, unit = '') => {
    if (value === null || value === undefined || isNaN(value)) {
        return 'N/A';
    }

    const num = Number(value);

    if (num === 0) {
        return `0${unit}`;
    }

    // For very small numbers, use scientific notation or more decimals
    if (Math.abs(num) < 0.000001) {
        return `${num.toExponential(2)}${unit}`;
    } else if (Math.abs(num) < 0.001) {
        return `${num.toFixed(6)}${unit}`;
    } else if (Math.abs(num) < 0.01) {
        return `${num.toFixed(5)}${unit}`;
    } else if (Math.abs(num) < 1) {
        return `${num.toFixed(4)}${unit}`;
    } else if (Math.abs(num) < 100) {
        return `${num.toFixed(3)}${unit}`;
    } else {
        return `${num.toFixed(2)}${unit}`;
    }
};

/**
 * Format bytes to human-readable format
 */
export const formatBytes = (bytes) => {
    if (bytes === null || bytes === undefined || isNaN(bytes)) {
        return 'N/A';
    }

    const num = Number(bytes);

    if (num === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(num) / Math.log(k));

    return `${(num / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
};

/**
 * Format time with appropriate unit and precision
 */
export const formatTime = (seconds) => {
    if (seconds === null || seconds === undefined || isNaN(seconds)) {
        return 'N/A';
    }

    const num = Number(seconds);

    if (num === 0) return '0s';

    if (num < 0.000001) {
        return `${(num * 1000000000).toFixed(2)} ns`;
    } else if (num < 0.001) {
        return `${(num * 1000000).toFixed(2)} μs`;
    } else if (num < 1) {
        return `${(num * 1000).toFixed(2)} ms`;
    } else if (num < 60) {
        return `${num.toFixed(3)} s`;
    } else {
        const minutes = Math.floor(num / 60);
        const secs = num % 60;
        return `${minutes}m ${secs.toFixed(2)}s`;
    }
};
