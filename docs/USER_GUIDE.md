# User Guide: Video Scene Calculation and Dialogue Improvements

## What Changed?

### 1. 🎬 Better Scene Calculation for Long Videos

**What it does:**
- Videos longer than 120 seconds now have better scene distribution
- Each scene is exactly 8 seconds (except the last scene which gets the remainder)

**Example:**
```
Before (all videos):
180s video → 23 scenes (rounded up, too many scenes)

After:
180s video → 22 scenes (exact division, better pacing)
300s video → 37 scenes (was 38 before)
```

**Why it matters:**
- Long videos have more consistent pacing
- Fewer scenes = better story flow
- Less processing time for video generation

---

### 2. 📝 Clear Dialogue Display

**What it does:**
- Scene descriptions and dialogues are now displayed separately
- Each dialogue shows who is speaking and their emotion

**Before:**
```
Scene Description: A man in an office speaking to colleague
Voice: John says hello, Mary responds
```

**After:**
```
📝 Mô tả cảnh:
   Một người đàn ông đứng trong văn phòng, nhìn ra cửa sổ

🎤 Lời thoại:
   John: "Hôm nay là một ngày đẹp trời" (happy)
   Mary: "Vâng, nhưng chúng ta có nhiều việc phải làm" (serious)
```

**Why it matters:**
- Easier to review scene content
- Clear distinction between visual and audio
- Emotions are visible for better TTS generation

---

### 3. 🎤 Enhanced ElevenLabs Voice Generation

**What it does:**
- Automatically tries multiple API keys if one fails
- Saves audio files in organized project folders

**Features:**

#### Multiple API Keys
If you have multiple ElevenLabs API keys in your config:
```json
{
  "elevenlabs_api_keys": [
    "key1_here",
    "key2_here",
    "key3_here"
  ]
}
```

The system will:
1. Try key1 first
2. If it fails (rate limit/quota), automatically try key2
3. Continue until successful or all keys exhausted

#### Organized Audio Files
Audio files are now saved in project-specific folders:
```
Your Projects/
  └── MyVideo/
      ├── Audio/          ← Audio files here!
      │   ├── scene_01_audio.mp3
      │   ├── scene_02_audio.mp3
      │   └── ...
      ├── Video/
      ├── Prompt/
      └── Ảnh xem trước/
```

**Why it matters:**
- Never run out of quota (auto-switches keys)
- Better project organization
- Easy to find and reuse audio files

---

### 4. 😊 Natural Speech with Emotions

**What it does:**
- Dialogues can have emotions (happy, sad, angry, etc.)
- TTS engines use these emotions for better voice synthesis

**Example Scene:**
```json
{
  "dialogues": [
    {
      "speaker": "John",
      "text": "I won the lottery!",
      "emotion": "excited"
    },
    {
      "speaker": "Mary", 
      "text": "Really? Congratulations!",
      "emotion": "surprised"
    }
  ]
}
```

**Result:**
- John's voice will sound excited
- Mary's voice will sound surprised
- More natural and engaging videos

**Why it matters:**
- More expressive voiceovers
- Better audience engagement
- Professional-quality narration

---

## How to Use

### Scene Calculation
No action needed! The system automatically calculates the right number of scenes based on your video duration.

**Tips:**
- Videos under 2 minutes: Slightly more scenes for faster pacing
- Videos over 2 minutes: Exact 8-second scenes for consistency

### Dialogue Display
Dialogues are automatically formatted when you view scenes in the UI.

**What you'll see:**
- Scene descriptions with 📝 icon
- Dialogues with 🎤 icon
- Speaker names in bold
- Emotions in parentheses

### ElevenLabs Configuration

#### Add Multiple API Keys
1. Open your `config.json` file
2. Add your ElevenLabs API keys:
```json
{
  "elevenlabs_api_keys": [
    "your_first_key",
    "your_second_key"
  ]
}
```
3. Save and restart the application

#### Find Your Audio Files
Your audio files are automatically saved to:
```
[Project Directory]/Audio/scene_XX_audio.mp3
```

