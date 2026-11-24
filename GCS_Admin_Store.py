"""
GLOBAL CHEMICAL SOLUTION — SINGLE FILE FLASK WEBSITE
----------------------------------------------------
A one-file starter website inspired by the user's Rainbow Mart structure.

Run:
    pip install Flask
    ADMIN_USERNAME=admin ADMIN_PASSWORD="YourStrongPassword" python app.py

Then open:
    http://127.0.0.1:5000

IMPORTANT:
- This demo intentionally displays only a limited lawful catalogue:
  Isopropyl Alcohol (IPA), HDPE Industrial Bottle, Ethylhexanoic Acid.
- It does not advertise, list, price, or facilitate orders for GBL, BDO or GHB. The admin catalogue blocks these terms.
- Confirm product classification, local law, destination-country rules,
  transport requirements, intended use, and current SDS before supply.
- The original contact form saves enquiries in enquiries.db. Store orders and customers are saved in gcs_store.db.
- Replace the development secret key before public deployment.
- Images are remote Unsplash images and require an internet connection.
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash
from datetime import datetime
import os
import sqlite3
import json

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "replace-this-development-key-before-deployment"
)

# ---------------------------------------------------------------------
# COMPANY PROFILE
# ---------------------------------------------------------------------

COMPANY = {
    "name": "Global Chemical Solution",
    "short_name": "GCS",
    "email": "Bestgblonine.uk@gmail.com",
    "phone": "+44 7983 259218",
    "address": "22 Parks Vw Rd, Inverness IV2 6JJ, United Kingdom",
    "country": "United Kingdom",
    "tagline": "Professional service. Responsible supply.",
}

# ---------------------------------------------------------------------
# SAFE STARTER CATALOGUE
# ---------------------------------------------------------------------
# No prices are displayed because final specifications, packaging,
# availability, and eligibility must be confirmed individually.

PRODUCTS = [
    {
        "id": 1,
        "slug": "isopropyl-alcohol",
        "name": "Isopropyl Alcohol (IPA)",
        "category": "Solvents",
        "short": "Industrial and professional-use solvent enquiry.",
        "description": (
            "Isopropyl alcohol is used in a range of legitimate industrial "
            "and cleaning applications. Exact concentration, grade, "
            "packaging, availability and supply eligibility must be "
            "confirmed before any quotation or supply decision."
        ),
        "image": (
            "https://images.unsplash.com/photo-1603126857599-f6e157fa2fe6"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "badge": "Solvent",
        "specifications": [
            ("Product", "Isopropyl Alcohol (IPA)"),
            ("Grade", "Confirm on enquiry"),
            ("Concentration", "Confirm on enquiry"),
            ("Packaging", "Subject to availability"),
            ("Documentation", "Current SDS on request"),
        ],
        "applications": [
            "Professional cleaning applications",
            "Industrial process enquiries",
            "Laboratory and maintenance supply enquiries",
        ],
        "notice": (
            "Use only in accordance with the current SDS and applicable "
            "workplace safety procedures."
        ),
    },
    {
        "id": 2,
        "slug": "hdpe-industrial-bottle",
        "name": "HDPE Industrial Bottle",
        "category": "Packaging",
        "short": "Durable packaging for compatible industrial materials.",
        "description": (
            "High-density polyethylene (HDPE) containers are used for "
            "packaging a variety of compatible materials. Container "
            "compatibility must be checked against the exact chemical, "
            "concentration, temperature and storage conditions."
        ),
        "image": (
            "https://images.unsplash.com/photo-1602143407151-7111542de6e8"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "badge": "Packaging",
        "specifications": [
            ("Material", "HDPE"),
            ("Capacity", "Confirm on enquiry"),
            ("Closure", "Confirm on enquiry"),
            ("Compatibility", "Must be verified for each substance"),
            ("Documentation", "Product information on request"),
        ],
        "applications": [
            "Compatible industrial packaging",
            "Storage of approved compatible materials",
            "Packaging procurement enquiries",
        ],
        "notice": (
            "Never assume a container is compatible. Obtain a documented "
            "compatibility confirmation before filling or storing chemicals."
        ),
    },
    {
        "id": 3,
        "slug": "ethylhexanoic-acid",
        "name": "Ethylhexanoic Acid",
        "category": "Industrial Chemicals",
        "short": "Industrial chemical specification enquiry.",
        "description": (
            "Ethylhexanoic acid is used in certain industrial chemical "
            "applications. Grade, specification, packaging and supply "
            "eligibility must be confirmed through a formal enquiry and "
            "applicable regulatory review."
        ),
        "image": (
            "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "badge": "Industrial",
        "specifications": [
            ("Product", "Ethylhexanoic Acid"),
            ("Grade", "Confirm on enquiry"),
            ("Specification", "Confirm on enquiry"),
            ("Packaging", "Subject to availability"),
            ("Documentation", "Current SDS on request"),
        ],
        "applications": [
            "Industrial chemical enquiries",
            "Specification and documentation review",
            "Approved professional applications",
        ],
        "notice": (
            "Review the current SDS and applicable local requirements before "
            "handling, storage, transport or use."
        ),
    },
]

CATEGORIES = ["All", "Solvents", "Packaging", "Industrial Chemicals"]

# ---------------------------------------------------------------------
# SINGLE-PAGE HTML TEMPLATE
# ---------------------------------------------------------------------

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Global Chemical Solution — professional industrial product and packaging enquiries.">
<meta name="theme-color" content="#10243b">
<title>{{ company.name }} | Professional Chemical Solutions</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
/* ================================================================
   01. RESET AND DESIGN TOKENS
   ================================================================ */

:root {
    --navy: #10243b;
    --navy-dark: #091827;
    --navy-soft: #173b59;
    --blue: #1768a5;
    --blue-light: #278fc0;
    --cyan: #36b9c7;
    --cyan-soft: #e8f8f9;
    --ink: #1c2b3a;
    --muted: #687887;
    --muted-light: #91a0aa;
    --white: #ffffff;
    --pale: #f3f7fa;
    --pale-blue: #eaf2f7;
    --line: #e3ebf0;
    --success: #16794a;
    --danger: #a52d36;
    --shadow: 0 18px 55px rgba(16, 36, 59, 0.10);
    --radius: 12px;
    --radius-small: 6px;
    --container: 1160px;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    scroll-behavior: smooth;
    scroll-padding-top: 90px;
}

body {
    color: var(--ink);
    background: var(--white);
    font-family: "DM Sans", sans-serif;
    line-height: 1.65;
    overflow-x: hidden;
}

body.modal-open {
    overflow: hidden;
}

img {
    display: block;
    max-width: 100%;
}

button,
input,
textarea,
select {
    font: inherit;
}

button {
    cursor: pointer;
}

a {
    color: inherit;
}

.container {
    width: min(var(--container), 90%);
    margin-inline: auto;
}

.section {
    padding: 92px 0;
}

.section-soft {
    background: var(--pale);
}

.section-dark {
    background: var(--navy);
    color: var(--white);
}

/* ================================================================
   02. TYPOGRAPHY
   ================================================================ */

h1,
h2,
h3,
h4,
h5 {
    font-family: "Manrope", sans-serif;
    line-height: 1.18;
    color: inherit;
}

h1 {
    font-size: clamp(2.6rem, 5vw, 4.7rem);
    font-weight: 800;
    letter-spacing: -2.4px;
}

h2 {
    font-size: clamp(2rem, 3.5vw, 3.15rem);
    font-weight: 800;
    letter-spacing: -1.4px;
}

h3 {
    font-size: 1.22rem;
    font-weight: 800;
}

p {
    color: var(--muted);
}

.lead {
    font-size: 1.08rem;
    line-height: 1.85;
}

/* ================================================================
   03. SMALL REUSABLE COMPONENTS
   ================================================================ */

.eyebrow {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 18px;
    color: var(--blue);
    font-size: 0.69rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.eyebrow::before {
    content: "";
    width: 27px;
    height: 2px;
    background: var(--cyan);
}

.eyebrow-light {
    color: #c0dce9;
}

.section-heading {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 25px;
    margin-bottom: 36px;
}

.section-heading h2 {
    margin-bottom: 0;
}

.section-intro {
    max-width: 650px;
    margin-top: 15px;
    font-size: 0.96rem;
}

.btn {
    display: inline-flex;
    min-height: 48px;
    align-items: center;
    justify-content: center;
    gap: 13px;
    padding: 13px 21px;
    border: 1px solid transparent;
    border-radius: var(--radius-small);
    text-decoration: none;
    font-size: 0.83rem;
    font-weight: 800;
    transition: transform 0.2s ease, background 0.2s ease;
}

.btn:hover {
    transform: translateY(-2px);
}

.btn-primary {
    color: var(--white);
    background: linear-gradient(105deg, var(--blue), #1599b1);
}

.btn-dark {
    color: var(--white);
    background: var(--navy);
}

.btn-outline {
    color: var(--white);
    border-color: rgba(255, 255, 255, 0.55);
    background: rgba(255, 255, 255, 0.07);
}

.btn-outline-dark {
    color: var(--navy);
    border-color: #cbd8e0;
    background: transparent;
}

.text-link {
    color: var(--blue);
    text-decoration: none;
    font-size: 0.83rem;
    font-weight: 800;
}

.text-link:hover {
    color: var(--cyan);
}

.pill {
    display: inline-flex;
    align-items: center;
    padding: 6px 11px;
    border-radius: 99px;
    color: var(--blue);
    background: #e9f5fa;
    font-size: 0.68rem;
    font-weight: 800;
}

.hidden {
    display: none !important;
}

/* ================================================================
   04. TOP CONTACT BAR
   ================================================================ */

.topbar {
    color: #c6d6e1;
    background: var(--navy-dark);
    font-size: 0.72rem;
}

.topbar-inner {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    padding: 9px 0;
}

.topbar a {
    color: #dce9ef;
    text-decoration: none;
}

.topbar a:hover {
    color: var(--cyan);
}

/* ================================================================
   05. HEADER AND NAVIGATION
   ================================================================ */

.site-header {
    position: sticky;
    top: 0;
    z-index: 50;
    background: rgba(255, 255, 255, 0.97);
    border-bottom: 1px solid var(--line);
    backdrop-filter: blur(14px);
}

.navbar {
    display: flex;
    min-height: 84px;
    align-items: center;
    justify-content: space-between;
    gap: 25px;
}

.brand {
    display: inline-flex;
    align-items: center;
    gap: 11px;
    color: var(--navy);
    text-decoration: none;
    font-family: "Manrope", sans-serif;
    font-size: 0.85rem;
    font-weight: 800;
    letter-spacing: 1px;
    line-height: 1.12;
}

.brand-mark {
    display: grid;
    width: 48px;
    height: 48px;
    place-items: center;
    border-radius: 12px;
    color: white;
    background: linear-gradient(135deg, var(--blue), var(--cyan));
    box-shadow: 0 8px 18px rgba(23, 104, 165, 0.18);
    font-size: 0.95rem;
    letter-spacing: 0;
}

.brand small {
    display: block;
    margin-top: 4px;
    color: #718294;
    font-size: 0.57rem;
    letter-spacing: 3px;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 28px;
}

.nav-links a {
    color: #34485a;
    text-decoration: none;
    font-size: 0.79rem;
    font-weight: 800;
    transition: color 0.2s ease;
}

.nav-links a:hover,
.nav-links a.active {
    color: var(--blue);
}

.nav-links .nav-cta {
    padding: 13px 17px;
    border-radius: 5px;
    color: white;
    background: var(--navy);
}

.menu-button {
    display: none;
    width: 42px;
    height: 42px;
    border: 1px solid var(--line);
    border-radius: 7px;
    color: var(--navy);
    background: white;
    font-size: 1.35rem;
}

/* ================================================================
   06. HERO
   ================================================================ */

.hero {
    position: relative;
    display: flex;
    min-height: 630px;
    align-items: center;
    overflow: hidden;
    color: white;
    background:
        linear-gradient(
            90deg,
            rgba(7, 24, 43, 0.97) 0%,
            rgba(9, 38, 61, 0.84) 48%,
            rgba(8, 37, 58, 0.36) 100%
        ),
        url("https://images.unsplash.com/photo-1581093458791-9d42e3c4a3d8?auto=format&fit=crop&w=2100&q=90")
        center / cover;
}

.hero::after {
    position: absolute;
    right: -120px;
    bottom: -240px;
    width: 580px;
    height: 580px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 50%;
    content: "";
}

.hero-content {
    position: relative;
    z-index: 2;
    padding: 95px 0;
}

.hero h1 {
    max-width: 790px;
    margin-bottom: 24px;
}

.hero h1 span {
    color: #68d8dc;
}

.hero-copy {
    max-width: 650px;
    color: #d0dce5;
    font-size: 1.04rem;
}

.hero-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 13px;
    margin-top: 31px;
}

.hero-proof {
    display: flex;
    flex-wrap: wrap;
    gap: 25px;
    margin-top: 35px;
    color: #d5e2e9;
    font-size: 0.75rem;
}

.hero-proof span::before {
    margin-right: 8px;
    color: #6ce0d9;
    content: "✓";
    font-weight: 900;
}

.hero-stamp {
    position: absolute;
    right: 8%;
    bottom: 55px;
    z-index: 2;
    display: flex;
    min-width: 210px;
    flex-direction: column;
    padding: 23px 25px;
    border: 1px solid rgba(255, 255, 255, 0.4);
    color: white;
    background: rgba(255, 255, 255, 0.11);
    backdrop-filter: blur(12px);
}

.hero-stamp strong {
    font-family: "Manrope", sans-serif;
    font-size: 2.5rem;
    letter-spacing: 3px;
}

.hero-stamp span {
    font-size: 0.65rem;
    letter-spacing: 2px;
}

.hero-stamp small {
    margin-top: 10px;
    color: #c8d9e5;
    font-size: 0.55rem;
    letter-spacing: 1.5px;
}

/* ================================================================
   07. VALUE STRIP
   ================================================================ */

.value-strip {
    border-bottom: 1px solid var(--line);
    background: #f4f8fa;
}

.value-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    padding: 27px 0;
}

.value-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 5px 22px;
    border-right: 1px solid #dce6eb;
}

.value-item:first-child {
    padding-left: 0;
}

.value-item:last-child {
    border: 0;
}

.value-number {
    color: #1a9caf;
    font-family: "Manrope", sans-serif;
    font-size: 1.65rem;
    font-weight: 800;
}

.value-item span:last-child {
    color: #43586a;
    font-size: 0.73rem;
    font-weight: 800;
    line-height: 1.35;
}

/* ================================================================
   08. PRODUCT CATALOGUE
   ================================================================ */

.catalogue-tools {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 25px;
}

.search-box {
    display: flex;
    width: min(360px, 100%);
    align-items: center;
    gap: 10px;
    padding: 11px 14px;
    border: 1px solid var(--line);
    border-radius: 7px;
    background: white;
}

.search-box span {
    color: var(--muted-light);
}

.search-box input {
    width: 100%;
    border: 0;
    outline: 0;
    color: var(--ink);
    background: transparent;
    font-size: 0.82rem;
}

.filter-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 28px;
}

.filter-button {
    padding: 9px 14px;
    border: 1px solid var(--line);
    border-radius: 99px;
    color: #536575;
    background: white;
    font-size: 0.72rem;
    font-weight: 800;
    transition: all 0.2s ease;
}

.filter-button:hover,
.filter-button.active {
    border-color: var(--blue);
    color: white;
    background: var(--blue);
}

.product-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 25px;
}

.product-card {
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: white;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.product-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow);
}

.product-image {
    position: relative;
    height: 300px;
    overflow: hidden;
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
}

.product-image img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center;
    padding: 10px;
    transition: transform 0.4s ease;
}

.product-card:hover .product-image img {
    transform: scale(1.06);
}

.product-badge {
    position: absolute;
    top: 16px;
    left: 16px;
    padding: 6px 11px;
    border-radius: 4px;
    color: var(--blue);
    background: white;
    font-size: 0.65rem;
    font-weight: 800;
}

.product-content {
    padding: 23px;
}

.product-content h3 {
    margin: 12px 0 10px;
}

.product-content p {
    min-height: 66px;
    font-size: 0.81rem;
}

.product-bottom {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-top: 17px;
    padding-top: 15px;
    border-top: 1px solid var(--line);
}

.product-bottom button {
    padding: 0;
    border: 0;
    color: var(--blue);
    background: transparent;
    font-size: 0.76rem;
    font-weight: 800;
}

.product-bottom span {
    color: var(--muted-light);
    font-size: 0.65rem;
}

.no-results {
    display: none;
    padding: 45px 20px;
    border: 1px dashed #cbd8e0;
    border-radius: var(--radius);
    color: var(--muted);
    text-align: center;
}

/* ================================================================
   09. FEATURE / ABOUT SPLIT
   ================================================================ */

.split-feature {
    display: grid;
    grid-template-columns: 1fr 1fr;
    background: var(--pale);
}

.split-photo {
    min-height: 530px;
    background:
        url("https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1400&q=85")
        center / cover;
}

.split-copy {
    align-self: center;
    padding: 80px clamp(35px, 8vw, 120px);
}

.split-copy h2 {
    max-width: 520px;
    margin-bottom: 20px;
}

.split-copy > p {
    max-width: 550px;
}

.check-list {
    margin: 27px 0;
    list-style: none;
}

.check-list li {
    position: relative;
    padding: 9px 0 9px 29px;
    color: #45596a;
    font-size: 0.82rem;
}

.check-list li::before {
    position: absolute;
    left: 0;
    color: #159eaa;
    content: "✓";
    font-weight: 900;
}

/* ================================================================
   10. PROCESS STEPS
   ================================================================ */

.process-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 23px;
    margin-top: 36px;
}

.process-card {
    padding: 30px;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: white;
}

.process-card .step {
    display: grid;
    width: 48px;
    height: 48px;
    place-items: center;
    margin-bottom: 22px;
    border-radius: 12px;
    color: white;
    background: linear-gradient(135deg, var(--blue), var(--cyan));
    font-family: "Manrope", sans-serif;
    font-weight: 800;
}

.process-card h3 {
    margin-bottom: 11px;
}

.process-card p {
    font-size: 0.81rem;
}

/* ================================================================
   11. SAFETY PANEL
   ================================================================ */

.safety-panel {
    position: relative;
    overflow: hidden;
    padding: 70px;
    border-radius: 15px;
    color: white;
    background:
        linear-gradient(110deg, rgba(12, 36, 57, 0.97), rgba(19, 91, 119, 0.88)),
        url("https://images.unsplash.com/photo-1581093588401-fbb62a02f120?auto=format&fit=crop&w=1600&q=85")
        center / cover;
}

.safety-panel h2 {
    max-width: 700px;
}

.safety-panel p {
    max-width: 680px;
    color: #d0dce5;
}

.safety-points {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin: 30px 0;
}

.safety-point {
    padding: 17px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 7px;
    color: #e3edf2;
    background: rgba(255, 255, 255, 0.07);
    font-size: 0.76rem;
}

/* ================================================================
   12. CTA BAND
   ================================================================ */

.cta-band {
    padding: 57px 0;
    color: white;
    background: linear-gradient(110deg, #10243b, #174b6c);
}

.cta-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 25px;
}

.cta-inner h2 {
    margin-bottom: 8px;
    font-size: clamp(1.8rem, 3vw, 2.5rem);
}

.cta-inner p {
    color: #c5d6e0;
}

/* ================================================================
   13. PAGE SECTIONS / ABOUT / SAFETY
   ================================================================ */

.page-banner {
    padding: 85px 0;
    color: white;
    background:
        linear-gradient(100deg, rgba(11, 32, 54, 0.96), rgba(18, 87, 122, 0.83)),
        url("https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=1800&q=85")
        center / cover;
}

.page-banner h1 {
    font-size: clamp(2.6rem, 5vw, 4rem);
}

.page-banner p {
    max-width: 680px;
    margin-top: 15px;
    color: #d0dce5;
}

.about-grid {
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
    gap: 75px;
}

.about-grid p {
    margin-bottom: 17px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.info-card {
    padding: 29px;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: white;
}

.info-card .info-number {
    color: var(--cyan);
    font-family: "Manrope", sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
}

.info-card h3 {
    margin: 12px 0;
}

.info-card p {
    font-size: 0.82rem;
}

/* ================================================================
   14. CONTACT FORM
   ================================================================ */

.contact-layout {
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
    gap: 75px;
}

.contact-details {
    margin-top: 28px;
}

.contact-line {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 17px 0;
    border-top: 1px solid var(--line);
}

.contact-line small {
    color: #8494a0;
    font-size: 0.63rem;
    font-weight: 800;
    letter-spacing: 1.5px;
}

.contact-line strong {
    overflow-wrap: anywhere;
    font-size: 0.88rem;
}

.contact-form {
    padding: 34px;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: #f7fafb;
}

.contact-form h3 {
    margin-bottom: 23px;
    font-size: 1.45rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
}

.form-field {
    margin-bottom: 16px;
}

.form-field label {
    display: block;
    margin-bottom: 7px;
    color: #42586a;
    font-size: 0.73rem;
    font-weight: 800;
}

.form-field input,
.form-field textarea,
.form-field select {
    width: 100%;
    padding: 13px 14px;
    border: 1px solid #dce5ea;
    border-radius: 5px;
    outline: none;
    color: var(--ink);
    background: white;
    font-size: 0.82rem;
    transition: border 0.2s ease, box-shadow 0.2s ease;
}

.form-field input:focus,
.form-field textarea:focus,
.form-field select:focus {
    border-color: var(--blue-light);
    box-shadow: 0 0 0 3px rgba(39, 143, 192, 0.10);
}

.form-field textarea {
    min-height: 130px;
    resize: vertical;
}

.form-note {
    display: block;
    margin-top: 14px;
    color: #8796a0;
    font-size: 0.65rem;
}

.flash {
    margin-bottom: 17px;
    padding: 12px 14px;
    border-radius: 5px;
    font-size: 0.77rem;
}

.flash.success {
    color: var(--success);
    background: #e5f6ec;
}

.flash.error {
    color: var(--danger);
    background: #fff0f0;
}

/* ================================================================
   15. FOOTER
   ================================================================ */

.footer {
    padding-top: 62px;
    color: #d8e3e9;
    background: var(--navy-dark);
}

.footer-grid {
    display: grid;
    grid-template-columns: 1.35fr 0.7fr 1fr;
    gap: 55px;
    padding-bottom: 47px;
}

.footer-brand {
    color: white;
}

.footer-brand p {
    max-width: 350px;
    margin-top: 20px;
    color: #aebfca;
    font-size: 0.78rem;
}

.footer h4 {
    margin-bottom: 18px;
    color: white;
    font-size: 0.85rem;
}

.footer-links a {
    display: block;
    margin: 10px 0;
    color: #afc0cb;
    text-decoration: none;
    font-size: 0.76rem;
}

.footer-links a:hover {
    color: var(--cyan);
}

.footer-contact p {
    margin: 9px 0;
    color: #afc0cb;
    font-size: 0.75rem;
    overflow-wrap: anywhere;
}

.footer-bottom {
    padding: 18px 0;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    color: #9fb0bc;
    font-size: 0.68rem;
}

.footer-bottom-inner {
    display: flex;
    justify-content: space-between;
    gap: 20px;
}

/* ================================================================
   16. PRODUCT DETAIL MODAL
   ================================================================ */

.modal-backdrop {
    position: fixed;
    inset: 0;
    z-index: 100;
    display: none;
    overflow-y: auto;
    padding: 35px 15px;
    background: rgba(5, 17, 29, 0.75);
}

.modal-backdrop.open {
    display: grid;
    place-items: center;
}

.product-modal {
    position: relative;
    width: min(900px, 100%);
    overflow: hidden;
    border-radius: 12px;
    background: white;
    box-shadow: 0 25px 90px rgba(0, 0, 0, 0.25);
}

.modal-close {
    position: absolute;
    top: 13px;
    right: 13px;
    z-index: 2;
    display: grid;
    width: 38px;
    height: 38px;
    place-items: center;
    border: 0;
    border-radius: 50%;
    color: var(--navy);
    background: white;
    font-size: 1.3rem;
}

.modal-content {
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
}

.modal-image {
    min-height: 440px;
    background: var(--pale-blue);
}

.modal-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.modal-info {
    padding: 43px 37px;
}

.modal-info h2 {
    margin: 13px 0;
    font-size: 2rem;
}

.modal-info p {
    font-size: 0.84rem;
}

.modal-specs {
    margin: 22px 0;
    list-style: none;
}

.modal-specs li {
    padding: 9px 0;
    border-bottom: 1px solid var(--line);
    color: #536575;
    font-size: 0.76rem;
}

.modal-notice {
    margin: 20px 0;
    padding: 13px;
    border-left: 3px solid var(--cyan);
    color: #496170;
    background: var(--cyan-soft);
    font-size: 0.72rem;
}

/* ================================================================
   17. BACK TO TOP AND ACCESSIBILITY
   ================================================================ */

.back-to-top {
    position: fixed;
    right: 22px;
    bottom: 22px;
    z-index: 40;
    display: none;
    width: 43px;
    height: 43px;
    border: 0;
    border-radius: 50%;
    color: white;
    background: var(--blue);
    box-shadow: var(--shadow);
    font-size: 1.2rem;
}

.back-to-top.visible {
    display: block;
}

:focus-visible {
    outline: 3px solid rgba(54, 185, 199, 0.65);
    outline-offset: 3px;
}

/* ================================================================
   18. RESPONSIVE TABLET
   ================================================================ */

@media (max-width: 900px) {
    .nav-links {
        gap: 15px;
    }

    .nav-links a {
        font-size: 0.72rem;
    }

    .hero-stamp {
        right: 5%;
    }

    .product-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .value-item {
        padding-inline: 12px;
    }

    .split-copy {
        padding: 60px 7%;
    }

    .footer-grid {
        gap: 30px;
    }
}

/* ================================================================
   19. RESPONSIVE MOBILE
   ================================================================ */

@media (max-width: 700px) {
    .topbar-inner {
        justify-content: center;
        text-align: center;
    }

    .topbar-inner span:last-child {
        display: none;
    }

    .navbar {
        min-height: 72px;
    }

    .menu-button {
        display: block;
    }

    .nav-links {
        position: absolute;
        top: 72px;
        right: 0;
        left: 0;
        display: none;
        align-items: stretch;
        flex-direction: column;
        gap: 0;
        padding: 12px 5% 20px;
        border-bottom: 1px solid var(--line);
        background: white;
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.08);
    }

    .nav-links.open {
        display: flex;
    }

    .nav-links a {
        padding: 12px 0;
        font-size: 0.82rem;
    }

    .nav-links .nav-cta {
        padding: 13px 15px;
    }

    .hero {
        min-height: 600px;
        background-position: 60% center;
    }

    .hero-content {
        padding: 75px 0;
    }

    .hero-stamp {
        display: none;
    }

    .hero-proof {
        gap: 12px 20px;
    }

    .value-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 18px 10px;
    }

    .value-item {
        border: 0;
        padding: 4px 0;
    }

    .section {
        padding: 65px 0;
    }

    .section-heading {
        display: block;
    }

    .section-heading .text-link {
        display: inline-block;
        margin-top: 15px;
    }

    .catalogue-tools {
        align-items: stretch;
        flex-direction: column;
    }

    .search-box {
        width: 100%;
    }

    .product-grid {
        grid-template-columns: 1fr;
    }

    .product-image {
        height: 230px;
    }

    .split-feature {
        grid-template-columns: 1fr;
    }

    .split-photo {
        min-height: 310px;
    }

    .split-copy {
        padding: 55px 6%;
    }

    .process-grid {
        grid-template-columns: 1fr;
    }

    .safety-panel {
        padding: 40px 25px;
    }

    .safety-points {
        grid-template-columns: 1fr;
    }

    .cta-inner {
        align-items: flex-start;
        flex-direction: column;
    }

    .about-grid,
    .contact-layout {
        grid-template-columns: 1fr;
        gap: 35px;
    }

    .info-grid {
        grid-template-columns: 1fr;
    }

    .footer-grid {
        grid-template-columns: 1fr;
        gap: 28px;
    }

    .footer-bottom-inner {
        flex-direction: column;
    }

    .modal-content {
        grid-template-columns: 1fr;
    }

    .modal-image {
        min-height: 230px;
        max-height: 260px;
    }

    .modal-info {
        padding: 28px 23px;
    }
}

/* ================================================================
   20. SMALL MOBILE
   ================================================================ */

@media (max-width: 420px) {
    h1 {
        letter-spacing: -1.5px;
    }

    .hero-actions {
        align-items: stretch;
        flex-direction: column;
    }

    .hero-actions .btn {
        width: 100%;
    }

    .form-row {
        grid-template-columns: 1fr;
        gap: 0;
    }

    .contact-form {
        padding: 23px 18px;
    }

    .brand {
        font-size: 0.75rem;
    }

    .brand-mark {
        width: 42px;
        height: 42px;
    }
}
</style>
</head>

<body>

<!-- ============================================================
     TOP BAR
     ============================================================ -->
<div class="topbar">
    <div class="container topbar-inner">
        <span>Professional industrial product enquiries</span>
        <span>
            <a href="mailto:{{ company.email }}">{{ company.email }}</a>
            &nbsp; | &nbsp;
            <a href="tel:{{ company.phone }}">{{ company.phone }}</a>
        </span>
    </div>
</div>

<!-- ============================================================
     HEADER
     ============================================================ -->
<header class="site-header">
    <div class="container navbar">
        <a class="brand" href="#home" aria-label="Global Chemical Solution home">
            <span class="brand-mark">GCS</span>
            <span>
                GLOBAL CHEMICAL
                <small>SOLUTION</small>
            </span>
        </a>

        <button
            class="menu-button"
            id="menuButton"
            aria-label="Open navigation"
            aria-expanded="false"
        >☰</button>

        <nav class="nav-links" id="navLinks">
            <a class="active" href="#home">Home</a>
            <a href="#products">Products</a>
            <a href="#about">About</a>
            <a href="#process">Our Process</a>
            <a href="#safety">Safety</a>
            <a href="/shop">Shop / Cart</a>
            <a href="/admin/login">Admin</a>
            <a href="#contact" class="nav-cta">Request an Enquiry ↗</a>
        </nav>
    </div>
</header>

<!-- ============================================================
     HERO SECTION
     ============================================================ -->
<main id="home">
<section class="hero">
    <div class="container hero-content">
        <div class="eyebrow eyebrow-light">
            INDUSTRIAL SUPPLY • RESPONSIBLE SERVICE
        </div>

        <h1>
            Reliable chemical solutions.
            <span>Professional service.</span>
        </h1>

        <p class="hero-copy">
            Explore selected industrial product and packaging enquiries.
            We focus on clear specifications, responsible communication
            and safety documentation.
        </p>

        <div class="hero-actions">
            <a class="btn btn-primary" href="#products">
                Explore Catalogue <span>→</span>
            </a>
            <a class="btn btn-outline" href="#contact">
                Contact Our Team
            </a>
        </div>

        <div class="hero-proof">
            <span>Specification-led enquiries</span>
            <span>Documentation on request</span>
            <span>Safety-first approach</span>
        </div>
    </div>

    <div class="hero-stamp">
        <strong>GCS</strong>
        <span>GLOBAL CHEMICAL</span>
        <span>SOLUTION</span>
        <small>INDUSTRIAL • PACKAGING • SUPPORT</small>
    </div>
</section>

<!-- ============================================================
     VALUE STRIP
     ============================================================ -->
<section class="value-strip">
    <div class="container value-grid">
        <div class="value-item">
            <span class="value-number">01</span>
            <span>Clear product<br>information</span>
        </div>
        <div class="value-item">
            <span class="value-number">02</span>
            <span>Safety-first<br>approach</span>
        </div>
        <div class="value-item">
            <span class="value-number">03</span>
            <span>Documentation<br>support</span>
        </div>
        <div class="value-item">
            <span class="value-number">04</span>
            <span>Professional<br>enquiries</span>
        </div>
    </div>
</section>

<!-- ============================================================
     PRODUCT CATALOGUE
     ============================================================ -->
<section class="section container" id="products">
    <div class="section-heading">
        <div>
            <div class="eyebrow">OUR CATALOGUE</div>
            <h2>Products & solutions</h2>
            <p class="section-intro">
                Browse the starter catalogue. Final product specifications,
                packaging and availability are confirmed individually.
            </p>
        </div>
        <a class="text-link" href="#contact">Ask about a product →</a>
    </div>

    <div class="catalogue-tools">
        <div class="search-box">
            <span>⌕</span>
            <input
                type="search"
                id="productSearch"
                placeholder="Search catalogue..."
                aria-label="Search products"
            >
        </div>
        <span class="pill">{{ products|length }} catalogue items</span>
    </div>

    <div class="filter-row" id="filterRow">
        {% for category in categories %}
        <button
            class="filter-button {% if loop.first %}active{% endif %}"
            data-category="{{ category }}"
            type="button"
        >{{ category }}</button>
        {% endfor %}
    </div>

    <div class="product-grid" id="productGrid">
        {% for product in products %}
        <article
            class="product-card"
            data-name="{{ product.name|lower }}"
            data-category="{{ product.category }}"
        >
            <div class="product-image">
                <img
                    src="{{ product.image }}"
                    alt="{{ product.name }}"
                    loading="lazy"
                >
                <span class="product-badge">{{ product.badge }}</span>
            </div>

            <div class="product-content">
                <span class="pill">{{ product.category }}</span>
                <h3>{{ product.name }}</h3>
                <p>{{ product.short }}</p>

                <div class="product-bottom">
                    <span>Specification on enquiry</span>
                    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                        {% if product.store_product %}
                        <span class="product-price">{% if product.price > 0 %}{{ product.currency_symbol }} {{ '%.2f'|format(product.price) }} · {{ product.currency }}{% else %}Price on request{% endif %}</span>
                        <a class="details-button" href="/shop">View in shop / Add to cart ↗</a>
                        {% else %}
                        <button type="button" class="details-button" data-product-id="{{ product.id }}">View details ↗</button>
                        <button type="button" class="details-button add-cart-button" data-product-id="{{ product.id }}">Add to enquiry cart +</button>
                        {% endif %}
                    </div>
                </div>
            </div>
        </article>
        {% endfor %}
    </div>

    <div class="no-results" id="noResults">
        No matching catalogue items found. Try another search.
    </div>

    <div class="catalogue-note" style="
        margin-top:30px;
        padding:17px 19px;
        border-left:3px solid var(--cyan);
        color:#496170;
        background:#edf7f8;
        font-size:.78rem;
    ">
        <strong>Important:</strong>
        Product supply is subject to applicable laws, intended-use review,
        transport requirements, destination checks and documentation.
    </div>
</section>

<!-- ============================================================
     ABOUT / IMAGE SECTION
     ============================================================ -->
<section class="split-feature" id="about">
    <div class="split-photo" role="img" aria-label="Modern laboratory workspace"></div>

    <div class="split-copy">
        <div class="eyebrow">ABOUT GLOBAL CHEMICAL SOLUTION</div>
        <h2>Good supply starts with the right information.</h2>

        <p>
            Global Chemical Solution provides a professional point of
            contact for enquiries relating to selected industrial products
            and compatible packaging solutions.
        </p>

        <ul class="check-list">
            <li>Clear product and specification discussions</li>
            <li>Safety Data Sheet information on request</li>
            <li>Destination and transport requirements reviewed</li>
            <li>Professional communication throughout the enquiry</li>
        </ul>

        <a class="btn btn-dark" href="#contact">
            Speak With Our Team →
        </a>
    </div>
</section>

<!-- ============================================================
     HOW THE ENQUIRY PROCESS WORKS
     ============================================================ -->
<section class="section container" id="process">
    <div class="section-heading">
        <div>
            <div class="eyebrow">HOW WE WORK</div>
            <h2>A clear enquiry process</h2>
            <p class="section-intro">
                Product discussions should be based on accurate information,
                appropriate documentation and relevant legal checks.
            </p>
        </div>
    </div>

    <div class="process-grid">
        <article class="process-card">
            <div class="step">01</div>
            <h3>Share your enquiry</h3>
            <p>
                Tell us which catalogue item you are asking about, the
                intended professional application and the destination.
            </p>
        </article>

        <article class="process-card">
            <div class="step">02</div>
            <h3>Review specifications</h3>
            <p>
                Confirm the exact specification, grade, packaging and
                documentation needed for your enquiry.
            </p>
        </article>

        <article class="process-card">
            <div class="step">03</div>
            <h3>Compliance review</h3>
            <p>
                Any supply decision requires applicable legal, safety,
                transport and destination-country checks.
            </p>
        </article>
    </div>
</section>

<!-- ============================================================
     SAFETY AND DOCUMENTATION
     ============================================================ -->
<section class="section section-soft" id="safety">
    <div class="container">
        <div class="safety-panel">
            <div class="eyebrow eyebrow-light">RESPONSIBLE HANDLING</div>
            <h2>Safety information is part of every chemical conversation.</h2>

            <p>
                Always obtain and review the current Safety Data Sheet (SDS)
                for the exact product and grade. Website content is not a
                substitute for professional safety advice or official
                product documentation.
            </p>

            <div class="safety-points">
                <div class="safety-point">
                    <strong>01 — SDS</strong><br>
                    Request current product documentation.
                </div>
                <div class="safety-point">
                    <strong>02 — Compatibility</strong><br>
                    Verify container and material compatibility.
                </div>
                <div class="safety-point">
                    <strong>03 — Regulations</strong><br>
                    Check laws and transport rules for each destination.
                </div>
            </div>

            <a class="btn btn-primary" href="#contact">
                Request Documentation Information ↗
            </a>
        </div>
    </div>
</section>

<!-- ============================================================
     COMPANY INFORMATION CARDS
     ============================================================ -->
<section class="section container">
    <div class="section-heading">
        <div>
            <div class="eyebrow">OUR COMMITMENT</div>
            <h2>Professional standards</h2>
        </div>
    </div>

    <div class="info-grid">
        <article class="info-card">
            <div class="info-number">01</div>
            <h3>Clear communication</h3>
            <p>
                We aim to make product enquiries and documentation
                discussions clear and straightforward.
            </p>
        </article>

        <article class="info-card">
            <div class="info-number">02</div>
            <h3>Accurate information</h3>
            <p>
                Product details must be checked against the exact
                specification and supplier documentation.
            </p>
        </article>

        <article class="info-card">
            <div class="info-number">03</div>
            <h3>Responsible handling</h3>
            <p>
                Safe handling, storage and transport require current
                product-specific information and trained personnel.
            </p>
        </article>

        <article class="info-card">
            <div class="info-number">04</div>
            <h3>Regulatory awareness</h3>
            <p>
                Any product supply must meet applicable requirements in
                the origin, transit and destination jurisdictions.
            </p>
        </article>
    </div>
</section>

<!-- ============================================================
     ENQUIRY CART
     ============================================================ -->
<section class="section container" id="cart">
  <div class="section-heading"><div><div class="eyebrow">YOUR SELECTION</div><h2>Enquiry cart</h2><p class="section-intro">Add permitted catalogue items and submit your requirements for a quotation. Prices are confirmed individually; no prices are invented here.</p></div></div>
  <div style="background:#f3f7fa;border:1px solid #e3ebf0;border-radius:12px;padding:22px">
    <div id="cartItems"><p>Your enquiry cart is empty.</p></div>
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-top:15px">
      <strong id="cartCount">0 items selected</strong>
      <button type="button" class="btn btn-outline-dark" id="clearCart">Clear cart</button>
    </div>
  </div>
</section>

<!-- ============================================================
     CONTACT SECTION
     ============================================================ -->
<section class="section section-soft" id="contact">
    <div class="container contact-layout">
        <div>
            <div class="eyebrow">GET IN TOUCH</div>
            <h2>Let's discuss your requirements.</h2>

            <p class="section-intro">
                Send a product, specification or documentation enquiry.
                For an accurate response, include the intended application
                and destination country.
            </p>

            <div class="contact-details">
                <div class="contact-line">
                    <small>EMAIL ADDRESS</small>
                    <strong>{{ company.email }}</strong>
                </div>

                <div class="contact-line">
                    <small>PHONE / WHATSAPP</small>
                    <strong>{{ company.phone }}</strong>
                </div>

                <div class="contact-line">
                    <small>BUSINESS ADDRESS</small>
                    <strong>{{ company.address }}</strong>
                </div>
            </div>

            <a
                class="btn btn-outline-dark"
                href="https://wa.me/447983259218"
                target="_blank"
                rel="noopener"
            >
                Open WhatsApp ↗
            </a>
        </div>

        <form class="contact-form" method="POST" action="{{ url_for('home') }}#contact">
            <h3>Send an enquiry</h3>

            {% with messages = get_flashed_messages(with_categories=true) %}
                {% for category, message in messages %}
                <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endwith %}

            <div class="form-row">
                <div class="form-field">
                    <label for="name">Your name *</label>
                    <input id="name" name="name" required maxlength="100"
                           placeholder="Full name">
                </div>

                <div class="form-field">
                    <label for="email">Email address *</label>
                    <input id="email" name="email" type="email" required
                           maxlength="150" placeholder="you@example.com">
                </div>
            </div>

            <div class="form-field">
                <label for="subject">Subject *</label>
                <select id="subject" name="subject" required>
                    <option value="">Select enquiry type</option>
                    <option>Product specification</option>
                    <option>Safety Data Sheet</option>
                    <option>Packaging information</option>
                    <option>General business enquiry</option>
                </select>
            </div>

            <div class="form-row">
                <div class="form-field"><label for="phone">Phone / WhatsApp *</label><input id="phone" name="phone" required maxlength="40" placeholder="Your contact number"></div>
                <div class="form-field"><label for="city">City *</label><input id="city" name="city" required maxlength="100" placeholder="City"></div>
            </div>
            <div class="form-field"><label for="address">Delivery / Business Address *</label><input id="address" name="address" required maxlength="300" placeholder="Street, building, postcode"></div>
            <div class="form-field"><label for="country">Country *</label><input id="country" name="country" required maxlength="100" placeholder="Country"></div>
            <input type="hidden" id="selectedProducts" name="selected_products" value="[]">

            <div class="form-field">
                <label for="message">Message / Intended application *</label>
                <textarea
                    id="message"
                    name="message"
                    required
                    maxlength="3000"
                    placeholder="Tell us about your enquiry, intended application and destination country."
                ></textarea>
            </div>

            <button class="btn btn-primary" type="submit">
                Submit Enquiry ↗
            </button>

            <small class="form-note">Your enquiry is saved to the website database for the site owner to review. A quotation and supply eligibility are subject to product, destination and regulatory checks. Do not submit sensitive personal information.</small>
        </form>
    </div>
</section>

<!-- ============================================================
     CTA BAND
     ============================================================ -->
<section class="cta-band">
    <div class="container cta-inner">
        <div>
            <div class="eyebrow eyebrow-light">GLOBAL CHEMICAL SOLUTION</div>
            <h2>Need product information?</h2>
            <p>Our contact details are available for professional enquiries.</p>
        </div>
        <a class="btn btn-primary" href="#contact">
            Contact Our Team ↗
        </a>
    </div>
</section>
</main>

<!-- ============================================================
     FOOTER
     ============================================================ -->
<footer class="footer">
    <div class="container footer-grid">
        <div class="footer-brand">
            <a class="brand footer-brand" href="#home">
                <span class="brand-mark">GCS</span>
                <span>
                    GLOBAL CHEMICAL
                    <small>SOLUTION</small>
                </span>
            </a>
            <p>
                Professional enquiries for selected industrial products
                and compatible packaging solutions. Responsible information
                and safety documentation matter.
            </p>
        </div>

        <div class="footer-links">
            <h4>Explore Website</h4>
            <a href="#home">Home</a>
            <a href="#products">Product catalogue</a>
            <a href="#about">About us</a>
            <a href="#process">Our process</a>
            <a href="#safety">Safety information</a>
            <a href="#contact">Contact</a>
        </div>

        <div class="footer-contact">
            <h4>Contact Information</h4>
            <p>{{ company.email }}</p>
            <p>{{ company.phone }}</p>
            <p>{{ company.address }}</p>
        </div>
    </div>

    <div class="footer-bottom">
        <div class="container footer-bottom-inner">
            <span>© {{ year }} Global Chemical Solution. All rights reserved.</span>
            <span>Supply is subject to legal, safety and destination checks.</span>
        </div>
    </div>
</footer>

<!-- ============================================================
     PRODUCT DETAIL MODAL
     ============================================================ -->
<div
    class="modal-backdrop"
    id="productModal"
    role="dialog"
    aria-modal="true"
    aria-labelledby="modalTitle"
>
    <div class="product-modal">
        <button class="modal-close" id="modalClose" aria-label="Close dialog">
            ×
        </button>

        <div class="modal-content">
            <div class="modal-image">
                <img id="modalImage" src="" alt="">
            </div>

            <div class="modal-info">
                <span class="pill" id="modalCategory"></span>
                <h2 id="modalTitle">Product details</h2>
                <p id="modalDescription"></p>

                <h3>Product information</h3>
                <ul class="modal-specs" id="modalSpecs"></ul>

                <div class="modal-notice" id="modalNotice"></div>

                <a class="btn btn-primary" href="#contact" id="modalEnquiry">
                    Enquire about this product ↗
                </a>
            </div>
        </div>
    </div>
</div>

<button class="back-to-top" id="backToTop" aria-label="Back to top">↑</button>

<!-- ============================================================
     JAVASCRIPT DATA
     ============================================================ -->
<script>
const PRODUCTS = {{ products|tojson }};

/* ================================================================
   21. MOBILE NAVIGATION
   ================================================================ */

const menuButton = document.getElementById("menuButton");
const navLinks = document.getElementById("navLinks");

menuButton.addEventListener("click", function () {
    const isOpen = navLinks.classList.toggle("open");
    menuButton.setAttribute("aria-expanded", String(isOpen));
    menuButton.textContent = isOpen ? "×" : "☰";
});

navLinks.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
        navLinks.classList.remove("open");
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.textContent = "☰";
    });
});

/* ================================================================
   22. PRODUCT SEARCH AND CATEGORY FILTER
   ================================================================ */

const searchInput = document.getElementById("productSearch");
const filterButtons = document.querySelectorAll(".filter-button");
const productCards = document.querySelectorAll(".product-card");
const noResults = document.getElementById("noResults");

let activeCategory = "All";

function filterProducts() {
    const searchTerm = searchInput.value.trim().toLowerCase();
    let visibleCount = 0;

    productCards.forEach(function (card) {
        const productName = card.dataset.name || "";
        const productCategory = card.dataset.category || "";
        const matchesSearch = productName.includes(searchTerm);
        const matchesCategory =
            activeCategory === "All" ||
            productCategory === activeCategory;

        const shouldShow = matchesSearch && matchesCategory;

        card.classList.toggle("hidden", !shouldShow);

        if (shouldShow) {
            visibleCount += 1;
        }
    });

    noResults.style.display = visibleCount === 0 ? "block" : "none";
}

searchInput.addEventListener("input", filterProducts);

filterButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        filterButtons.forEach(function (item) {
            item.classList.remove("active");
        });

        button.classList.add("active");
        activeCategory = button.dataset.category;
        filterProducts();
    });
});

/* ================================================================
   23. PRODUCT DETAILS MODAL
   ================================================================ */

const modal = document.getElementById("productModal");
const modalClose = document.getElementById("modalClose");
const modalImage = document.getElementById("modalImage");
const modalCategory = document.getElementById("modalCategory");
const modalTitle = document.getElementById("modalTitle");
const modalDescription = document.getElementById("modalDescription");
const modalSpecs = document.getElementById("modalSpecs");
const modalNotice = document.getElementById("modalNotice");
const modalEnquiry = document.getElementById("modalEnquiry");

function openProductModal(productId) {
    const product = PRODUCTS.find(function (item) {
        return Number(item.id) === Number(productId);
    });

    if (!product) {
        return;
    }

    modalImage.src = product.image;
    modalImage.alt = product.name;
    modalCategory.textContent = product.category;
    modalTitle.textContent = product.name;
    modalDescription.textContent = product.description;
    modalNotice.textContent = product.notice;

    modalSpecs.innerHTML = "";

    product.specifications.forEach(function (specification) {
        const item = document.createElement("li");
        const label = document.createElement("strong");
        label.textContent = specification[0] + ": ";
        item.appendChild(label);
        item.appendChild(document.createTextNode(specification[1]));
        modalSpecs.appendChild(item);
    });

    modalEnquiry.dataset.productName = product.name;

    modal.classList.add("open");
    document.body.classList.add("modal-open");
    modalClose.focus();
}

function closeProductModal() {
    modal.classList.remove("open");
    document.body.classList.remove("modal-open");
}

document.querySelectorAll(".details-button").forEach(function (button) {
    button.addEventListener("click", function () {
        openProductModal(button.dataset.productId);
    });
});

modalClose.addEventListener("click", closeProductModal);

modal.addEventListener("click", function (event) {
    if (event.target === modal) {
        closeProductModal();
    }
});

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && modal.classList.contains("open")) {
        closeProductModal();
    }
});

modalEnquiry.addEventListener("click", function () {
    closeProductModal();
});

/* ================================================================
   24. BACK TO TOP BUTTON
   ================================================================ */

const backToTop = document.getElementById("backToTop");

window.addEventListener("scroll", function () {
    if (window.scrollY > 450) {
        backToTop.classList.add("visible");
    } else {
        backToTop.classList.remove("visible");
    }
});

backToTop.addEventListener("click", function () {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
});

/* ================================================================
   25. ACTIVE NAVIGATION LINK
   ================================================================ */

const pageSections = document.querySelectorAll("main section[id]");
const navAnchors = document.querySelectorAll(".nav-links a[href^='#']");

const sectionObserver = new IntersectionObserver(
    function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                navAnchors.forEach(function (anchor) {
                    anchor.classList.toggle(
                        "active",
                        anchor.getAttribute("href") === "#" + entry.target.id
                    );
                });
            }
        });
    },
    {
        rootMargin: "-35% 0px -55% 0px"
    }
);

pageSections.forEach(function (section) {
    sectionObserver.observe(section);
});

/* ================================================================
   26. IMAGE FALLBACK
   ================================================================ */

document.querySelectorAll("img").forEach(function (imageElement) {
    imageElement.addEventListener("error", function () {
        imageElement.style.opacity = "0.25";
        imageElement.alt = "Image unavailable — check internet connection";
    });
});

/* ================================================================
   ENQUIRY CART — browser-side selection
   ================================================================ */
const enquiryCart = {};
const cartItemsBox = document.getElementById("cartItems");
const cartCountLabel = document.getElementById("cartCount");
const selectedProductsInput = document.getElementById("selectedProducts");
function renderCart() {
    const ids = Object.keys(enquiryCart);
    cartItemsBox.innerHTML = "";
    if (!ids.length) { cartItemsBox.innerHTML = "<p>Your enquiry cart is empty.</p>"; }
    ids.forEach(function(id) {
        const row = document.createElement("div");
        row.style.cssText = "display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid #dce6ec;align-items:center;flex-wrap:wrap";
        const title = document.createElement("strong"); title.textContent = enquiryCart[id].name;
        const qty = document.createElement("span"); qty.textContent = "Quantity: " + enquiryCart[id].quantity;
        const controls = document.createElement("div"); controls.style.cssText = "display:flex;gap:8px;align-items:center";
        [["−",-1],["+",1],["Remove",0]].forEach(function(pair) {
            const b=document.createElement("button"); b.type="button"; b.textContent=pair[0]; b.className="details-button";
            b.addEventListener("click",function(){ if(pair[1]===0 || enquiryCart[id].quantity+pair[1]<1) delete enquiryCart[id]; else enquiryCart[id].quantity+=pair[1]; renderCart(); });
            controls.appendChild(b);
        });
        row.append(title, qty, controls); cartItemsBox.appendChild(row);
    });
    const total = ids.reduce((sum,id)=>sum+enquiryCart[id].quantity,0);
    cartCountLabel.textContent = total + (total===1 ? " item selected" : " items selected");
    selectedProductsInput.value = JSON.stringify(ids.map(id=>({id:Number(id),name:enquiryCart[id].name,quantity:enquiryCart[id].quantity})));
}
document.querySelectorAll(".add-cart-button").forEach(function(button){
    button.addEventListener("click",function(){
        const item=PRODUCTS.find(p=>Number(p.id)===Number(button.dataset.productId));
        if(!item) return;
        if(!enquiryCart[item.id]) enquiryCart[item.id]={name:item.name,quantity:0};
        enquiryCart[item.id].quantity++;
        renderCart();
        document.getElementById("cart").scrollIntoView({behavior:"smooth"});
    });
});
document.getElementById("clearCart").addEventListener("click",function(){ Object.keys(enquiryCart).forEach(k=>delete enquiryCart[k]); renderCart(); });
renderCart();

/* ================================================================
   27. CONTACT FORM FRONT-END CHECK
   ================================================================ */

const contactForm = document.querySelector(".contact-form");

contactForm.addEventListener("submit", function (event) {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const message = document.getElementById("message").value.trim();

    if (!name || !email || !message) {
        event.preventDefault();
        alert("Please complete all required fields.");
    }
});

/* ================================================================
   28. YEAR AND PAGE INITIALIZATION
   ================================================================ */

document.addEventListener("DOMContentLoaded", function () {
    filterProducts();
});

</script>
</body>
</html>
"""

