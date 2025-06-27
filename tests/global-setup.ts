/**
 * Global setup for E2E tests
 * Runs once before all tests
 */

import { FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global test setup...');

  // Ensure required directories exist
  const dirs = ['logs', 'saves', 'test-results'];
  for (const dir of dirs) {
    const dirPath = path.resolve(dir);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
      console.log(`✅ Created directory: ${dir}`);
    }
  }

  // Create a test environment file
  const envPath = path.resolve('.env.test');
  if (!fs.existsSync(envPath)) {
    const testEnv = `
# Test Environment Configuration
FLASK_ENV=testing
DEBUG_MODE=False
PORT=5001
LOG_LEVEL=DEBUG
DEEPSEEK_API_KEY=test-key
    `.trim();
    
    fs.writeFileSync(envPath, testEnv);
    console.log('✅ Created test environment file');
  }

  // Store start time for performance tracking
  (global as any).__TEST_START_TIME__ = Date.now();

  console.log('✅ Global setup completed');
  console.log(`📍 Base URL: ${config.projects[0].use?.baseURL}`);
  console.log(`⏱️  Test timeout: ${config.timeout}ms`);
  
  return async () => {
    // This runs after all tests
    console.log('🏁 All tests completed');
  };
}

export default globalSetup;