### Using Emotions in Dialogues
When generating a script, the AI will automatically assign emotions to dialogues. You can also manually add them:

**Common emotions:**
- happy, sad, angry, surprised
- excited, nervous, calm, serious
- playful, stern, gentle, dramatic

---

## Troubleshooting

### "Too many scenes generated"
✅ **Fixed!** Long videos now use exact division (no rounding up)

### "Can't find dialogue text"
✅ **Fixed!** Dialogues are now clearly separated from scene descriptions

### "ElevenLabs quota exceeded"
✅ **Fixed!** System automatically tries your other API keys

### "Audio files scattered everywhere"
✅ **Fixed!** All audio files are now in the Audio subfolder of each project

---

## Technical Details

### Scene Calculation Formula

**Short videos (≤120s):**
```
scenes = (duration + 7) / 8  (rounded up)
Example: 60s → 8 scenes
```

**Long videos (>120s):**
```
scenes = duration / 8  (exact division)
Example: 180s → 22 scenes (not 23)
```

### API Key Rotation Logic
```
1. Load all keys from config.json
2. Try first key
3. If 401 (unauthorized) or 429 (rate limit):
   → Try next key
4. If other error:
   → Report error and stop
5. Repeat until success or all keys tried
```

### Audio Folder Structure
```
Project/
  Audio/
    scene_01_audio.mp3  ← Scene 1 audio
    scene_02_audio.mp3  ← Scene 2 audio
    ...
```

---

## Examples

### Example 1: 3-minute Video
```
Duration: 180 seconds
Scenes: 22 (was 23 before)
Distribution: [8s × 21 scenes] + [12s last scene]
```

### Example 2: Dialogue with Emotion
```
Input:
  Scene: Office meeting
  Dialogue 1: John says "Great work everyone!" (proud)
  Dialogue 2: Team responds "Thank you!" (happy)

Output:
  📝 Mô tả cảnh: Office meeting room with team
  🎤 Lời thoại:
     John: "Great work everyone!" (proud)
     Team: "Thank you!" (happy)
```

### Example 3: Multi-Key Setup
```json
{
  "elevenlabs_api_keys": [
    "sk_abc123...",  ← Used first
    "sk_def456...",  ← Fallback #1
    "sk_ghi789..."   ← Fallback #2
  ]
}
```

---

## Benefits Summary

### For You (User)
- ✅ Better paced videos (especially long ones)
- ✅ Clearer scene review (separated descriptions and dialogues)
- ✅ Never run out of API quota (auto key switching)
- ✅ Organized project files (Audio subfolder)
- ✅ More natural voiceovers (emotion support)

### For Your Videos
- ✅ Professional quality narration
- ✅ Consistent scene length
- ✅ Engaging dialogue delivery
- ✅ Better audience retention

### For Your Workflow
- ✅ Less manual management
- ✅ Automatic organization
- ✅ Resilient to API failures
- ✅ Easier to find files

---

## Questions?

**Q: Will this affect my existing projects?**
A: No, all changes are backward compatible. Existing projects work exactly as before.

**Q: Do I need to update my configuration?**
A: No, the system works with your current config. Adding multiple ElevenLabs keys is optional but recommended.

**Q: What if I don't have ElevenLabs?**
A: That's fine! Google TTS and OpenAI TTS also work. ElevenLabs enhancements are only for ElevenLabs users.

**Q: Can I still use the old scene calculation?**
A: The new calculation is better for all videos. Short videos (≤120s) use the same method as before.

**Q: Where are the old audio files?**
A: They're still in their original locations. Only new audio files go to the Audio subfolder.

---

## Next Steps

1. ✅ Update your application to get these features
2. ✅ (Optional) Add multiple ElevenLabs API keys to config.json
3. ✅ Generate a new video to see the improvements
4. ✅ Check the Audio subfolder for your audio files
5. ✅ Enjoy better videos with natural dialogues!

---

*Last updated: 2025-11-11*
*Version: v3 with scene calculation improvements*
