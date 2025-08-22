# writer-tech-base

Base set of tools to organize writing into chapters or scenes and provide build scripts to create .DOCX, .RTF, HTML, and PDF outputs from Markdown sources.

## Project Overview

This repository acts as a template for fiction projects.  It keeps the story in plain Markdown files and offers simple scripts to combine them into complete manuscripts.  The goal is to let writers focus on text while still producing polished documents at any stage of the process.

## Getting Started

1. Fork or clone this repository when beginning a new story.
2. Create a `content/` directory and place your chapter or scene files there.  Use one `.md` file per unit of writing.
3. Describe the order of those files and any metadata in `book.yml`.
4. Run the provided build scripts to generate output formats such as HTML, PDF, DOCX, or RTF using [Pandoc](https://pandoc.org/).

### Example Layout
```
content/
  01-title-page.md
  02-chapter-01.md
  03-chapter-02.md
book.yml
```

### Configuration (`book.yml`)

The configuration file lists your manuscript pieces and options:

```
title: My Novel
author: Jane Doe
parts:
  - file: 01-title-page.md
    new_page: true
  - file: 02-chapter-01.md
    new_page: true
```

`new_page` can be used to start sections on their own page in formats that support it.

### Building Outputs

The project includes cross-platform shell scripts (bash/zsh) and a simple `Makefile` to generate documents:

```
make html   # Creates output/manuscript.html
make pdf    # Creates output/manuscript.pdf
make docx   # Creates output/manuscript.docx
make rtf    # Creates output/manuscript.rtf
```

The scripts aim to run on Linux, macOS, or Windows via Git Bash or WSL.  Ensure [Pandoc](https://pandoc.org/) is installed and on your `PATH`.

### Workflow Tips

- Use Git to track revisions and explore alternate branches for scenes.
- Any Markdown editor works; [Visual Studio Code](https://code.visualstudio.com/) provides helpful extensions.
- Run builds at any time to preview progress in different formats.

### Future Enhancements

This base setup is intentionally minimal.  Future versions may add e-book targets, AI-assisted tools, or deeper IDE integration.  Contributions and ideas are welcome!

