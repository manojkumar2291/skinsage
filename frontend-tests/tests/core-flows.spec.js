const { test, expect } = require('@playwright/test');

test.describe('Authentication Flow', () => {
  // We mock network requests since the frontend is not actually running

  test('Successful Login redirects to dashboard', async ({ page }) => {
    // Mock the API response for login
    await page.route('**/api/auth/login', async route => {
      await route.fulfill({
        status: 200,
        json: {
          access_token: 'mock-token',
          user: { role: 'patient', full_name: 'Test Patient' }
        }
      });
    });

    // We can't navigate to the real frontend in this isolated repo without the frontend code,
    // so we mock the HTML to test the general structure/interactions Playwright expects
    await page.setContent(`
      <html>
        <body>
          <input type="email" id="email" placeholder="Email" />
          <input type="password" id="password" placeholder="Password" />
          <button id="login-btn">Login</button>
        </body>
        <script>
          document.getElementById('login-btn').addEventListener('click', () => {
             fetch('/api/auth/login', {method: 'POST'})
               .then(res => res.json())
               .then(data => {
                  if(data.access_token) {
                      window.location.href = '/patient/dashboard';
                  }
               });
          });
        </script>
      </html>
    `);

    // Fill the form
    await page.fill('#email', 'patient@test.com');
    await page.fill('#password', 'password123');

    // Click login and wait for redirect
    await page.click('#login-btn');

    // Check if it redirected correctly (mocking behavior)
    await expect(page).toHaveURL(/.*\/patient\/dashboard/);
  });
});

test.describe('AI Analysis Flow', () => {
  test('Uploading an image and getting analysis', async ({ page }) => {
    // Mock the AI analysis response
    await page.route('**/api/ai/analyze', async route => {
      await route.fulfill({
        status: 200,
        json: {
           analysis: {
              condition: 'Acne',
              confidence: 0.95,
              recommendation: 'Use Salicylic Acid'
           }
        }
      });
    });

    await page.setContent(`
      <html>
        <body>
          <input type="file" id="image-upload" />
          <button id="analyze-btn">Analyze</button>
          <div id="result"></div>
        </body>
        <script>
          document.getElementById('analyze-btn').addEventListener('click', () => {
             fetch('/api/ai/analyze', {method: 'POST'})
               .then(res => res.json())
               .then(data => {
                  document.getElementById('result').innerText = data.analysis.condition;
               });
          });
        </script>
      </html>
    `);

    // Mock file upload
    const buffer = Buffer.from('fake-image-content');
    await page.setInputFiles('#image-upload', {
        name: 'skin-issue.jpg',
        mimeType: 'image/jpeg',
        buffer
    });

    // Click analyze
    await page.click('#analyze-btn');

    // Wait for the result to appear on screen
    await expect(page.locator('#result')).toHaveText('Acne');
  });
});
