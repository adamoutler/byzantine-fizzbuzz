"""
Unit and integration tests for PWA and Open Graph sharing metadata.
"""

import os
import json
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_pwa_manifest_route():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/manifest.json")
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "FizzBuzz: The Inquisition"
        assert data["short_name"] == "FizzBuzz"
        assert data["display"] == "standalone"
        assert len(data["icons"]) >= 4

        # Test webmanifest alias
        res_alias = await ac.get("/manifest.webmanifest")
        assert res_alias.status_code == 200
        assert res_alias.json()["name"] == data["name"]

@pytest.mark.asyncio
async def test_service_worker_route():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/sw.js")
        assert res.status_code == 200
        assert "application/javascript" in res.headers.get("content-type", "")
        assert res.headers.get("service-worker-allowed") == "/"
        assert "fizzbuzz-inquisition" in res.text

@pytest.mark.asyncio
async def test_favicon_ico_route():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/favicon.ico")
        assert res.status_code == 200
        assert len(res.content) > 0

@pytest.mark.asyncio
async def test_index_html_metadata():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/")
        assert res.status_code == 200
        html = res.text

        # Title & Subtitle Links + Help Button
        assert "FizzBuzz: The Inquisition" in html
        assert "17 Agent Swarm" in html
        assert "No modulo or division" in html
        assert 'id="header-help-btn"' in html
        assert 'id="info-modal"' in html

        # Open Graph Metadata
        assert 'property="og:title"' in html
        assert 'property="og:description"' in html
        assert 'property="og:image"' in html
        assert 'https://fizzbuzz.adamoutler.com/static/icons/og-image.png' in html
        assert 'property="og:url"' in html
        assert 'property="og:type"' in html

        # Twitter Card Metadata
        assert 'name="twitter:card"' in html
        assert 'content="summary_large_image"' in html
        assert 'name="twitter:image"' in html

        # PWA & Web App tags
        assert 'rel="manifest" href="/manifest.json"' in html
        assert 'name="apple-mobile-web-app-capable" content="yes"' in html
        assert 'name="theme-color" content="#10b981"' in html
        assert 'navigator.serviceWorker.register' in html

def test_pwa_icon_assets_exist():
    base_dir = "/home/adamoutler/MeatloafBot/active-projects/byzantine-fizzbuzz/web/app/static"
    manifest_path = os.path.join(base_dir, "manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    for icon in manifest["icons"]:
        rel_path = icon["src"].lstrip("/")
        full_path = os.path.join("/home/adamoutler/MeatloafBot/active-projects/byzantine-fizzbuzz/web/app", rel_path)
        assert os.path.exists(full_path), f"Icon not found: {full_path}"
        assert os.path.getsize(full_path) > 0, f"Icon is empty: {full_path}"

    # Also verify og-image.png and apple-touch-icon.png
    og_image = os.path.join(base_dir, "icons/og-image.png")
    apple_icon = os.path.join(base_dir, "icons/apple-touch-icon.png")
    assert os.path.exists(og_image) and os.path.getsize(og_image) > 1000
    assert os.path.exists(apple_icon) and os.path.getsize(apple_icon) > 1000

    # Verify all 17 static speaker portrait avatars exist in /static/avatars/
    expected_avatars = [
        "judge_baz.png",
        "bailiff_bar.png",
        "historian.png",
        "court_clerk.png",
        "forensic_auditor.png",
        "fizz_strategist.png",
        "lobbyist_3.png",
        "fizz_appellate.png",
        "orator_fizz.png",
        "buzz_inspector.png",
        "lobbyist_5.png",
        "buzz_appellate.png",
        "orator_buzz.png",
        "antitrust_regulator.png",
        "orator_fizzbuzz.png",
        "orator_tribune.png",
        "fun_anchor.png",
    ]
    for avatar_name in expected_avatars:
        avatar_path = os.path.join(base_dir, "avatars", avatar_name)
        assert os.path.exists(avatar_path), f"Missing speaker avatar: {avatar_path}"
        assert os.path.getsize(avatar_path) > 10000, f"Speaker avatar unexpectedly small: {avatar_path}"
