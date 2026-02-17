#!/bin/bash

# Normalize markdown filenames in current directory
# Converts to lowercase, replaces spaces with underscores,
# removes special characters, handles conflicts with numbering

for file in *.md; do
    # Skip if no .md files exist
    [ -e "$file" ] || continue

    # Skip if already normalized (no changes needed)
    basename="${file%.md}"

    # Normalize: lowercase, spaces to underscores, remove special chars
    normalized=$(echo "$basename" | \
        tr '[:upper:]' '[:lower:]' | \
        tr ' ' '_' | \
        sed 's/[^a-z0-9_]//g' | \
        sed 's/__*/_/g' | \
        sed 's/^_//; s/_$//')

    new_name="${normalized}.md"

    # Skip if name unchanged
    [ "$file" = "$new_name" ] && continue

    # Handle conflicts by appending numbers
    if [ -e "$new_name" ]; then
        counter=1
        while [ -e "${normalized}_${counter}.md" ]; do
            ((counter++))
        done
        new_name="${normalized}_${counter}.md"
    fi

    mv "$file" "$new_name"
    echo "Renamed: $file -> $new_name"
done
