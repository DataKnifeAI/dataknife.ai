# dataknife.ai

Portfolio site for [DataKnifeAI](https://github.com/DataKnifeAI), served at [dataknife.ai](https://dataknife.ai) from GitHub Pages.

- `index.html` — mission, north star, featured work, build layers, recent activity, principles
- `projects.html` — every public original repository, filterable by category

Mission and principles copy follows the org profile in [DataKnifeAI/.github](https://github.com/DataKnifeAI/.github/blob/main/profile/README.md). Colors come from the org logo.

## Project catalog

`projects.json` lists original public repositories. Forks and private repositories are omitted. A GitLab link is included only when the mirror under [dk-raas/dkai](https://gitlab.com/dk-raas/dkai) is public.

The Pages workflow regenerates it on every push and once a day, so "In motion" on the home page tracks recent pushes. The committed copy is the fallback if that step fails.

Refresh locally:

```bash
python3 scripts/sync_catalog.py
```

Uses `GITHUB_TOKEN` if set, otherwise `gh auth token`. Categories, status labels, and live URLs are set at the top of the script.

## Preview

```bash
python3 -m http.server 8765
```

## DNS

The domain is on Cloudflare with four DNS-only A records for the apex (`185.199.108.153` through `185.199.111.153`). The `CNAME` file sets the Pages hostname to `dataknife.ai`.
