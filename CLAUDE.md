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

## Deployment

Pushes to `master` trigger a GitHub Actions workflow (`.github/workflows/build.yml`) that builds and deploys to GitHub Pages.

## Project structure

- `_posts/` — blog posts in Markdown (named `YYYY-MM-DD-slug.md`)
- `_layouts/` — page templates (`default.html`, `post.html`, `landing.html`, `home.html`, `page.html`)
- `assets/css/main.css` — site styles
- `index.html` — landing page
- `posts.html` — post index
- `_config.yml` — Jekyll config (permalink: `/posts/:title.html`)

## Linting, formatting, and testing

There are no linters, formatters, or test suites configured for this project. Validate changes by running `bundle exec jekyll build` and checking the dev server output.

## Workflow

After every change: validate with `bundle exec jekyll build`, then commit and push to `master`.
