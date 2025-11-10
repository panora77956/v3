# -*- coding: utf-8 -*-
"""
SRT Export Service
Generate SubRip (.srt) subtitle files from scene dialogues
"""

import os
from typing import List, Dict, Optional


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm)
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string (e.g., "00:00:03,500")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt_from_scenes(
    scenes: List[Dict],
    output_path: str,
    scene_duration: int = 8,
    language: str = "vi"
) -> bool:
    """
    Generate SRT subtitle file from scene dialogues.
    
    Combines all dialogues from all scenes into a single SRT file with timestamps
    corresponding to each scene's position in the video.
    
    Args:
        scenes: List of scene dictionaries containing dialogues
        output_path: Full path where SRT file should be saved
        scene_duration: Duration of each scene in seconds (default: 8)
        language: Language code for selecting dialogue text (default: "vi")
        
    Returns:
        True if SRT file was created successfully, False otherwise
        
    Example scene structure:
        {
            "dialogues": [
                {
                    "speaker": "Narrator",
                    "text_vi": "Đây là lời thoại tiếng Việt",
                    "text_tgt": "This is target language dialogue"
                }
            ]
        }
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        srt_entries = []
        entry_number = 1
        current_time = 0.0
        
        for scene_idx, scene in enumerate(scenes):
            # Get dialogues from scene
            dialogues = scene.get("dialogues", [])
            
            if not dialogues:
                # No dialogues in this scene, move to next
                current_time += scene_duration
                continue
            
            # Combine all dialogues for this scene
            scene_dialogues = []
            for dlg in dialogues:
                if not isinstance(dlg, dict):
                    continue
                
                # Select text based on language
                text_field = "text_vi" if language == "vi" else "text_tgt"
                fallback_field = "text_tgt" if language == "vi" else "text_vi"
                text = dlg.get(text_field) or dlg.get(fallback_field) or ""
                
                if not text:
                    continue
                
                speaker = dlg.get("speaker", "")
                if speaker:
                    scene_dialogues.append(f"{speaker}: {text}")
                else:
                    scene_dialogues.append(text)
            
            if scene_dialogues:
                # Create SRT entry for this scene
                start_time = current_time
                end_time = current_time + scene_duration
                
                # Format: 
                # 1
                # 00:00:00,000 --> 00:00:08,000
                # Dialogue text here
                #
                srt_entry = (
                    f"{entry_number}\n"
                    f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n"
                    f"{' '.join(scene_dialogues)}\n"
                )
                
                srt_entries.append(srt_entry)
                entry_number += 1
            
            # Move to next scene
            current_time += scene_duration
        
        # Write SRT file
        if srt_entries:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(srt_entries))
            return True
        else:
            # No dialogues found in any scene
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to generate SRT file: {e}")
        return False


def export_scene_dialogues_to_srt(
    scenes: List[Dict],
    script_folder: str,
    filename: str = "dialogues.srt",
    scene_duration: int = 8,
    language: str = "vi"
) -> Optional[str]:
    """
    Export scene dialogues to SRT file in script folder.
    
    Convenience function that generates SRT file and saves it to the
    project's script folder (e.g., 01_KichBan).
    
    Args:
        scenes: List of scene dictionaries containing dialogues
        script_folder: Path to script folder (e.g., "C:\\...\\01_KichBan")
        filename: Name of SRT file (default: "dialogues.srt")
        scene_duration: Duration of each scene in seconds (default: 8)
        language: Language code for selecting dialogue text (default: "vi")
        
    Returns:
        Full path to created SRT file if successful, None otherwise
    """
    output_path = os.path.join(script_folder, filename)
    
    success = generate_srt_from_scenes(
        scenes=scenes,
        output_path=output_path,
        scene_duration=scene_duration,
        language=language
    )
    
    return output_path if success else None
