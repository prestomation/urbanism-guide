# Architecture: Centralizing the Urbanism Guide Platform

## Problem

Three repos — `urbanism-guide` (Seattle), `bothell-urbanism-guide`, and `lakewood-urbanism-guide` — share the same concept, site structure, and tooling but duplicate all infrastructure. When a workflow bug is fixed, a shortcode improved, or CSS polished, the change must be manually replicated across every repo. New city guides require copying an entire repo and surgically removing Seattle-specific content.

## Goals

1. **A new city guide requires only content and a small config file.** No workflows, no layouts, no scripts to copy.
2. **Centralized updates flow automatically.** Fix a shortcode or workflow once, every city benefits on next build.
3. **Escape hatches at every layer.** Any city can override layouts, CSS, workflows, or scripts without forking the core.
4. **No vendor lock-in.** Everything uses Hugo-native features (modules, config merge) and GitHub-native features (reusable workflows).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  urbanism-guide-core  (central repo)                    │
│                                                         │
│  ├── layouts/          shortcodes, partials, baseof     │
│  ├── static/css/       framework.css (component styles) │
│  ├── archetypes/       blog, glossary, guide templates  │
│  ├── scripts/          validate-timeline, check-links   │
│  ├── .github/workflows/ reusable deploy, preview, clean │
│  ├── hugo.toml          shared defaults (markup, ToC)   │
│  └── go.mod             Hugo module definition          │
└──────────────────┬──────────────────────────────────────┘
                   │  imported by Hugo module system
                   │  called by reusable workflows
                   ▼
┌─────────────────────────────────────────────────────────┐
│  seattle-urbanism-guide  (city repo)                    │
│                                                         │
│  ├── content/          all markdown (guides, glossary…) │
│  ├── data/             timeline.yaml                    │
│  ├── static/css/       brand.css (CSS variable values)  │
│  ├── hugo.toml         city config (baseURL, title,     │
│  │                     colors, analytics, module import) │
│  ├── .github/workflows/ thin callers → core workflows   │
│  └── CLAUDE.md         city-specific AI instructions    │
└─────────────────────────────────────────────────────────┘
```

## Layer 1: Hugo Module (`urbanism-guide-core`)

Hugo modules (built on Go modules) let one repo provide layouts, static files, archetypes, and assets to another. The importing repo's local files always take precedence, giving free override capability.

### What the core module provides

| Directory | Contents | Override mechanism |
|---|---|---|
| `layouts/_default/baseof.html` | Base HTML structure with injection points | City drops a file at same path |
| `layouts/shortcodes/` | `timeline.html`, `blog-list.html` | City creates same-named shortcode |
| `layouts/partials/docs/inject/` | `head.html`, `body.html`, `search.html` | City creates same-named partial |
| `static/css/framework.css` | All component styles using CSS variables | City adds `brand.css` or overrides `framework.css` |
| `archetypes/` | `blog.md`, `glossary.md`, `default.md` | City creates same-named archetype |
| `scripts/` | `validate-timeline.py`, `check-external-links.py` | City provides own scripts dir |

### Core `hugo.toml` (shared defaults only)

```toml
# urbanism-guide-core/hugo.toml
# These are defaults — city repos override via config merge.

theme = "hugo-book"
uglyURLs = false
enableGitInfo = true
enableEmoji = true

[params]
  BookTheme = "auto"
  BookToC = true
  BookSection = "*"
  BookDateFormat = "January 2, 2006"
  BookSearch = false
  BookComments = false
  BookPortableLinks = true

[params.bookToc]
  startLevel = 2
  endLevel = 4

[markup]
  [markup.goldmark.renderer]
    unsafe = true
  [markup.tableOfContents]
    startLevel = 2
    endLevel = 4
    ordered = false
  [markup.highlight]
    style = "github"

[outputs]
  home = ["HTML", "RSS"]
  section = ["HTML", "RSS"]

[taxonomies]
  tag = "tags"
  category = "categories"
```

### Core `go.mod`

```
module github.com/prestomation/urbanism-guide-core

go 1.21

require github.com/alex-shpak/hugo-book v0.0.0  // the theme
```

This means the core module *also* imports hugo-book, so city repos don't need to manage the theme submodule at all.

### City `hugo.toml` (Seattle example)

```toml
baseURL = "https://seattle.urbanism-guide.com/"
languageCode = "en-us"
title = "Seattle Urbanism Guide"

