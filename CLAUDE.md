# CLAUDE.md - AI Assistant Guide for Seattle Urbanism Guide

## Project Overview

This is a **Hugo static site** serving as a practical reference guide for Seattle urbanists and advocates. It helps people understand urban planning issues, learn terminology, and prepare for community participation.

- **Site URL**: https://seattle.urbanism-guide.com/
- **Theme**: hugo-book (git submodule at `themes/hugo-book/`)
- **Hugo Version**: 0.147.0 (extended)
- **License**: MIT

## Directory Structure

```
urbanism-guide/
├── archetypes/           # Content templates for new pages
│   ├── blog.md          # Blog post template
│   ├── glossary.md      # Glossary entry template
│   └── default.md       # Generic page template
├── content/              # All Markdown content (main working area)
│   ├── _index.md        # Homepage
│   ├── quick-start/     # Seattle governance & context
│   ├── glossary/        # Terminology by category (4 files)
│   ├── guides/          # In-depth topic guides (bike network, micro mobility, etc.)
│   ├── timeline/        # Historical events section
│   └── blog/            # Analysis posts
├── data/                 # Structured data files
│   └── timeline.yaml    # Timeline entries (year, title, description, sources)
├── layouts/              # Custom Hugo templates
│   ├── partials/        # Template includes (head injection for CSS)
│   └── shortcodes/      # timeline.html, blog-list.html
├── static/               # Static assets served as-is
│   └── css/timeline.css # Custom styling for timeline and blog
├── themes/hugo-book/     # External theme (git submodule - DO NOT EDIT)
├── scripts/              # Build and validation scripts
│   └── validate-timeline.py  # Ensures timeline is in reverse chronological order
├── .github/workflows/    # CI/CD automation
│   ├── deploy.yml       # Production deployment to gh-pages
│   ├── pr-preview.yml   # PR preview builds
│   └── pr-preview-cleanup.yml
├── hugo.toml             # Main Hugo configuration
├── .htmltest.yml         # Link validation config
└── README.md             # User-facing documentation
```

## Quick Commands

```bash
# Local development server (includes drafts)
hugo server -D

# Production build
hugo --gc --minify

# Validate timeline order (run before committing timeline changes)
python3 scripts/validate-timeline.py

# Create new blog post
hugo new blog/my-post-title.md

# Create new glossary entry
hugo new glossary/category/term-name.md
```

## Content Editing Guidelines

### Glossary Entries (`content/glossary/`)

Four category files exist:
- `housing-zoning.md` - ADU, DADU, FAR, MHA, upzoning, etc.
- `transportation.md` - LOS, mode share, complete streets, etc.
- `land-use.md` - SEPA, comprehensive plan, GMA, etc.
- `funding-policy.md` - TIF, MFTE, impact fees, etc.

**Format for new terms**:
```markdown
### Term Name

Brief definition in plain language.

**Why it matters:** Explain relevance to Seattle urbanists.

**See also:** [Related Term](#related-term)

**Learn more:** [Primary Source](url) | [Secondary Source](url)
```

**Source requirements for glossary terms:**
- **Primary source (required):** Must be a governmental or official institutional source (e.g., seattle.gov, soundtransit.org, wsdot.wa.gov, mrsc.org, commerce.wa.gov)
- **Secondary source (preferred):** The Urbanist (theurbanist.org) when relevant coverage exists, or other reputable local journalism/policy sources (Sightline, Publicola, Seattle Times)

### Timeline Entries (`data/timeline.yaml`)

Entries are in **reverse chronological order** (newest first). Each entry:

```yaml
- year: 2024
  title: "Event Title"
  description: "What happened and why it matters."
  legacy: "Long-term impact or current relevance."
  sources:
    primary:
      text: "Source Name"
      url: "https://..."
    secondary:
      text: "Additional Source"
      url: "https://..."
```

### Topic Guides (`content/guides/`)

Guides are in-depth pages covering a specific urbanism topic in Seattle. Each guide lives as a single Markdown file in `content/guides/`.

**Existing guides:**
- `micro-mobility.md` - E-scooters, bike share, operators, permits, data
- `bike-network.md` - Protected bike lanes, neighborhood greenways, trails

**Front matter:**
```yaml
---
title: "Guide Title"
weight: 3          # Controls sidebar order (1 = first)
bookToc: true      # Enables right-side table of contents
---
```

