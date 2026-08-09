from playwright.sync_api import sync_playwright


def test_ui_basic_flow():
    url = "http://127.0.0.1:8000/ui"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url)
            # ensure page loaded
            page.wait_for_selector('#recommendButton', timeout=5000)
            # fill skills and trigger recommend
            page.fill('#skills', 'Python, Data Science')
            page.select_option('#method', 'auto')
            page.select_option('#aggregateBy', '')
            page.click('#recommendButton')
            # wait for output
            page.wait_for_selector('#output .card', timeout=5000)
            content = page.inner_text('#output')
            assert 'Input skills:' in content
            assert 'Match score' in content or 'Aggregate score' in content
        except Exception:
            # ensure artifacts directory exists
            import os
            os.makedirs('tests/e2e/artifacts', exist_ok=True)
            path = 'tests/e2e/artifacts/failure_screenshot.png'
            try:
                page.screenshot(path=path, full_page=True)
            except Exception:
                pass
            raise
        finally:
            browser.close()
