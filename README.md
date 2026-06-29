# 60 Seconds Smarter — Entertaining Shorts Pipeline

This version makes more entertaining YouTube Shorts instead of a static text card.

It now includes:

- multi-scene storytelling
- fast hook-first structure
- animated Ken Burns style backgrounds
- topic-matched illustrated visuals
- big TikTok-style captions
- timestamps and progress bar
- sound effects on transitions
- generated background music bed
- metadata files with title, description, hashtags, and tags
- optional OpenAI script/scene generation
- optional YouTube upload as private/unlisted/public

## Upload structure

Your repo root must contain:

```text
.github/workflows/make-short.yml
src/
data/
requirements.txt
run_pipeline.py
README.md
```

Do not upload the outer ZIP folder itself. Upload the contents.

## Run it

Go to:

```text
Actions → Make and Upload YouTube Short → Run workflow
```

For testing use:

```text
upload = false
privacy = private
```

After the run finishes, download the `generated-short` artifact. It will contain:

- `.mp4` video
- `.wav` narration
- `.json` metadata
- generated sound effects

## Optional OpenAI scripts

Add this GitHub secret for better scripts and scene planning:

```text
OPENAI_API_KEY
```

Without it, the project still works using built-in fallback scripts.

## YouTube upload

Add these GitHub secrets after setting up OAuth:

```text
YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN
```

Then run the workflow with:

```text
upload = true
privacy = private
```

Keep uploads private first. Review each video before publishing.

## Improve content

Edit:

```text
data/topics.json
```

Add evergreen, high-curiosity facts. Best formats:

- "Why can't you stand on a neutron star?"
- "The island nobody is allowed to visit"
- "The shortest war in history lasted minutes"
- "This animal can survive extreme environments"

## Important

This system automates production. It does not guarantee views or monetization. Use it to create original, useful Shorts, then improve based on retention and comments.
