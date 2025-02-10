declare module 'newrelic' {
    export function getLicenseKey(): string | undefined;
    export function setLicenseKey(key: string): void;
    export function setAppName(name: string): void;
    export function recordMetric(name: string, value: number): void;
    export function recordCustomEvent(eventType: string, attributes: Record<string, any>): void;
    export function noticeError(error: Error, customAttributes?: Record<string, any>): void;
    export function addCustomAttribute(key: string, value: any): void;
    export function addCustomAttributes(attributes: Record<string, any>): void;
    export function getBrowserTimingHeader(): string;
    export function setTransactionName(name: string): void;
    export function endTransaction(): void;
    export function startSegment(name: string, record?: boolean): any;
    export function startWebTransaction(url: string, handle: () => void): void;
    export function endWebTransaction(): void;
    export function createTracer(name: string, callback: (...args: any[]) => any): (...args: any[]) => any;
    export function createWebTransaction(url: string, handle: () => void): void;
    export function startBackgroundTransaction(name: string, group: string, handle: () => void): void;
    export function endBackgroundTransaction(): void;
} 