# ---------------------------------------------------------------------
# ROUTE: HOME PAGE AND CONTACT FORM
# ---------------------------------------------------------------------

def init_db():
    db = sqlite3.connect("enquiries.db")
    db.execute("""CREATE TABLE IF NOT EXISTS enquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL,
        phone TEXT NOT NULL, address TEXT NOT NULL, city TEXT NOT NULL,
        country TEXT NOT NULL, subject TEXT NOT NULL, selected_products TEXT NOT NULL,
        message TEXT NOT NULL
    )""")
    db.commit()
    db.close()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        fields = {key: request.form.get(key, "").strip() for key in
                  ["name", "email", "phone", "address", "city", "country", "subject", "message"]}
        selected_raw = request.form.get("selected_products", "[]")
        try:
            selected = json.loads(selected_raw)
            if not isinstance(selected, list): raise ValueError
        except (ValueError, TypeError):
            selected = []
        valid_ids = {int(p["id"]) for p in PRODUCTS}
        clean_items = []
        for item in selected:
            try:
                pid, qty = int(item.get("id")), int(item.get("quantity"))
                if pid in valid_ids and 1 <= qty <= 1000:
                    product = next(p for p in PRODUCTS if int(p["id"]) == pid)
                    clean_items.append({"id": pid, "name": product["name"], "quantity": qty})
            except (AttributeError, TypeError, ValueError):
                continue
        if not all(fields.values()):
            flash("Please complete all required fields.", "error")
            return redirect(url_for("home") + "#contact")
        if len(fields["name"]) > 100 or len(fields["email"]) > 150 or len(fields["message"]) > 3000 or len(fields["address"]) > 300:
            flash("One or more fields are too long.", "error")
            return redirect(url_for("home") + "#contact")
        init_db()
        db = sqlite3.connect("enquiries.db")
        db.execute("""INSERT INTO enquiries
            (created_at,name,email,phone,address,city,country,subject,selected_products,message)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (datetime.utcnow().isoformat(), fields["name"], fields["email"], fields["phone"],
             fields["address"], fields["city"], fields["country"], fields["subject"],
             json.dumps(clean_items), fields["message"]))
        db.commit(); db.close()
        flash("Thank you. Your enquiry has been saved successfully. The team can review it and contact you.", "success")
        return redirect(url_for("home") + "#contact")

    homepage_products = list(PRODUCTS)
    try:
        with store_db() as db:
            rows = db.execute("SELECT * FROM store_products WHERE active=1 ORDER BY id DESC").fetchall()
        for row in rows:
            homepage_products.append({"id":100000+int(row["id"]), "slug":f"store-product-{row['id']}", "name":row["name"], "category":row["category"], "short":row["description"] or "Product details available on request.", "description":row["description"] or "Product details available on request.", "image":row["image"], "badge":"Available product", "specifications":[], "applications":[], "notice":"Confirm specifications and suitability before purchase.", "store_product":True, "store_id":int(row["id"]), "price":float(row["price"]), "currency":row["currency"], "currency_symbol":CURRENCY_INFO.get(row["currency"],{}).get("symbol",row["currency"]), "stock":int(row["stock"])})
    except (sqlite3.Error, NameError):
        pass
    return render_template_string(PAGE, company=COMPANY, products=homepage_products, categories=CATEGORIES, year=datetime.now().year)


# ---------------------------------------------------------------------
# ROUTE: SIMPLE HEALTH CHECK
# ---------------------------------------------------------------------

@app.route("/health")
def health():
    return {
        "status": "ok",
        "website": COMPANY["name"],
        "catalogue_items": len(PRODUCTS)
    }


# ---------------------------------------------------------------------
# ROUTE: NOT FOUND
# ---------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return (
        "<h1>Page not found</h1>"
        "<p>The page you requested does not exist.</p>"
        '<p><a href="/">Return to website</a></p>',
        404
    )


# ---------------------------------------------------------------------
# APPLICATION ENTRY POINT
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# GCS STORE + ADMIN PANEL (SQLite-backed)
# ---------------------------------------------------------------------
from flask import session, send_from_directory, abort
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from collections import defaultdict
import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORE_DB = os.path.join(BASE_DIR, "gcs_store.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
CURRENCY_INFO = {'GBP': {'name':'British Pound','symbol':'£'}, 'USD': {'name':'US Dollar','symbol':'$'}, 'EUR': {'name':'Euro','symbol':'€'}, 'PKR': {'name':'Pakistani Rupee','symbol':'Rs'}}
def money_label(code, amount=None):
    info=CURRENCY_INFO.get(code, {'name':code,'symbol':code})
    return f"{info['symbol']} {amount:,.2f} ({info['name']})" if amount is not None else f"{info['name']} ({info['symbol']})"
# BDO/GBL/GHB are intentionally excluded from this storefront.
RESTRICTED_TERMS = ("1,4-butanediol", "1,4 butanediol", "butanediol", "bdo", "gbl", "gamma-butyrolactone", "ghb")


def store_db():
    db = sqlite3.connect(STORE_DB)
    db.row_factory = sqlite3.Row
    return db


def init_store_db():
    with store_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS store_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            category TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
            price REAL NOT NULL DEFAULT 0, currency TEXT NOT NULL DEFAULT 'GBP',
            image TEXT NOT NULL DEFAULT '', stock INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT NOT NULL, phone TEXT NOT NULL DEFAULT '',
            address TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL,
            UNIQUE(email)
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, order_no TEXT UNIQUE NOT NULL,
            customer_id INTEGER NOT NULL, total REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'GBP', status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL, notes TEXT DEFAULT '',
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL,
            product_id INTEGER, product_name TEXT NOT NULL, quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL, FOREIGN KEY(order_id) REFERENCES orders(id)
        );
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        """)
        # Seed only ordinary packaging/industrial items; prices are editable by admin.
        count = db.execute("SELECT COUNT(*) FROM store_products").fetchone()[0]
        if count == 0:
            for item in PRODUCTS:
                db.execute("INSERT INTO store_products(name,category,description,price,currency,image,stock,active,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                    (item['name'], item['category'], item['description'], 0, 'GBP', item['image'], 0, 1, datetime.utcnow().isoformat()))
        if db.execute("SELECT COUNT(*) FROM admin_users").fetchone()[0] == 0:
            # Change these defaults immediately or set ADMIN_USERNAME / ADMIN_PASSWORD.
            username = os.environ.get('ADMIN_USERNAME', 'admin')
            password = os.environ.get('ADMIN_PASSWORD', 'ChangeMe-Now-2026!')
            db.execute("INSERT INTO admin_users(username,password_hash) VALUES(?,?)", (username, generate_password_hash(password)))

init_store_db()


def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get('admin_id'):
            return redirect(url_for('admin_login', next=request.path))
        return fn(*args, **kwargs)
    return wrapped


def blocked_catalogue_item(name, description=''):
    text = (name + ' ' + description).lower()
    return any(term in text for term in RESTRICTED_TERMS)

ADMIN_STYLE = """
<style>
*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#172b40;font:15px Arial,sans-serif}
a{color:#1768a5;text-decoration:none}.top{background:#10243b;color:white;padding:17px 5%;display:flex;justify-content:space-between;align-items:center}.wrap{width:min(1180px,92%);margin:28px auto}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:15px}.card,.panel{background:white;padding:20px;border-radius:12px;box-shadow:0 5px 22px #10243b12;margin-bottom:18px}.metric{font-size:28px;font-weight:bold;margin-top:8px}.muted{color:#718096}.btn,button{border:0;border-radius:7px;background:#1768a5;color:white;padding:10px 15px;cursor:pointer;display:inline-block}.btn.secondary{background:#64748b}.btn.danger{background:#b42332}input,textarea,select{width:100%;padding:11px;border:1px solid #d7e0e8;border-radius:7px;margin:5px 0 13px}label{font-weight:bold;font-size:13px}table{width:100%;border-collapse:collapse;background:white}th,td{text-align:left;padding:12px;border-bottom:1px solid #e7edf2}th{background:#f7f9fb}.table-wrap{overflow:auto}.row{display:grid;grid-template-columns:1fr 1fr;gap:14px}.actions{display:flex;gap:8px;flex-wrap:wrap}.product-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}.product img{width:100%;height:300px;object-fit:contain;object-position:center;background:#fff;border-radius:8px;padding:8px}.price{font-size:21px;font-weight:bold}.nav{display:flex;gap:16px;flex-wrap:wrap}.notice{padding:12px;background:#fff4df;border-radius:8px;margin:12px 0}@media(max-width:650px){.row{grid-template-columns:1fr}.top{align-items:flex-start;gap:12px;flex-direction:column}th,td{padding:8px}}
</style>"""


def page(title, body, **ctx):
    return render_template_string("""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{{title}} | GCS</title>""" + ADMIN_STYLE + """</head><body><header class='top'><b>GCS · {{title}}</b><nav class='nav'><a style='color:white' href='/'>Website</a><a style='color:white' href='/shop'>Shop & Cart</a><a style='color:white' href='/admin'>Dashboard</a>{% if session.get('admin_id') %}<a style='color:white' href='/admin/logout'>Logout</a>{% endif %}</nav></header><main class='wrap'>{% with messages=get_flashed_messages(with_categories=true) %}{% for category,message in messages %}<div class='notice'>{{message}}</div>{% endfor %}{% endwith %}""" + body + """</main></body></html>""", title=title, **ctx)


@app.route('/shop')
def shop():
    with store_db() as db:
        products = db.execute('SELECT * FROM store_products WHERE active=1 ORDER BY id DESC').fetchall()
    return page('Online Store', """
    <h1>Product catalogue</h1><p class='muted'>Add approved catalogue products to your cart. Checkout creates an order request for review.</p>
    <div class='product-grid'>{% for p in products %}<article class='card product'>
    {% if p.image %}<img src='{{p.image}}' alt='{{p.name}}'>{% endif %}<h3>{{p.name}}</h3><p class='muted'>{{p.category}}</p><p>{{p.description}}</p>
    <div class='price'>{% if p.price > 0 %}{{currency_symbols.get(p.currency, p.currency)}} {{'%.2f'|format(p.price)}} <small>({{p.currency}})</small>{% else %}Price on request{% endif %}</div>
    <p class='muted'>Stock shown: {{p.stock}}</p><form method='post' action='/cart/add'><input type='hidden' name='product_id' value='{{p.id}}'><label>Quantity</label><input name='quantity' type='number' min='1' max='50' value='1'><button>Add to cart</button></form></article>{% endfor %}</div>
    <section class='panel'><h2>Your cart</h2>{% if cart %}<form method='post' action='/cart/update'>{% for item in cart %}<p>{{item.name}} — {{item.quantity}} × {{item.price_label}} <button class='btn danger' name='remove' value='{{item.id}}'>Remove</button></p>{% endfor %}<button class='btn secondary'>Update cart</button></form><h3>Estimated total: {{total}}</h3><a class='btn' href='/checkout'>Proceed to checkout</a>{% else %}<p>Your cart is empty.</p>{% endif %}</section>
    """, products=products, cart=cart_view(), total=cart_total(), currency_symbols={k:v['symbol'] for k,v in CURRENCY_INFO.items()})


def cart_view():
    cart = session.get('cart', {})
    if not cart: return []
    ids = [int(k) for k in cart.keys()]
    with store_db() as db:
        rows = db.execute('SELECT * FROM store_products WHERE active=1 AND id IN (%s)' % ','.join('?'*len(ids)), ids).fetchall()
    result=[]
    for p in rows:
        q=max(1,min(50,int(cart.get(str(p['id']),1))))
        result.append({'id':p['id'],'name':p['name'],'quantity':q,'price':p['price'],'currency':p['currency'],'price_label':money_label(p['currency'],p['price']) if p['price']>0 else 'Price on request'})
    return result


def cart_total():
    items=cart_view()
    if not items or any(i['price'] <= 0 for i in items): return 'Confirmed after enquiry'
    return money_label(items[0]['currency'],sum(i['price']*i['quantity'] for i in items))


@app.post('/cart/add')
def cart_add():
    pid=request.form.get('product_id',''); qty=request.form.get('quantity','1')
    try: pid=int(pid); qty=max(1,min(50,int(qty)))
    except ValueError: return redirect('/shop')
    with store_db() as db: product=db.execute('SELECT * FROM store_products WHERE id=? AND active=1',(pid,)).fetchone()
    if not product: flash('Product unavailable.','error'); return redirect('/shop')
    cart=session.get('cart',{}); cart[str(pid)]=min(50,int(cart.get(str(pid),0))+qty); session['cart']=cart
    flash('Added to cart.','success'); return redirect('/shop')


@app.post('/cart/update')
def cart_update():
    cart=session.get('cart',{})
    remove=request.form.get('remove')
    if remove: cart.pop(str(remove),None)
    else:
        for k in list(cart):
            try: cart[k]=max(1,min(50,int(request.form.get('qty_'+k,cart[k]))))
            except ValueError: pass
    session['cart']=cart; return redirect('/shop')


@app.route('/checkout', methods=['GET','POST'])
def checkout():
    items=cart_view()
    if not items: return redirect('/shop')
    if request.method=='POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); phone=request.form.get('phone','').strip(); address=request.form.get('address','').strip()
        if not name or not email or '@' not in email or not phone or not address:
            flash('Please complete all checkout details.','error'); return redirect('/checkout')
        if any(i['price'] <= 0 for i in items):
            total=0.0
        else: total=sum(i['price']*i['quantity'] for i in items)
        with store_db() as db:
            db.execute('INSERT INTO customers(name,email,phone,address,created_at) VALUES(?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET name=excluded.name,phone=excluded.phone,address=excluded.address',(name,email,phone,address,datetime.utcnow().isoformat()))
            customer=db.execute('SELECT id FROM customers WHERE email=?',(email,)).fetchone()
            order_no='GCS-'+datetime.now().strftime('%y%m%d')+'-'+secrets.token_hex(3).upper()
            cur=db.execute('INSERT INTO orders(order_no,customer_id,total,currency,status,created_at) VALUES(?,?,?,?,?,?)',(order_no,customer['id'],total,'GBP','Pending',datetime.utcnow().isoformat()))
            for i in items: db.execute('INSERT INTO order_items(order_id,product_id,product_name,quantity,unit_price) VALUES(?,?,?,?,?)',(cur.lastrowid,i['id'],i['name'],i['quantity'],i['price']))
        session['cart']={}
        return page('Order received',"<div class='panel'><h1>Thank you — order request received</h1><p>Your order reference is <b>{{ref}}</b>.</p><p>Current status: Pending review. The team will confirm availability, delivery and any final price.</p><a class='btn' href='/order-status'>Track order</a></div>",ref=order_no)
    return page('Checkout',"""<h1>Checkout</h1><div class='panel'><h3>Order summary</h3>{% for i in items %}<p>{{i.name}} × {{i.quantity}} — {{i.price_label}}</p>{% endfor %}<h3>{{total}}</h3></div><form class='panel' method='post'><label>Full name</label><input name='name' required><label>Email</label><input type='email' name='email' required><label>Phone / WhatsApp</label><input name='phone' required><label>Delivery address</label><textarea name='address' required></textarea><button>Place order request</button></form>""",items=items,total=cart_total())


@app.route('/order-status',methods=['GET','POST'])
def order_status():
    orders=[]
    if request.method=='POST':
        email=request.form.get('email','').strip().lower(); ref=request.form.get('order_no','').strip()
        with store_db() as db:
            orders=db.execute('SELECT o.*,c.name FROM orders o JOIN customers c ON c.id=o.customer_id WHERE lower(c.email)=? AND o.order_no=?',(email,ref)).fetchall()
    return page('Track your order',"""<h1>Track your order</h1><form class='panel' method='post'><label>Order reference</label><input name='order_no' required><label>Checkout email</label><input type='email' name='email' required><button>Check order</button></form>{% for o in orders %}<div class='panel'><h3>{{o.order_no}}</h3><p>Status: <b>{{o.status}}</b></p><p>Total: {{o.currency}} {{'%.2f'|format(o.total) if o.total else 'To be confirmed'}}</p><p>Placed: {{o.created_at}}</p></div>{% else %}{% if request.method=='POST' %}<p>No matching order found. Check the reference and email.</p>{% endif %}{% endfor %}""",orders=orders)


@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        username=request.form.get('username',''); password=request.form.get('password','')
        with store_db() as db: user=db.execute('SELECT * FROM admin_users WHERE username=?',(username,)).fetchone()
        if user and check_password_hash(user['password_hash'],password):
            session['admin_id']=user['id']; session['admin_name']=user['username']
            return redirect(request.args.get('next') or url_for('admin_dashboard'))
        flash('Invalid username or password.','error')
    return page('Admin login',"""<div class='panel' style='max-width:450px;margin:auto'><h1>Admin login</h1><form method='post'><label>Username</label><input name='username' required><label>Password</label><input name='password' type='password' required><button>Login securely</button></form><p class='muted'>Default local demo: admin / ChangeMe-Now-2026! — change immediately.</p></div>""")


@app.get('/admin/logout')
def admin_logout():
    session.clear(); return redirect('/admin/login')


@app.get('/admin')
@admin_required
def admin_dashboard():
    with store_db() as db:
        products=db.execute('SELECT COUNT(*) FROM store_products').fetchone()[0]
        orders=db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
        customers=db.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
        sales=db.execute("SELECT COALESCE(SUM(total),0) FROM orders WHERE status IN ('Paid','Completed','Shipped')").fetchone()[0]
        recent=db.execute('SELECT o.*,c.name,c.email FROM orders o JOIN customers c ON c.id=o.customer_id ORDER BY o.id DESC LIMIT 8').fetchall()
        monthly=db.execute("SELECT strftime('%Y-%m',created_at) month, SUM(total) revenue FROM orders WHERE status IN ('Paid','Completed','Shipped') GROUP BY month ORDER BY month DESC LIMIT 6").fetchall()
    labels=[r['month'] for r in reversed(monthly)]; values=[r['revenue'] for r in reversed(monthly)]
    return page('Admin dashboard',"""
    <h1>Business overview</h1><div class='grid'><div class='card'>Products<div class='metric'>{{products}}</div></div><div class='card'>Orders<div class='metric'>{{orders}}</div></div><div class='card'>Customers<div class='metric'>{{customers}}</div></div><div class='card'>Recognized sales<div class='metric'>GBP {{'%.2f'|format(sales)}}</div></div></div>
    <div class='panel'><div class='actions'><a class='btn' href='/admin/products'>Manage products</a><a class='btn' href='/admin/orders'>Orders & sales</a><a class='btn' href='/admin/customers'>Customers</a><a class='btn secondary' href='/order-status'>Customer order tracking</a></div></div>
    <div class='panel'><h2>Monthly sales graph</h2><canvas id='salesChart' height='100'></canvas></div><div class='panel'><h2>Recent orders</h2><div class='table-wrap'><table><tr><th>Order</th><th>Customer</th><th>Total</th><th>Status</th><th>Date</th></tr>{% for o in recent %}<tr><td><a href='/admin/orders/{{o.id}}'>{{o.order_no}}</a></td><td>{{o.name}}<br><small>{{o.email}}</small></td><td>{{o.currency}} {{'%.2f'|format(o.total)}}</td><td>{{o.status}}</td><td>{{o.created_at[:10]}}</td></tr>{% endfor %}</table></div></div>
    <script src='https://cdn.jsdelivr.net/npm/chart.js'></script><script>new Chart(document.getElementById('salesChart'),{type:'line',data:{labels:{{labels|tojson}},datasets:[{label:'Sales (GBP)',data:{{values|tojson}},borderWidth:3,tension:.3}]},options:{responsive:true}});</script>
    """,products=products,orders=orders,customers=customers,sales=sales,recent=recent,labels=labels,values=values)


@app.route('/admin/products',methods=['GET','POST'])
@admin_required
def admin_products():
    if request.method=='POST':
        name=request.form.get('name','').strip(); category=request.form.get('category','').strip(); desc=request.form.get('description','').strip()
        try: price=float(request.form.get('price','0')); stock=max(0,int(request.form.get('stock','0')))
        except ValueError: flash('Invalid price or stock.','error'); return redirect('/admin/products')
        if not name or not category or price<0 or blocked_catalogue_item(name,desc):
            flash('Invalid product. This catalogue accepts approved lawful goods only.','error'); return redirect('/admin/products')
        image_url=request.form.get('image_url','').strip()
        file=request.files.get('image')
        if file and file.filename:
            filename=secure_filename(file.filename); ext=filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
            if ext not in ALLOWED_IMAGE_EXTENSIONS: flash('Image must be PNG, JPG, WEBP or GIF.','error'); return redirect('/admin/products')
            filename=secrets.token_hex(8)+'_'+filename; file.save(os.path.join(UPLOAD_DIR,filename)); image_url='/static_uploads/'+filename
        with store_db() as db: db.execute('INSERT INTO store_products(name,category,description,price,currency,image,stock,active,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(name,category,desc,price,request.form.get('currency','GBP'),image_url,stock,1,datetime.utcnow().isoformat()))
        flash('Product added.','success'); return redirect('/admin/products')
    with store_db() as db: products=db.execute('SELECT * FROM store_products ORDER BY id DESC').fetchall()
    return page('Product manager',"""
    <h1>Product manager</h1><div class='panel'><h2>Add product</h2><form method='post' enctype='multipart/form-data'><div class='row'><div><label>Product name</label><input name='name' required><label>Category</label><input name='category' required></div><div><label>Price</label><input type='number' name='price' min='0' step='.01' value='0' required><label>Currency</label><select name='currency'><option value="GBP">GBP — British Pound (£)</option><option value="USD">USD — US Dollar ($)</option><option value="EUR">EUR — Euro (€)</option><option value="PKR">PKR — Pakistani Rupee (Rs)</option></select></div></div><label>Description</label><textarea name='description'></textarea><div class='row'><div><label>Stock quantity</label><input type='number' name='stock' min='0' value='0'></div><div><label>Image upload</label><input type='file' name='image' accept='.png,.jpg,.jpeg,.webp,.gif'><label>Or image URL</label><input name='image_url'></div></div><button>Add product to shop</button></form></div>
    <div class='panel'><h2>Current products</h2><div class='table-wrap'><table><tr><th>Product</th><th>Price</th><th>Stock</th><th>Visibility</th><th>Actions</th></tr>{% for p in products %}<tr><td>{{p.name}}<br><small>{{p.category}}</small></td><td>{{currency_symbols.get(p.currency, p.currency)}} {{'%.2f'|format(p.price)}} <small>({{p.currency}})</small></td><td>{{p.stock}}</td><td>{{'Active' if p.active else 'Hidden'}}</td><td><a href='/admin/products/{{p.id}}/edit'>Edit</a> · <form style='display:inline' method='post' action='/admin/products/{{p.id}}/toggle'><button class='btn secondary'>{{'Hide' if p.active else 'Show'}}</button></form></td></tr>{% endfor %}</table></div></div>
    """,products=products,currency_symbols={k:v['symbol'] for k,v in CURRENCY_INFO.items()})


@app.route('/admin/products/<int:pid>/edit',methods=['GET','POST'])
@admin_required
def admin_product_edit(pid):
    with store_db() as db: product=db.execute('SELECT * FROM store_products WHERE id=?',(pid,)).fetchone()
    if not product: abort(404)
    if request.method=='POST':
        name=request.form.get('name','').strip(); desc=request.form.get('description','').strip()
        if not name or blocked_catalogue_item(name,desc): flash('Invalid product details.','error'); return redirect(request.url)
        try: price=max(0,float(request.form.get('price','0'))); stock=max(0,int(request.form.get('stock','0')))
        except ValueError: flash('Invalid price or stock.','error'); return redirect(request.url)
        image_url=product['image']; file=request.files.get('image')
        if file and file.filename:
            filename=secure_filename(file.filename); ext=filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
            if ext not in ALLOWED_IMAGE_EXTENSIONS: flash('Image must be PNG, JPG, WEBP or GIF.','error'); return redirect(request.url)
            filename=secrets.token_hex(8)+'_'+filename; file.save(os.path.join(UPLOAD_DIR,filename)); image_url='/static_uploads/'+filename
        with store_db() as db: db.execute('UPDATE store_products SET name=?,category=?,description=?,price=?,currency=?,stock=?,active=?,image=? WHERE id=?',(name,request.form.get('category','').strip(),desc,price,request.form.get('currency','GBP'),stock,1 if request.form.get('active')=='1' else 0,image_url,pid))
        flash('Product updated.','success'); return redirect('/admin/products')
    return page('Edit product',"""<h1>Edit product</h1><form class='panel' method='post' enctype='multipart/form-data'><label>Name</label><input name='name' value='{{p.name}}' required><label>Category</label><input name='category' value='{{p.category}}'><label>Description</label><textarea name='description'>{{p.description}}</textarea><div class='row'><div><label>Price</label><input name='price' type='number' step='.01' min='0' value='{{p.price}}'></div><div><label>Currency</label><select name='currency'><option value="{{p.currency}}">{{p.currency}}</option><option value="GBP">GBP — British Pound (£)</option><option value="USD">USD — US Dollar ($)</option><option value="EUR">EUR — Euro (€)</option><option value="PKR">PKR — Pakistani Rupee (Rs)</option></select></div></div><label>Stock</label><input name='stock' type='number' min='0' value='{{p.stock}}'><label>Replace product image (optional)</label><input type='file' name='image' accept='.png,.jpg,.jpeg,.webp,.gif'>{% if p.image %}<img src='{{p.image}}' style='width:100%;max-height:300px;object-fit:contain;background:#fff'>{% endif %}<label>Visibility</label><select name='active'><option value='1' {{'selected' if p.active else ''}}>Active</option><option value='0' {{'selected' if not p.active else ''}}>Hidden</option></select><button>Save changes</button></form>""",p=product)


@app.post('/admin/products/<int:pid>/toggle')
@admin_required
def admin_product_toggle(pid):
    with store_db() as db: db.execute('UPDATE store_products SET active=CASE active WHEN 1 THEN 0 ELSE 1 END WHERE id=?',(pid,))
    return redirect('/admin/products')


@app.get('/admin/orders')
@admin_required
def admin_orders():
    with store_db() as db: orders=db.execute('SELECT o.*,c.name,c.email,c.phone FROM orders o JOIN customers c ON c.id=o.customer_id ORDER BY o.id DESC').fetchall()
    return page('Orders and sales',"""<h1>Orders & sales report</h1><div class='panel table-wrap'><table><tr><th>Reference</th><th>Customer</th><th>Amount</th><th>Status</th><th>Date</th></tr>{% for o in orders %}<tr><td><a href='/admin/orders/{{o.id}}'>{{o.order_no}}</a></td><td>{{o.name}}<br>{{o.email}}<br>{{o.phone}}</td><td>{{o.currency}} {{'%.2f'|format(o.total)}}</td><td>{{o.status}}</td><td>{{o.created_at[:16]}}</td></tr>{% endfor %}</table></div>""",orders=orders)


@app.route('/admin/orders/<int:oid>',methods=['GET','POST'])
@admin_required
def admin_order_detail(oid):
    with store_db() as db:
        order=db.execute('SELECT o.*,c.name,c.email,c.phone,c.address FROM orders o JOIN customers c ON c.id=o.customer_id WHERE o.id=?',(oid,)).fetchone()
        if not order: abort(404)
        if request.method=='POST':
            status=request.form.get('status','Pending')
            if status not in ('Pending','Confirmed','Paid','Processing','Shipped','Completed','Cancelled'): abort(400)
            db.execute('UPDATE orders SET status=?,notes=? WHERE id=?',(status,request.form.get('notes','')[:1000],oid)); return redirect(request.url)
        items=db.execute('SELECT * FROM order_items WHERE order_id=?',(oid,)).fetchall()
    return page('Order details',"""<h1>{{o.order_no}}</h1><div class='panel'><h3>Customer details</h3><p>{{o.name}} · {{o.email}} · {{o.phone}}</p><p>{{o.address}}</p><h3>Items</h3>{% for i in items %}<p>{{i.product_name}} × {{i.quantity}} @ {{o.currency}} {{'%.2f'|format(i.unit_price)}}</p>{% endfor %}<h3>Total: {{o.currency}} {{'%.2f'|format(o.total)}}</h3><form method='post'><label>Order status</label><select name='status'>{% for st in ['Pending','Confirmed','Paid','Processing','Shipped','Completed','Cancelled'] %}<option {{'selected' if st==o.status else ''}}>{{st}}</option>{% endfor %}</select><label>Internal notes</label><textarea name='notes'>{{o.notes}}</textarea><button>Update order</button></form></div>""",o=order,items=items)


@app.get('/admin/customers')
@admin_required
def admin_customers():
    with store_db() as db: customers=db.execute('SELECT c.*,COUNT(o.id) order_count,COALESCE(SUM(o.total),0) lifetime FROM customers c LEFT JOIN orders o ON o.customer_id=c.id GROUP BY c.id ORDER BY c.id DESC').fetchall()
    return page('Customers',"""<h1>Customer directory</h1><div class='panel table-wrap'><table><tr><th>Name</th><th>Contact</th><th>Address</th><th>Orders</th><th>Order value</th></tr>{% for c in customers %}<tr><td>{{c.name}}</td><td>{{c.email}}<br>{{c.phone}}</td><td>{{c.address}}</td><td>{{c.order_count}}</td><td>GBP {{'%.2f'|format(c.lifetime)}}</td></tr>{% endfor %}</table></div>""",customers=customers)


@app.get('/static_uploads/<path:filename>')
def uploaded_image(filename):
    return send_from_directory(UPLOAD_DIR, filename)


if __name__ == "__main__":
    # debug=True is for local development only.
    # Turn debug off in production and use a production WSGI server.
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "5000")), debug=os.environ.get("FLASK_DEBUG", "0") == "1")