**Standard section structure** (follow this order; omit sections that don't apply):

```markdown
# Topic Name in Seattle

Introductory paragraph: what this is and why it matters. 1-3 sentences.

## Current state / types / operators
Overview of how things work today. Use ### subheadings for categories.

## History
Chronological ### subheadings (e.g., "### 2014: Bicycle Master Plan update").
Cover key milestones from origin to present. Include inline source links.

## How the city manages / plans / funds it
Permitting, planning frameworks, funding sources, selection criteria.

## Advocacy organizations (if applicable)
Bullet list of key orgs with links and one-line descriptions.

## Data sources
Where to find official data: city dashboards, open data portals, APIs, maps.

## Key statistics
Markdown table with current metrics. Cite sources below the table.

## Related resources
Cross-links to other guides (use relref) and relevant external pages.

---

*Last updated: Month Year*
```

**Writing style:**
- Practical and factual; write for someone preparing for a public hearing or community meeting
- Use **bold** for program names, organization names, and key terms on first mention
- Inline source citations as Markdown links, not footnotes
- Prefer seattle.gov, sdotblog.seattle.gov, soundtransit.org, mrsc.org as primary sources
- Use The Urbanist (theurbanist.org) or other local journalism as secondary sources
- Every claim with a number or date should have a source link

**Source requirements for guides:**
- **Primary sources (required):** Government or official institutional sources (seattle.gov, sdotblog.seattle.gov, wsdot.wa.gov, mrsc.org, commerce.wa.gov, soundtransit.org)
- **Secondary sources (preferred):** The Urbanist, Seattle Bike Blog, Cascade PBS, Sightline, GeekWire, Publicola
- **Advocacy/org sources (acceptable for org-specific claims):** cascade.org, seattlegreenways.org, etc.
- **Verify every URL** with WebFetch or the link checker before committing

**After creating a new guide**, update `content/guides/_index.md` to add an entry under "Available Guides":
```markdown
- [Guide Title]({{< relref "file-name" >}}) -- Short description
```

### Blog Posts (`content/blog/`)

Use the archetype: `hugo new blog/post-title.md`

Front matter includes:
- `title`, `date`, `tags`, `categories`, `summary`
- `draft: true` by default (remove or set false to publish)

## Key Configuration (hugo.toml)

- **Base URL**: `https://seattle.urbanism-guide.com/`
- **Theme settings**: Auto dark/light mode, TOC enabled, search enabled
- **Markup**: Goldmark with unsafe HTML allowed (for shortcodes)
- **Menu weights**: Quick Start (1), Glossary (2), Timeline (3), Blog (4)

## Custom Components

### Timeline Shortcode
`{{</* timeline */>}}` renders `data/timeline.yaml` as an interactive timeline with source citations.

### Blog List Shortcode
`{{</* blog-list */>}}` auto-generates a list of blog posts with dates, tags, and summaries.

## Build and Deployment

### Automated (GitHub Actions)
- **Push to main**: Validates timeline order, builds, validates links via htmltest, deploys to gh-pages
- **Pull requests**: Validates timeline order, creates preview at `/pr-preview/{PR_NUMBER}/`
- **PR close**: Cleans up preview directory

### Timeline Validation
`scripts/validate-timeline.py` runs before every build to ensure timeline entries are in reverse chronological order. The build will fail if entries are out of order.

### Link Validation
`.htmltest.yml` checks internal and external links. External link failures don't block builds (15s timeout).

## Important Conventions

1. **Every factual claim needs a source**: All claims, facts, statistics, dates, and assertions in content must have an inline linked source. No unsourced statements -- if you can't find a source for a claim, don't include it. Use inline Markdown links (not footnotes) to cite sources directly where the claim appears.

2. **Theme is read-only**: Never edit files in `themes/hugo-book/`. Override via `layouts/` or `static/`.

3. **Content format**: All content is Markdown with YAML front matter. Keep it portable.

4. **Timeline sources required**: New timeline entries should include at least a primary source with URL.

5. **Chronology**: Timeline entries in `data/timeline.yaml` are ordered newest-first.

6. **Draft content**: Set `draft: true` in front matter for work-in-progress. Use `hugo server -D` to preview.

7. **No node_modules by default**: The project is pure Hugo unless package.json is added for asset processing.

8. **Verify links before adding**: Always use WebFetch to verify that external URLs are valid before adding them to content. The CI runs `python3 scripts/check-external-links.py` which will fail the build on broken links. To check all links locally, run:
   ```bash
   python3 scripts/check-external-links.py
   ```

## Git Workflow

- Main branch: `main`
- Feature branches for changes
- PRs get automatic preview builds
- Merge triggers production deployment

## Common Tasks for AI Assistants

### Adding a glossary term
1. Identify the correct category file in `content/glossary/`
2. Add the term in alphabetical order within the file
3. Follow the "Term Name / Definition / Why it matters / See also / Learn more" format
4. **Verify all URLs using WebFetch before adding them** to ensure they return valid content (not 404s)
5. Include a primary governmental source and secondary source (preferably The Urbanist) in the "Learn more" section

### Adding a timeline event
1. Edit `data/timeline.yaml`
2. Insert at the correct position (reverse chronological - newer entries first)
3. Include year, title, description, legacy, and at least one source
4. **Verify all source URLs using WebFetch before adding them** to ensure they return valid content (not 404s)
5. Run `python3 scripts/validate-timeline.py` to verify order before committing

### Creating a new topic guide
1. Read an existing guide (e.g., `content/guides/micro-mobility.md` or `content/guides/bike-network.md`) to match the tone and structure
2. Create a new file at `content/guides/topic-name.md` with the standard front matter (`title`, `weight`, `bookToc: true`)
3. Follow the standard section structure: current state, history, city management/planning, advocacy orgs, data sources, key statistics table, related resources
4. Research content using WebSearch; aim for a mix of government sources and journalism
5. **Verify every external URL** using WebFetch or `python3 scripts/check-external-links.py` before committing
6. Add cross-links: link to related glossary pages using `{{< relref "/glossary/category" >}}` and to other guides using `{{< relref "guide-name" >}}`
7. Update `content/guides/_index.md` to add the new guide under "Available Guides"
8. End the page with `*Last updated: Month Year*`

### Creating a blog post
1. Run `hugo new blog/post-title.md` or manually create file
2. Fill in front matter (title, date, tags, summary)
3. Set `draft: false` when ready to publish

### Modifying styles
1. Edit `static/css/timeline.css` for timeline/blog styling
2. Dark mode: Use `@media (prefers-color-scheme: dark)` queries
3. Mobile: Breakpoint at 600px width

### Testing locally
```bash
hugo server -D  # Starts at http://localhost:1313/
```

## File Size Reference

- Content: ~10 markdown files, 379 lines in glossary alone
- Timeline: 14+ entries, 203 lines YAML
- Custom CSS: 179 lines
- Total repository: ~706 KB

## External Resources

- Hugo documentation: https://gohugo.io/documentation/
- hugo-book theme: https://github.com/alex-shpak/hugo-book
- htmltest: https://github.com/wjdp/htmltest
