# CLAUDE.md - AI Assistant Guide for Seattle Urbanism Guide

## Project Overview

This is a **Hugo static site** serving as a practical reference guide for Seattle urbanists and advocates. It helps people understand urban planning issues, learn terminology, and prepare for community participation.

- **Site URL**: https://prestomation.github.io/urbanism-guide/
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

### Blog Posts (`content/blog/`)

Use the archetype: `hugo new blog/post-title.md`

Front matter includes:
- `title`, `date`, `tags`, `categories`, `summary`
- `draft: true` by default (remove or set false to publish)

## Key Configuration (hugo.toml)

- **Base URL**: `https://prestomation.github.io/urbanism-guide/`
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
- **Push to main**: Builds, validates links via htmltest, deploys to gh-pages
- **Pull requests**: Creates preview at `/pr-preview/{PR_NUMBER}/`
- **PR close**: Cleans up preview directory

### Link Validation
`.htmltest.yml` checks internal and external links. External link failures don't block builds (15s timeout).

## Important Conventions

1. **Theme is read-only**: Never edit files in `themes/hugo-book/`. Override via `layouts/` or `static/`.

2. **Content format**: All content is Markdown with YAML front matter. Keep it portable.

3. **Timeline sources required**: New timeline entries should include at least a primary source with URL.

4. **Chronology**: Timeline entries in `data/timeline.yaml` are ordered newest-first.

5. **Draft content**: Set `draft: true` in front matter for work-in-progress. Use `hugo server -D` to preview.

6. **No node_modules by default**: The project is pure Hugo unless package.json is added for asset processing.

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
4. Include a primary governmental source and secondary source (preferably The Urbanist) in the "Learn more" section

### Adding a timeline event
1. Edit `data/timeline.yaml`
2. Insert at the correct position (reverse chronological - newer entries first)
3. Include year, title, description, legacy, and at least one source

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
hugo server -D  # Starts at http://localhost:1313/urbanism-guide/
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
