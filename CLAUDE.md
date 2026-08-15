# CLAUDE.md

## Project overview

sourceless.org — a personal blog built with Jekyll, hosted on GitHub Pages.

## Development environment

This repo uses a **Nix flake** for dev tooling. Enter the dev shell with:

```
nix develop
```

Or automatically via **direnv** (`.envrc` contains `use flake`). The shell provides Ruby 3.3, bundler, and native dependencies. Gems install to `.gem/` in the project root.

## Common commands

- **Dev server:** `bundle exec jekyll serve` (serves at localhost:4000)
- **Build:** `bundle exec jekyll build` (outputs to `_site/`)
- **Install deps:** `bundle install`
- **Regenerate social cards:** `python tools/generate_og_images.py`

## Deployment

Pushes to `master` trigger a GitHub Actions workflow (`.github/workflows/build.yml`) that builds and deploys to GitHub Pages.

## Project structure

- `_posts/` — blog posts in Markdown (named `YYYY-MM-DD-slug.md`)
- `_layouts/` — page templates (`default.html`, `post.html`, `landing.html`, `home.html`, `page.html`)
- `assets/css/main.css` — site styles
- `assets/og/` — generated Open Graph cards, one per post plus `default.png`
- `tools/generate_og_images.py` — renders those cards
- `index.html` — landing page
- `posts.html` — post index
- `_config.yml` — Jekyll config (permalink: `/posts/:title.html`)

## Linting, formatting, and testing

There are no linters, formatters, or test suites configured for this project. Validate changes by running `bundle exec jekyll build` and checking the dev server output.

## Post artwork

Every post has a Julia set fractal seeded from a SHA-256 of its body text,
rendered by `tools/generate_og_images.py` and committed under `assets/og/`. Four
files per post, since the site has both themes and the index needs something
small:

- `<slug>.png` — 1200x630 dark, used as the `og:image` and the post banner
- `<slug>-light.png` — the light-theme banner
- `<slug>-thumb.png` / `<slug>-thumb-light.png` — 96x96 for the post index

Banners come from `_includes/post-banner.html`, thumbnails from
`_includes/post-list.html`. Both pass the two variants as CSS custom properties
so `main.css` can swap them per theme; a `<picture>` element would not work here,
because the theme toggle sets a `data-theme` attribute rather than relying on
`prefers-color-scheme` alone.

**After adding a post, or editing the body of an existing one, re-run the
generator and commit the result.** The GitHub Pages build runs Jekyll in safe
mode, so this cannot be a Jekyll plugin. A missing file is a broken image rather
than a build failure, so it will not show up as a failed deploy.

## Workflow

After every change: validate with `bundle exec jekyll build`, then commit and push to `master`.