[params]
  description = "A practical guide for Seattle urbanists and advocates."
  goatCounterCode = "seattle-urbanism-guide"
  BookRepo = "https://github.com/prestomation/seattle-urbanism-guide"
  BookEditPath = "edit/main/content"
  # City-specific brand colors (used in body.html analytics partial)
  cityName = "Seattle"
  timezone = "America/Los_Angeles"

[module]
  [[module.imports]]
    path = "github.com/prestomation/urbanism-guide-core"
```

That's it. Hugo automatically mounts `layouts/`, `static/`, `archetypes/`, `data/`, `i18n/`, and `assets/` from the imported module. Local files in the city repo take precedence over module files, so any override is just "drop a file at the same path."

## Layer 2: CSS Theming

Split the current monolithic `timeline.css` into two concerns:

### `framework.css` (in core module → `static/css/framework.css`)

Contains all component styles — typography, timeline, blog list, homepage cards, sidebar, tables, blockquotes, search, responsive breakpoints. References CSS custom properties for all colors:

```css
/* All color values come from variables — never hardcoded */
:root {
  /* Defaults (overridden by brand.css) */
  --color-link: #0046AD;
  --accent-teal: #00839A;
  --accent-emerald: #A3D559;
  --accent-gold: #FECB00;
  --accent-light-blue: #63B1E5;
  --accent-gradient: linear-gradient(135deg, var(--color-link), var(--accent-teal));
  --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
  --card-shadow-hover: 0 4px 12px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
  --border-radius: 0.5rem;
}
```

### `brand.css` (in city repo → `static/css/brand.css`)

Only CSS variable definitions. Minimal file that any non-developer can edit:

```css
/* Seattle brand colors — from seattle.gov brand guidelines */
:root {
  --color-link: #0046AD;
  --accent-teal: #00839A;
  --accent-emerald: #A3D559;
  --accent-gold: #FECB00;
  --accent-light-blue: #63B1E5;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-link: #63B1E5;
    --accent-teal: #2CC8D9;
    --accent-emerald: #B8E07C;
    --accent-gold: #FFD84D;
    --accent-light-blue: #8DC8ED;
  }
}
```

The `head.html` partial in the core loads `framework.css` first, then `brand.css` second, so city variables win via cascade.

### Escape hatch

A city can replace `framework.css` entirely by placing their own at `static/css/framework.css`. Or they can add a `static/css/custom.css` and add it to `head.html` via a local override of that partial.

## Layer 3: Reusable GitHub Actions Workflows

GitHub supports [reusable workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows) via `workflow_call`. The core repo defines parameterized workflow templates. City repos have thin caller workflows.

### Core reusable workflows

#### `.github/workflows/deploy.yml`

```yaml
# urbanism-guide-core/.github/workflows/deploy.yml
name: Deploy Hugo Site

on:
  workflow_call:
    inputs:
      hugo_version:
        type: string
        default: "0.147.0"
      timezone:
        type: string
        default: "America/Los_Angeles"
      base_url:
        description: "Site base URL (read from hugo.toml if not provided)"
        type: string
        default: ""
      run_timeline_validation:
        type: boolean
        default: true
      run_link_check:
        type: boolean
        default: true

permissions:
  contents: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Install Hugo CLI
        run: |
          wget -O ${{ runner.temp }}/hugo.deb \
            https://github.com/gohugoio/hugo/releases/download/v${{ inputs.hugo_version }}/hugo_extended_${{ inputs.hugo_version }}_linux-amd64.deb \
          && sudo dpkg -i ${{ runner.temp }}/hugo.deb

      - name: Install Dart Sass
        run: sudo snap install dart-sass

      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Hugo modules
        run: hugo mod get

      - name: Install Node.js dependencies
        run: "[[ -f package-lock.json || -f npm-shrinkwrap.json ]] && npm ci || true"

      - name: Validate timeline order
        if: inputs.run_timeline_validation
        run: |
          # Use city's script if present, otherwise fetch from module
          if [ -f scripts/validate-timeline.py ]; then
            python3 scripts/validate-timeline.py
          else
            hugo mod vendor
            python3 _vendor/github.com/prestomation/urbanism-guide-core/scripts/validate-timeline.py
          fi

      - name: Build with Hugo
        env:
          HUGO_CACHEDIR: ${{ runner.temp }}/hugo_cache
          HUGO_ENVIRONMENT: production
          TZ: ${{ inputs.timezone }}
        run: hugo --gc --minify

      - name: Build search index
        run: npx pagefind --site public

      - name: Validate internal links
        if: inputs.run_link_check
        run: |
          curl -sSL https://github.com/wjdp/htmltest/releases/download/v0.17.0/htmltest_0.17.0_linux_amd64.tar.gz | tar xz -C /tmp
          /tmp/htmltest --conf .htmltest.yml

      - name: Deploy to gh-pages
        run: |
          # ... (same deployment logic, no city-specific values)
