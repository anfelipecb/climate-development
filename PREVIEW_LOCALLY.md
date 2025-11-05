# Preview Your HTML Story Locally

Before deploying to GitHub Pages, you can preview your HTML story locally in your browser.

## Quick Preview Methods

### Method 1: Python HTTP Server (Recommended)

Open a terminal and run:

```bash
cd "/Users/anfelipecb/Library/CloudStorage/Box-Box/MSCAPP/4th quarter/Data Visualization/static-project/static_viz"
python3 -m http.server 8000
```

Then open your browser and go to:
```
http://localhost:8000/
```

Press `Ctrl+C` in the terminal to stop the server when you're done.

### Method 2: Direct File Open

Simply double-click the `index.html` file in Finder, or:

```bash
open "/Users/anfelipecb/Library/CloudStorage/Box-Box/MSCAPP/4th quarter/Data Visualization/static-project/static_viz/index.html"
```

**Note:** Some features (like certain fonts) may work better with Method 1.

## What to Check

When previewing, verify:
- ✅ Chicago maroon header appears and stays fixed when scrolling
- ✅ Table of contents on the left highlights the current section as you scroll
- ✅ All images load correctly
- ✅ Text is readable and properly formatted
- ✅ Responsive design works (try resizing your browser window)
- ✅ All links in the table of contents work

## Making Changes

If you need to make changes:
1. Edit `static_viz/index.html` in your preferred text editor
2. Save the file
3. Refresh your browser (⌘+R on Mac, Ctrl+R on Windows)

Enjoy previewing your beautiful research story! 🎨

