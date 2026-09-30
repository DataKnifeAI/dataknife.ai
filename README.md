# dataknife.ai

Public project index for [DataKnifeAI](https://github.com/DataKnifeAI).

The site lists original public repositories. Forks and private repositories are omitted. A GitLab link is included only when the mirror under [dk-raas/dkai](https://gitlab.com/dk-raas/dkai) is public.

## Refresh the catalog

```bash
python3 scripts/sync_catalog.py
```

Requires `gh` logged in with access to the DataKnifeAI org, and `glab` logged in to gitlab.com.

## DNS

The domain is on Cloudflare. Point the apex at GitHub Pages:

| Type | Name | Value |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |

Leave the records DNS-only (grey cloud) until GitHub finishes certificate provisioning. The `CNAME` file in this repo sets the Pages hostname to `dataknife.ai`.
