from pathlib import Path

from playwright.sync_api import expect


def test_search_units_errors_and_mobile(page):
    page.goto("http://localhost:3000")
    expect(page.get_by_text("Condiciones actuales", exact=True)).to_be_visible(timeout=30000)
    search = page.get_by_role("textbox", name="Buscar ubicación")
    search.fill("Lima")
    expect(page.get_by_role("button", name="Lima Lima, Perú")).to_be_visible()
    search.press("ArrowDown")
    search.press("Enter")
    expect(page.get_by_role("heading", name="Lima", exact=True)).to_be_visible()
    expect(page.get_by_text("Pronóstico diario (7 días)", exact=True)).to_be_visible()
    page.get_by_role("button", name="Unidades").click()
    page.get_by_role("button", name="Fahrenheit (°F)").click()
    page.keyboard.press("Escape")
    expect(page.get_by_text("72°F", exact=True)).to_be_visible()
    page.reload()
    expect(page.get_by_text("72°F", exact=True)).to_be_visible(timeout=15000)
    search.fill("ErrorTown")
    page.get_by_role("button", name="ErrorTown ErrorTown, Lima, Perú").click()
    expect(
        page.get_by_text("No fue posible obtener la información climática. Por favor, reintente.")
    ).to_be_visible(timeout=15000)
    expect(page.get_by_role("button", name="Reintentar")).to_be_visible()
    search.fill("Lima")
    page.get_by_role("button", name="Lima Lima, Perú").click()
    expect(page.get_by_text("72°F", exact=True)).to_be_visible()
    page.set_viewport_size({"width": 320, "height": 760})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    Path("test-results").mkdir(exist_ok=True)
    page.screenshot(path="test-results/mobile.png", full_page=True)


def test_denied_geolocation_keeps_search_available(page):
    page.add_init_script(
        "navigator.geolocation.getCurrentPosition = (_, error) => error({code: 1});"
    )
    page.goto("http://localhost:3000")
    page.get_by_role("button", name="Usar mi ubicación").click()
    expect(page.get_by_role("status").filter(has_text="Permiso de geolocalización")).to_be_visible(
        timeout=15000
    )
    expect(page.get_by_role("textbox", name="Buscar ubicación")).to_be_enabled()
