# Vulnerable Demo App

## ⚠️ WARNING: This repository intentionally contains vulnerable dependencies!

This repo is created for testing **DDHM (Dynamic Dependency Health Monitor)**.

## Vulnerable Packages Included:

| Package | Version | Why It's Vulnerable |
|---------|---------|---------------------|
| Flask | 0.12.2 | Old version with known security issues |
| requests | 2.18.0 | Vulnerable to redirect attacks |
| urllib3 | 1.21.1 | Multiple CVEs |
| PyJWT | 1.5.0 | CVE-2022-29217 |
| cryptography | 2.1.4 | Multiple CVEs |
| numpy | 1.14.0 | CVE-2019-6446 |
| aiohttp | 2.3.0 | CVE-2018-1000528 |

## Purpose

Test DDHM's ability to:
1. Detect vulnerable dependencies
2. Generate accurate fix suggestions
3. Show risk score improvement

## How to Test

1. Enter this repo URL in DDHM
2. Review the risk scores
3. Apply suggested fixes
4. Re-scan to see improvement
