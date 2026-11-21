# UN Women → cinfoPoste RSS

A small converter that reads the **official UN Women RSS 1.0 (RDF)** and publishes **RSS 2.0** containing only current international P- and D-grade staff vacancies.

Official source: https://jobs.undp.org/rss_feeds/UNWomen.xml

## Setup using the GitHub website

1. In the GitHub organization **cinfoposte**, create a new **public** repository named **unwomen-jobs** (initialize it with README, if prompted).
2. Upload `build_feed.py` to the repository root. If you already created a README, you can keep it.
3. Create a file named `.github/workflows/update.yml` and paste the contents of this kit's workflow file. Commit it to the **main** branch.
4. Open **Actions → Update UN Women RSS → Run workflow**. The workflow should generate `unwomen_jobs.xml` at the repository root. If there is an error, open the workflow log; do not continue until fixed.
5. Open **Settings → Pages**, choose **Deploy from a branch**, **main**, **/(root)**, and save. On a normal GitHub Pages configuration, the expected URL is:
   `https://cinfoposte.github.io/unwomen-jobs/unwomen_jobs.xml`
   **Do not assume it works until the URL displays `<rss version="2.0">` and item records.**
6. In ARCA choose company **UN Women** and paste this new URL as a **new** feed (do not keep the unfiltered old import active in parallel). Under `Organize RSS`, map `ITEM=Start item`, `TITLE=Title`, `LINK=Link`, `DESCRIPTION=Description`, `GUID=Unique ID`, `PUBDATE=Date`, and all channel-only/other fields to `None`.
7. Import only after checking the first vacancy. Make sure every vacancy has the correct title and link and that no duplicates or old jobs are created.

Notes:
- No external libraries or tokens are required by this code. The workflow needs permission to push changes (`contents: write`). If Actions cannot push, check the repository's Actions workflow permissions or branch protections.
- This depends on the official source being available. If it fails, the workflow shows a failure and leaves the last published XML untouched.
- The source only contains a short description (grade and deadline), **not the complete job description**. Applicants should use the original vacancy link.
- This is automatic collection, **not** a certified ARCA integration; confirm with a controlled test.
