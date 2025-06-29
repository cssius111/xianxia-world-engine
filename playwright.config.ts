import { defineConfig, devices } from '@playwright/test';

/**
 * Xianxia World Engine E2E Test Configuration
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',
  
  /* Ignore Cypress test files */
  testIgnore: ['**/e2e/*.spec.js', '**/xiuxian-game.spec.js'],
  
  /* Maximum time one test can run for */
  timeout: 90_000, // 90 seconds as requested
  
  /* Run tests in files in parallel */
  fullyParallel: false,
  
  /* Fail the build on CI if you accidentally left test.only in the source code */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 1,
  
  /* Opt out of parallel tests on CI */
  workers: process.env.CI ? 1 : 1,
  
  /* Reporter to use */
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['list'],
    ['json', { outputFile: 'test-results/results.json' }]
  ],
  
  /* Shared settings for all the projects below */
  use: {
    /* Base URL to use in actions like `await page.goto('/')` */
    baseURL: process.env.BASE_URL || 'http://localhost:5001',

    /* Collect trace when retrying the failed test */
    trace: 'on-first-retry',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Record video on failure - as requested */
    video: 'retain-on-failure',
    
    /* Timeout for each action */
    actionTimeout: 15_000,
    
    /* Timeout for navigation */
    navigationTimeout: 30_000,
    
    /* Accept downloads */
    acceptDownloads: true,
    
    /* Emulate locale */
    locale: 'zh-CN',
    
    /* Timezone */
    timezoneId: 'Asia/Shanghai',
  },

  /* Configure projects for major browsers - ALL ENABLED for comprehensive testing */
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Optimized settings for Xianxia game testing
        viewport: { width: 1280, height: 720 },
        launchOptions: {
          headless: process.env.CI ? true : false, // Headless in CI, headed locally
          slowMo: process.env.CI ? 0 : 100, // Slow down actions for better visibility
          args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--disable-features=IsolateOrigins',
            '--disable-site-isolation-trials'
          ]
        },
        // Custom context options
        contextOptions: {
          // Save auth state
          storageState: {
            cookies: [],
            origins: []
          },
          // Ignore HTTPS errors
          ignoreHTTPSErrors: true,
          // Permissions
          permissions: ['geolocation', 'notifications'],
        }
      },
    },

    // Firefox configuration for cross-browser testing
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1280, height: 720 },
        launchOptions: {
          headless: process.env.CI ? true : false,
          slowMo: process.env.CI ? 0 : 100,
        }
      },
    },

    // Safari/WebKit configuration
    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1280, height: 720 },
        launchOptions: {
          headless: process.env.CI ? true : false,
          slowMo: process.env.CI ? 0 : 100,
        }
      },
    },

    // Mobile Chrome testing
    {
      name: 'mobile-chrome',
      use: { 
        ...devices['Pixel 5'],
        launchOptions: {
          headless: process.env.CI ? true : false,
        }
      },
    },

    // Mobile Safari testing
    {
      name: 'mobile-safari',
      use: { 
        ...devices['iPhone 12'],
        launchOptions: {
          headless: process.env.CI ? true : false,
        }
      },
    },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    // Use the project's run script to start the server
    command: process.env.CI ? 'python run.py' : 'python run.py',
    port: 5001,
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
    // Wait for the server to be ready
    stdout: 'pipe',
    stderr: 'pipe',
    env: {
      FLASK_ENV: 'development',
      FLASK_DEBUG: 'False', // Disable debug for testing
      PORT: '5001',
      ENABLE_E2E_API: 'true', // Enable E2E test routes
    },
  },

  /* Global setup */
  globalSetup: require.resolve('./tests/global-setup.ts'),
  
  /* Global teardown */
  globalTeardown: require.resolve('./tests/global-teardown.ts'),

  /* Output folder for test artifacts */
  outputDir: 'test-results/',

  /* Preserve test output */
  preserveOutput: 'failures-only',

  /* Quiet mode */
  quiet: false,

  /* Update snapshots */
  updateSnapshots: 'missing',

  /* Maximum parallel tests */
  maxFailures: process.env.CI ? 10 : 0,
});
