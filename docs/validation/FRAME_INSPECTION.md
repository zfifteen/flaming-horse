# Frame Inspection Procedure

Use these commands to validate visual quality of rendered scenes.

## Extract Representative Frames

### Mid-frame from video
```bash
ffmpeg -ss 50% -i final_video.mp4 -vframes 1 -q:v 2 midframe.jpg
```

### Specific timestamp
```bash
ffmpeg -ss 00:00:05 -i scene_01_intro.mp4 -vframes 1 frame_5s.jpg
```

### Grid of thumbnails (every 10 seconds)
```bash
ffmpeg -i final_video.mp4 -vf "fps=1/10" frame_%03d.jpg
```

## Visual Validation Checklist

For each extracted frame, verify:

### Positioning
- [ ] Title visible near top edge (y ≈ 3.8)
- [ ] Title not clipped by frame boundary
- [ ] Subtitle spacing consistent (0.4-0.5 units below title)
- [ ] Content within safe bounds (y between -4.0 and 4.0)
- [ ] No elements touching left/right edges

### Layout
- [ ] No overlapping text elements
- [ ] Sibling elements properly spaced (h_buff ≥ 0.5)
- [ ] Vertical alignment intentional (not accidental)
- [ ] Charts/graphs offset below subtitle (not overlapping title)

### Quality
- [ ] Text readable at 1440p (no aliasing or blur)
- [ ] Colors have sufficient contrast
- [ ] Mathematical notation renders cleanly (no garbled LaTeX)
- [ ] Animations appear smooth (no stuttering or frozen frames)

## Automated Validation (Future)

Planned: `scripts/validate_frames.py` to programmatically check positioning rules.
