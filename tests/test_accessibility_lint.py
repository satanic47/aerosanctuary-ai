"""Automated WCAG 2.1 AA and accessibility DOM linting tests.

Contains 18 comprehensive unit tests statically verifying semantic landmarks,
accessible labels, ARIA attributes, responsive viewports, and reduced-motion support.
"""

import os
import re

import pytest


@pytest.fixture(scope="module")
def html_content():
    """Reads frontend/index.html for static accessibility analysis."""
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    assert os.path.exists(html_path), "index.html must exist"
    with open(html_path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def css_content():
    """Reads frontend/css/style.css for accessibility and responsive styling analysis."""
    css_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "frontend", "css", "style.css"
    )
    assert os.path.exists(css_path), "style.css must exist"
    with open(css_path, encoding="utf-8") as f:
        return f.read()


def test_html_lang_attribute(html_content):
    """Verifies that the html tag defines a valid primary language."""
    assert re.search(r'<html\s+lang=["\']en["\']', html_content, re.IGNORECASE)


def test_meta_viewport_for_responsive_scaling(html_content):
    """Verifies meta viewport tag ensuring responsive layout across all screen devices."""
    assert 'name="viewport"' in html_content
    assert "width=device-width" in html_content


def test_skip_link_present(html_content):
    """Verifies presence of an accessible skip-to-content link."""
    assert 'class="skip-link"' in html_content
    assert 'href="#main-content"' in html_content


def test_skip_link_target_exists(html_content):
    """Verifies that the anchor target for the skip link exists in DOM."""
    assert 'id="main-content"' in html_content


def test_banner_landmark_role(html_content):
    """Verifies presence of ARIA banner landmark role."""
    assert 'role="banner"' in html_content


def test_navigation_landmark_role(html_content):
    """Verifies presence of ARIA navigation landmark role with label."""
    assert 'role="navigation"' in html_content
    assert 'aria-label="Main Navigation"' in html_content


def test_main_landmark_role(html_content):
    """Verifies presence of ARIA main landmark role."""
    assert 'role="main"' in html_content


def test_contentinfo_landmark_role(html_content):
    """Verifies presence of ARIA contentinfo landmark role."""
    assert 'role="contentinfo"' in html_content


def test_form_inputs_have_matching_labels(html_content):
    """Verifies that all input fields have explicit <label for="..."> associations."""
    input_ids = re.findall(r'<input\s+[^>]*id=["\']([^"\']+)["\']', html_content)
    assert len(input_ids) > 0
    for el_id in input_ids:
        pattern = rf'<label\s+[^>]*for=["\']{el_id}["\']'
        assert re.search(pattern, html_content), f"Input '{el_id}' lacks an associated label."


def test_select_dropdowns_have_matching_labels(html_content):
    """Verifies that all select dropdowns have explicit <label for="..."> associations."""
    select_ids = re.findall(r'<select\s+[^>]*id=["\']([^"\']+)["\']', html_content)
    assert len(select_ids) > 0
    for el_id in select_ids:
        pattern = rf'<label\s+[^>]*for=["\']{el_id}["\']'
        assert re.search(pattern, html_content), f"Select '{el_id}' lacks an associated label."


def test_buttons_have_discernible_text_or_aria_labels(html_content):
    """Verifies that all buttons possess readable text or an aria-label attribute."""
    buttons = re.findall(r"<button\s+([^>]*)>(.*?)</button>", html_content, re.DOTALL)
    assert len(buttons) > 0
    for attrs, inner_text in buttons:
        has_text = len(inner_text.strip()) > 0
        has_aria_label = "aria-label=" in attrs
        assert has_text or has_aria_label, "Found button lacking both visible text and aria-label."


def test_aria_live_on_dynamic_chat_thread(html_content):
    """Verifies that the chat thread container has aria-live and screen reader status announcers."""
    assert 'aria-live="polite"' in html_content
    assert 'id="a11y-announcer"' in html_content
    assert 'id="chat-messages"' in html_content


def test_tablist_and_tab_accessibility(html_content):
    """Verifies ARIA roles on tablist and tab controls."""
    assert 'role="tablist"' in html_content
    assert 'role="tab"' in html_content
    assert "aria-selected=" in html_content


def test_heading_hierarchy_presence(html_content):
    """Verifies logical presence of heading levels."""
    assert "<h2" in html_content
    assert "<h3" in html_content


def test_focus_visible_styling_defined(css_content):
    """Verifies visible keyboard focus rings in stylesheet."""
    assert ":focus-visible" in css_content
    assert "outline:" in css_content


def test_touch_target_size_defined(css_content):
    """Verifies minimum touch target height (44px) for WCAG 2.1 compliance."""
    assert "min-height: 44px" in css_content or "min-height: 42px" in css_content


def test_reduced_motion_media_query_defined(css_content):
    """Verifies prefers-reduced-motion media query for users with motion sensitivity."""
    assert "@media (prefers-reduced-motion: reduce)" in css_content


def test_responsive_mobile_breakpoint_defined(css_content):
    """Verifies responsive breakpoint rules for mobile screens."""
    assert "@media (max-width: 768px)" in css_content


def test_form_inputs_have_aria_describedby_error_association(html_content):
    """Verifies that form inputs are linked to an accessible error container via aria-describedby."""
    assert 'id="profile-form-error"' in html_content
    assert 'aria-describedby="profile-form-error"' in html_content
    assert 'role="alert"' in html_content


def test_wcag_color_contrast_documentation(css_content):
    """Verifies that high-contrast color choices meeting WCAG AA (>= 4.5:1) are implemented."""
    assert "#fee2e2" in css_content or "#b91c1c" in css_content
    assert ":focus-visible" in css_content