```

#### `.github/workflows/pr-preview.yml`

Same pattern — accepts `base_url` as input to construct the preview URL. The PR comment step reads the base URL from inputs.

#### `.github/workflows/pr-preview-cleanup.yml`

Identical logic, fully generic already.

### City caller workflows

Each city repo has thin 10-line caller workflows:

```yaml
# seattle-urbanism-guide/.github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: ["main"]
  workflow_dispatch:

jobs:
  deploy:
    uses: prestomation/urbanism-guide-core/.github/workflows/deploy.yml@main
    with:
      timezone: "America/Los_Angeles"
```

```yaml
# seattle-urbanism-guide/.github/workflows/pr-preview.yml
name: PR Preview
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  preview:
    uses: prestomation/urbanism-guide-core/.github/workflows/deploy-preview.yml@main
    with:
      base_url: "https://seattle.urbanism-guide.com"
```

### Escape hatches

- **Override a workflow entirely:** Don't call the reusable workflow; write a custom one.
- **Add pre/post steps:** Add a wrapper job in the caller that runs before/after the core workflow.
- **Pin a version:** Use `@v1.2.0` instead of `@main` to lock to a known-good version of core.
- **Toggle features:** Use the boolean inputs (`run_timeline_validation: false`) to skip steps that don't apply.

## Layer 4: Scripts

### Default: Scripts live in the core module

The reusable workflows vendor the Hugo module and run scripts from it. City repos don't need to copy `validate-timeline.py` or `check-external-links.py`.

### Override: City provides its own script

The workflow checks for a local `scripts/` directory first. If a city has custom validation needs (e.g., Bothell doesn't use the timeline feature), they can either:
- Put a no-op script at `scripts/validate-timeline.py`
- Set `run_timeline_validation: false` in the caller workflow

## Layer 5: Content Structure Convention

The core module doesn't dictate content structure, but it provides **archetypes** and **shortcodes** that assume a convention:

| Content convention | Enforced by |
|---|---|
| `content/glossary/` with category files | Archetype + shortcode assumptions |
| `content/guides/` with per-topic files | Archetype naming |
| `content/blog/` section | `blog-list.html` shortcode queries this section |
| `content/timeline/` page using `{{</* timeline */>}}` | Shortcode reads `data/timeline.yaml` |
| `data/timeline.yaml` in reverse chronological order | `validate-timeline.py` script |

Cities are free to not use any of these. The blog-list shortcode gracefully handles an empty blog section. The timeline shortcode handles missing data. Validation steps can be disabled.

### Optional: Starter content

The core repo could include a `starters/` directory (not mounted by Hugo) with template content files:

```
starters/
├── content/
│   ├── _index.md            # Homepage template with {CITY_NAME} placeholders
│   ├── glossary/_index.md
│   ├── guides/_index.md
│   ├── blog/_index.md
│   └── timeline/_index.md
├── data/
│   └── timeline.yaml        # Empty example
├── static/css/
│   └── brand.css            # Template with color placeholders
└── hugo.toml                # Template config
```

A setup script or `hugo new site` hook could scaffold a new city from these templates.

## What a New City Repo Looks Like

Minimal file tree for a new `tacoma-urbanism-guide`:

```
tacoma-urbanism-guide/
├── content/
│   ├── _index.md                    # Tacoma homepage
│   ├── glossary/
│   │   └── housing-zoning.md        # Tacoma-relevant terms
│   ├── guides/
│   │   └── light-rail.md            # Tacoma Link extension
│   └── timeline/
│       └── _index.md                # {{</* timeline */>}}
├── data/
│   └── timeline.yaml                # Tacoma history
├── static/css/
│   └── brand.css                    # Tacoma city colors
├── .github/workflows/
│   ├── deploy.yml                   # 10 lines → calls core
│   ├── pr-preview.yml               # 10 lines → calls core
│   └── pr-preview-cleanup.yml       # 10 lines → calls core
├── hugo.toml                        # ~20 lines (baseURL, title, module import)
├── go.mod                           # Hugo module declaration
├── .htmltest.yml                    # Can import from core or keep local
├── CLAUDE.md                        # City-specific AI instructions
└── README.md
```

Total scaffolding: ~6 files, ~80 lines of config. Everything else is content.

## Migration Plan

### Phase 1: Create the core repo

1. Create `prestomation/urbanism-guide-core` repository
2. Move shared infrastructure from `urbanism-guide`:
   - `layouts/` (all shortcodes, partials, baseof.html)
   - `static/css/timeline.css` → rename to `static/css/framework.css`, extract variables
   - `archetypes/`
   - `scripts/`
3. Set up as Hugo module (`go.mod` with hugo-book dependency)
4. Convert workflows to reusable (`workflow_call` triggers with inputs)
5. Add `.htmltest.yml` as a shipped default
6. Tag `v1.0.0`

### Phase 2: Migrate Seattle repo

1. Remove `themes/hugo-book` submodule (core module handles this now)
2. Remove `layouts/`, `archetypes/`, `scripts/` (now from core)
3. Add `go.mod` importing `urbanism-guide-core`
4. Create `static/css/brand.css` with Seattle colors
5. Slim `hugo.toml` to city-specific values only
6. Replace workflow files with thin callers
7. Verify build locally with `hugo server -D`
8. Verify all three workflows work (deploy, preview, cleanup)

### Phase 3: Migrate Bothell and Lakewood

Same steps as Phase 2 — should be mechanical at this point.

### Phase 4: Scaffold tooling (optional)

Create a `create-city-guide` script or GitHub template repository that generates the minimal city repo structure with prompts for city name, base URL, and brand colors.

## Escape Hatch Summary

| Layer | Default behavior | How to override |
|---|---|---|
| **Layouts** | From core module | Drop same-path file in city repo |
| **CSS variables** | Core defaults (Seattle blue) | `brand.css` in city repo |
| **CSS components** | `framework.css` from core | Replace with local `framework.css` or add `custom.css` |
| **Shortcodes** | `timeline.html`, `blog-list.html` from core | Same-named shortcode in city repo |
| **Workflows** | Reusable from core, called by thin wrappers | Write a full custom workflow instead |
| **Workflow steps** | All steps enabled | Boolean inputs to toggle (e.g., `run_timeline_validation: false`) |
| **Workflow version** | `@main` (latest) | Pin to `@v1.2.0` tag |
| **Scripts** | From core module (vendored) | Local `scripts/` directory takes precedence |
| **Hugo config** | Core provides defaults | City `hugo.toml` merges on top |
| **Theme** | hugo-book via core module | City can import a different theme |
| **Content structure** | Convention (glossary/, guides/, blog/) | No enforcement — shortcodes degrade gracefully |
| **Archetypes** | From core module | Local archetype overrides |

## Versioning and Update Strategy

- **Core repo uses semver tags** (`v1.0.0`, `v1.1.0`, `v2.0.0`).
- City repos can pin to a tag for stability or track `@main` for latest.
- **Breaking changes** (layout structure changes, removed shortcodes, renamed CSS variables) bump the major version.
- **Additions** (new shortcodes, new CSS components) bump minor.
- **Fixes** (bug fixes, workflow improvements) bump patch.
- Hugo module updates in city repos: `hugo mod get -u github.com/prestomation/urbanism-guide-core` to pull latest.
- Dependabot can be configured on city repos to auto-PR when core updates.

## Alternatives Considered

### Git submodule for shared code
Rejected. Submodules create friction (init, update, detached HEAD states). Hugo modules are purpose-built for this and handle dependency resolution natively.

### Monorepo with all cities
Rejected. Coupling between cities creates merge conflicts, permission issues, and means contributors to one city see irrelevant changes from others. Separate repos with a shared dependency is cleaner.

### Fork-based workflow
Rejected. Forks diverge. Upstream changes require cherry-picking. Three months in, every fork has drifted and nobody updates.

### npm package for shared code
Rejected. Adds Node.js as a dependency for what is otherwise a pure Hugo project. Hugo modules are the native solution.

### GitHub template repository (alone)
Insufficient. Templates are a one-time copy — no ongoing updates. Good as a supplement (for scaffolding) but not a replacement for the module approach.
