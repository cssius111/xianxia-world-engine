/**
 * Global teardown for E2E tests
 * Runs once after all tests
 */

import { FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global test teardown...');

  // Calculate total test duration
  const startTime = (global as any).__TEST_START_TIME__;
  if (startTime) {
    const duration = Date.now() - startTime;
    const minutes = Math.floor(duration / 60000);
    const seconds = Math.floor((duration % 60000) / 1000);
    console.log(`⏱️  Total test duration: ${minutes}m ${seconds}s`);
  }

  // Clean up test artifacts if requested
  if (process.env.CLEANUP_AFTER_TESTS === 'true') {
    console.log('🗑️  Cleaning up test artifacts...');
    
    // Clean test logs
    const testLogs = ['app.log', 'app.log.1.gz', 'state_transitions.log'];
    for (const logFile of testLogs) {
      const logPath = path.resolve('logs', logFile);
      if (fs.existsSync(logPath)) {
        fs.unlinkSync(logPath);
        console.log(`  ✅ Deleted ${logFile}`);
      }
    }
    
    // Clean test saves
    const savesDir = path.resolve('saves');
    if (fs.existsSync(savesDir)) {
      const saveFiles = fs.readdirSync(savesDir);
      for (const file of saveFiles) {
        if (file.includes('test') || file.includes('测试')) {
          fs.unlinkSync(path.join(savesDir, file));
          console.log(`  ✅ Deleted test save: ${file}`);
        }
      }
    }
  }

  // Generate test summary
  const resultsPath = path.resolve('test-results', 'results.json');
  if (fs.existsSync(resultsPath)) {
    try {
      const results = JSON.parse(fs.readFileSync(resultsPath, 'utf-8'));
      console.log('\n📊 Test Summary:');
      console.log(`  Total tests: ${results.stats?.total || 0}`);
      console.log(`  Passed: ${results.stats?.passed || 0}`);
      console.log(`  Failed: ${results.stats?.failed || 0}`);
      console.log(`  Skipped: ${results.stats?.skipped || 0}`);
    } catch (e) {
      // Results file might have different format
    }
  }

  // Save performance metrics
  const metricsPath = path.resolve('test-results', 'performance-metrics.json');
  const metrics = {
    timestamp: new Date().toISOString(),
    duration: (global as any).__TEST_START_TIME__ ? Date.now() - (global as any).__TEST_START_TIME__ : 0,
    environment: {
      node_version: process.version,
      platform: process.platform,
      ci: !!process.env.CI
    }
  };
  
  fs.writeFileSync(metricsPath, JSON.stringify(metrics, null, 2));
  console.log('📈 Performance metrics saved');

  console.log('✅ Global teardown completed');
}

export default globalTeardown;
