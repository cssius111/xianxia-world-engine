/**
 * Log Helper utilities for E2E tests
 * Provides functions to read, write, and manage log files
 */

import * as fs from 'fs';
import * as path from 'path';
import * as zlib from 'zlib';

export class LogHelper {
  private logDir: string;

  constructor(logDir: string = 'logs') {
    this.logDir = path.resolve(logDir);
  }

  /**
   * Read the content of a log file
   */
  async readLogFile(filename: string): Promise<string> {
    const filePath = path.join(this.logDir, filename);
    return fs.promises.readFile(filePath, 'utf-8');
  }

  /**
   * Check if a log file exists
   */
  async logExists(filename: string): Promise<boolean> {
    const filePath = path.join(this.logDir, filename);
    try {
      await fs.promises.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get the size of a log file in bytes
   */
  async getLogSize(filename: string): Promise<number> {
    const filePath = path.join(this.logDir, filename);
    const stats = await fs.promises.stat(filePath);
    return stats.size;
  }

  /**
   * Clear/empty a log file
   */
  async clearLog(filename: string): Promise<void> {
    const filePath = path.join(this.logDir, filename);
    await fs.promises.writeFile(filePath, '');
  }

  /**
   * Write data to a log file (append mode)
   */
  async writeToLog(filename: string, data: string): Promise<void> {
    const filePath = path.join(this.logDir, filename);
    await fs.promises.appendFile(filePath, data);
  }

  /**
   * Check if a gzipped log file exists
   */
  async gzipLogExists(filename: string): Promise<boolean> {
    return this.logExists(filename + '.gz');
  }

  /**
   * Read the last N lines from a log file
   */
  async readLastLines(filename: string, n: number): Promise<string[]> {
    const content = await this.readLogFile(filename);
    const lines = content.trim().split('\n');
    return lines.slice(-n);
  }

  /**
   * Parse JSON log entries from the last N lines
   */
  async parseLastJsonEntries(filename: string, n: number): Promise<any[]> {
    const lines = await this.readLastLines(filename, n);
    return lines.map(line => {
      try {
        return JSON.parse(line);
      } catch (e) {
        console.error(`Failed to parse log line: ${line}`);
        return null;
      }
    }).filter(entry => entry !== null);
  }

  /**
   * Wait for a log file to be created with timeout
   */
  async waitForLogFile(filename: string, timeout: number = 5000): Promise<boolean> {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
      if (await this.logExists(filename)) {
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return false;
  }

  /**
   * Get all log files in the log directory
   */
  async getAllLogFiles(): Promise<string[]> {
    const files = await fs.promises.readdir(this.logDir);
    return files.filter(file => file.endsWith('.log') || file.endsWith('.log.gz'));
  }

  /**
   * Create the log directory if it doesn't exist
   */
  async ensureLogDir(): Promise<void> {
    await fs.promises.mkdir(this.logDir, { recursive: true });
  }

  /**
   * Delete a log file
   */
  async deleteLog(filename: string): Promise<void> {
    const filePath = path.join(this.logDir, filename);
    try {
      await fs.promises.unlink(filePath);
    } catch (e) {
      // Ignore if file doesn't exist
    }
  }

  /**
   * Get the age of a log file in milliseconds
   */
  async getLogAge(filename: string): Promise<number> {
    const filePath = path.join(this.logDir, filename);
    const stats = await fs.promises.stat(filePath);
    return Date.now() - stats.mtimeMs;
  }
}
