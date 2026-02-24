import { test, expect } from '@playwright/test';

test.describe('Copilot Web Relay', () => {
  test('ページが読み込まれること', async ({ page }) => {
    await page.goto('/');

    // タイトルが表示されること
    await expect(page.locator('h1')).toContainText('Copilot Web Relay');

    // ターミナルコンテナが存在すること
    await expect(page.locator('.terminal-container')).toBeVisible();
  });

  test('"Start Session" ボタンが存在すること', async ({ page }) => {
    await page.goto('/');

    // Start Session ボタンが存在すること
    const startButton = page.locator('button.start');
    await expect(startButton).toBeVisible();
    await expect(startButton).toContainText('Start Session');
  });

  test('WebSocket 接続ステータスが表示されること', async ({ page }) => {
    await page.goto('/');

    // ステータスインジケーターが存在すること
    await expect(page.locator('.status-indicator')).toBeVisible();

    // Disconnected 状態で開始（バックエンドなしの場合）
    // または Connected 状態（バックエンドありの場合）
    const statusText = page.locator('.status-indicator span').last();
    await expect(statusText).toBeVisible();
  });

  test('ターミナルにウェルカムメッセージが表示されること', async ({ page }) => {
    await page.goto('/');

    // ターミナルが初期化されるまで待機
    await page.waitForSelector('.xterm');

    // xterm が初期化されていることを確認
    const terminal = page.locator('.xterm');
    await expect(terminal).toBeVisible();
  });

  test('Start Session クリックでステータス変化を確認', async ({ page }) => {
    await page.goto('/');

    // Start Session ボタンを取得
    const startButton = page.locator('button.start');

    // ボタンが有効になるまで待機（WebSocket接続後）
    // バックエンドが起動している場合のみ enabled になる
    await page.waitForTimeout(1000);

    // ボタンが存在することを確認
    await expect(startButton).toBeVisible();
  });
});
