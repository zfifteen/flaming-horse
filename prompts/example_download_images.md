**Task: Search, Verify, and Download Valid Geometric Factorization Images**

Search online for exactly three high-quality, accessible JPG/JPEG images (no PNG, SVG, or other formats) related to "geometric factorization" (e.g., area models, box methods, or diagrams for polynomial factoring). Use reliable, stable educational sources like Wikimedia Commons, MathsIsFun, Khan Academy, or .edu sites to avoid broken links.

**Requirements:**

1. **Search Query:** "geometric factorization diagram JPG" or similar, prioritizing educational visuals.
2. **Number of Images:** Exactly 3.
3. **File Formats:** Strictly JPG/JPEG only; reject and replace any non-JPG.
4. **Image Quality:** Medium to high resolution (at least 500px in one dimension; verify dimensions post-download using `sips -g pixelWidth -g pixelHeight file.jpg` on macOS).
5. **Sources:** Stable sites (e.g., upload.wikimedia.org, www.mathsisfun.com, www.khanacademy.org); avoid Google Images redirects or temporary links.
6. **Download Location:** `assets/` (create if needed with `mkdir -p assets`).
7. **Filename Convention:** Descriptive, lowercase with underscores (e.g., `geometric_factorization_area_model.jpg`).
8. **Download and Verification Method:**
    - Use the `task` tool with `explore` subagent (thoroughness: "very thorough") to find and pre-verify URLs: For each URL, use `webfetch` or `curl -I` via `bash` to check HTTP 200 status, Content-Type: image/jpeg, and Content-Length >20KB.
    - Download one-by-one using `wget -O filename URL` via `bash`.
    - After each download, immediately verify with `bash`: `ls -la filename` (size >20KB) and `file filename` (must output "JPEG image data"). If invalid (0 bytes, wrong format, or error), discard, search for a new URL, and retry until valid.
    - Only proceed to the next image after the current one passes verification. Do not batch downloads without per-file checks.
    - If all three fail after 3 retries each, stop and report the issue without false confirmation.
9. **Error Handling:** Log any 404s, redirects, or failures in bash output. Never claim success until all files are verified valid.

**Expected Output:**
- Exactly three valid JPG files in `assets/` with sizes >20KB and confirmed as JPEG.
- Final confirmation message listing filenames, sizes, and resolutions only after all verifications pass. If unable, explain failures and suggest alternatives.