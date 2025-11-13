#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Complete Audio Processing Workflow
=========================================

This script demonstrates the complete audio generation workflow:
1. Creating project structure with Audio folder
2. Generating audio for multiple scenes
3. Validating audio files
4. Exporting and organizing audio files

Author: Video Super Ultra v7 Team
Date: 2025-11-13
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demo_1_create_project_structure():
    """Demo 1: Create project structure with Audio folder"""
    print("\n" + "=" * 70)
    print("DEMO 1: Tạo Cấu Trúc Dự Án / Create Project Structure")
    print("=" * 70)
    
    try:
        from services.sales_video_service import ensure_project_dirs
        
        # Create a demo project
        project_name = "Demo-Audio-Processing"
        base_dir = Path.home() / "Downloads"
        
        print(f"\n📁 Tạo dự án: {project_name}")
        print(f"   Thư mục gốc: {base_dir}")
        
        # Create project directories
        dirs = ensure_project_dirs(project_name, str(base_dir))
        
        print("\n✅ Đã tạo các thư mục:")
        print(f"   📂 Root:    {dirs['root']}")
        print(f"   🎬 Video:   {dirs['video']}")
        print(f"   📝 Prompt:  {dirs['prompt']}")
        print(f"   🖼️  Preview: {dirs['preview']}")
        print(f"   🎤 Audio:   {dirs['audio']} ⬅️ THƯ MỤC AUDIO")
        
        # Verify Audio folder exists
        audio_folder_exists = dirs['audio'].exists()
        print(f"\n🔍 Kiểm tra thư mục Audio: {'✅ Tồn tại' if audio_folder_exists else '❌ Không tồn tại'}")
        
        return dirs
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_2_generate_scene_audio(audio_dir):
    """Demo 2: Generate audio for a single scene"""
    print("\n" + "=" * 70)
    print("DEMO 2: Tạo Audio Cho Một Cảnh / Generate Audio for Single Scene")
    print("=" * 70)
    
    try:
        from services.audio_generator import generate_scene_audio, validate_voiceover_config
        
        # Define scene with Vietnamese dialogue
        scene_data = {
            "scene_index": 1,
            "audio": {
                "voiceover": {
                    "tts_provider": "google",
                    "voice_id": "vi-VN-Wavenet-A",
                    "language": "vi",
                    "text": "Xin chào! Đây là demo về quy trình tạo audio tự động cho video. "
                           "Hệ thống sẽ tạo file audio MP3 cho từng cảnh trong video của bạn.",
                    "prosody": {
                        "rate": 1.0,
                        "pitch": 0
                    }
                }
            }
        }
        
        print("\n📄 Dữ liệu cảnh (Scene Data):")
        print(json.dumps(scene_data, indent=2, ensure_ascii=False))
        
        # Validate configuration
        voiceover_config = scene_data["audio"]["voiceover"]
        is_valid, error = validate_voiceover_config(voiceover_config)
        
        if not is_valid:
            print(f"\n❌ Cấu hình không hợp lệ: {error}")
            return None
        
        print("\n✅ Cấu hình hợp lệ")
        print("⚠️  Lưu ý: Để thực sự tạo audio, cần có Google API key trong config.json")
        print("   Xem: docs/TTS_SERVICE.md để biết cách cấu hình API key")
        
        # In production, this would actually generate audio:
        # audio_path = generate_scene_audio(scene_data, str(audio_dir), 1)
        
        # For demo, show what would happen
        expected_path = Path(audio_dir) / "scene_01_audio.mp3"
        print(f"\n📤 File audio sẽ được lưu tại:")
        print(f"   {expected_path}")
        
        return expected_path
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_3_batch_audio_generation(audio_dir):
    """Demo 3: Generate audio for multiple scenes"""
    print("\n" + "=" * 70)
    print("DEMO 3: Tạo Audio Cho Nhiều Cảnh / Batch Audio Generation")
    print("=" * 70)
    
    try:
        from services.audio_generator import generate_batch_audio
        
        # Define multiple scenes with Vietnamese dialogue
        scenes = [
            {
                "scene_index": 1,
                "voiceover": "Xin chào! Chào mừng bạn đến với video giới thiệu sản phẩm của chúng tôi.",
                "tts_provider": "google",
                "voice_id": "vi-VN-Wavenet-A",
                "language": "vi"
            },
            {
                "scene_index": 2,
                "voiceover": "Sản phẩm của chúng tôi có nhiều tính năng vượt trội.",
                "tts_provider": "google",
                "voice_id": "vi-VN-Wavenet-A",
                "language": "vi"
            },
            {
                "scene_index": 3,
                "voiceover": "Đặt hàng ngay hôm nay để nhận ưu đãi đặc biệt!",
                "tts_provider": "google",
                "voice_id": "vi-VN-Wavenet-A",
                "language": "vi"
            }
        ]
        
        print(f"\n📋 Tạo audio cho {len(scenes)} cảnh:")
        for i, scene in enumerate(scenes, 1):
            print(f"   {i}. Cảnh {scene['scene_index']}: {scene['voiceover'][:50]}...")
        
        print("\n⚠️  Lưu ý: Để thực sự tạo audio batch, cần có Google API key")
        
        # In production, this would generate all audio files:
        # results = generate_batch_audio(scenes, str(audio_dir))
        # print(f"\n✅ Đã tạo {len(results)} file audio")
        
        # For demo, show expected output
        print("\n📤 Files audio sẽ được tạo:")
        for scene in scenes:
            idx = scene['scene_index']
            filename = f"scene_{idx:02d}_audio.mp3"
            filepath = Path(audio_dir) / filename
            print(f"   - {filepath}")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


def demo_4_custom_voice_settings():
    """Demo 4: Customize voice settings (rate, pitch)"""
    print("\n" + "=" * 70)
    print("DEMO 4: Tùy Chỉnh Giọng Nói / Customize Voice Settings")
    print("=" * 70)
    
    print("\n🎛️  Các tham số điều chỉnh giọng nói:")
    print("\n1. SPEAKING RATE (Tốc độ nói):")
    print("   - 0.5  = Chậm rãi (slow)")
    print("   - 1.0  = Bình thường (normal, default)")
    print("   - 1.5  = Nhanh (fast)")
    print("   - 2.0  = Rất nhanh (very fast)")
    
    print("\n2. PITCH (Cao độ giọng):")
    print("   - -10  = Trầm hơn (deeper)")
    print("   - 0    = Bình thường (normal, default)")
    print("   - +5   = Cao hơn (higher)")
    print("   - +10  = Rất cao (very high)")
    
    print("\n📝 Ví dụ cấu hình:")
    
    configs = [
        {
            "name": "Giọng nam trầm, nói chậm (Deep male, slow)",
            "config": {
                "tts_provider": "google",
                "voice_id": "vi-VN-Wavenet-D",  # Male Southern
                "language": "vi",
                "text": "Đây là giọng nam miền Nam, nói chậm và trầm.",
                "prosody": {
                    "rate": 0.8,
                    "pitch": -3
                }
            }
        },
        {
            "name": "Giọng nữ cao, nói nhanh (High female, fast)",
            "config": {
                "tts_provider": "google",
                "voice_id": "vi-VN-Wavenet-B",  # Female Northern
                "language": "vi",
                "text": "Đây là giọng nữ miền Bắc, nói nhanh và cao.",
                "prosody": {
                    "rate": 1.3,
                    "pitch": +4
                }
            }
        }
    ]
    
    for i, item in enumerate(configs, 1):
        print(f"\n{i}. {item['name']}")
        print("   ```json")
        print("   " + json.dumps(item['config'], indent=2, ensure_ascii=False).replace('\n', '\n   '))
        print("   ```")


def demo_5_audio_file_info():
    """Demo 5: Show audio file information and structure"""
    print("\n" + "=" * 70)
    print("DEMO 5: Thông Tin File Audio / Audio File Information")
    print("=" * 70)
    
    print("\n📊 Định dạng file audio:")
    print("   - Format:      MP3")
    print("   - Bitrate:     128 kbps (default from TTS API)")
    print("   - Sample Rate: 24000 Hz (Google TTS)")
    print("   - Channels:    Mono (1 channel)")
    print("   - Encoding:    MPEG Audio Layer 3")
    
    print("\n📝 Quy ước đặt tên file:")
    print("   - Pattern:     scene_XX_audio.mp3")
    print("   - XX:          Số thứ tự cảnh (có leading zero)")
    print("   - Examples:")
    print("      • scene_01_audio.mp3  (Cảnh 1)")
    print("      • scene_02_audio.mp3  (Cảnh 2)")
    print("      • scene_15_audio.mp3  (Cảnh 15)")
    
    print("\n📁 Cấu trúc thư mục hoàn chỉnh:")
    print("   Dự-Án/")
    print("   ├── Audio/              🎤 Thư mục chứa thoại")
    print("   │   ├── scene_01_audio.mp3")
    print("   │   ├── scene_02_audio.mp3")
    print("   │   └── scene_03_audio.mp3")
    print("   ├── Video/              🎬 Video clips")
    print("   │   ├── scene_01.mp4")
    print("   │   ├── scene_02.mp4")
    print("   │   └── scene_03.mp4")
    print("   ├── Prompt/             📝 Scene prompts")
    print("   │   ├── scene_01_prompt.txt")
    print("   │   └── ...")
    print("   └── nhat_ky_xu_ly.log   📊 Processing log")


def demo_6_troubleshooting():
    """Demo 6: Common issues and solutions"""
    print("\n" + "=" * 70)
    print("DEMO 6: Xử Lý Lỗi Thường Gặp / Troubleshooting")
    print("=" * 70)
    
    issues = [
        {
            "problem": "❌ Không tìm thấy thư mục Audio",
            "cause": "Dự án chưa được khởi tạo",
            "solution": [
                "Sử dụng ensure_project_dirs() để tạo thư mục:",
                "  from services.sales_video_service import ensure_project_dirs",
                "  dirs = ensure_project_dirs('Tên-Dự-Án')",
                "  print(f'Audio folder: {dirs[\"audio\"]}')"
            ]
        },
        {
            "problem": "❌ Audio không được tạo",
            "cause": "Thiếu API key hoặc lời thoại rỗng",
            "solution": [
                "1. Kiểm tra API key trong config.json:",
                "   {\"google_api_keys\": [\"YOUR_API_KEY\"]}",
                "",
                "2. Kiểm tra lời thoại trong scene:",
                "   scene_data['speech'] phải có nội dung",
                "",
                "3. Xem log để biết lỗi chi tiết:",
                "   cat ~/Downloads/<Dự-Án>/nhat_ky_xu_ly.log"
            ]
        },
        {
            "problem": "❌ Voice không khớp với ngôn ngữ",
            "cause": "Sử dụng voice_id không phù hợp",
            "solution": [
                "Đảm bảo voice_id khớp với language:",
                "  - Tiếng Việt: vi-VN-* voices",
                "  - Tiếng Anh:  en-US-* hoặc en-GB-* voices",
                "  - Tiếng Nhật: ja-JP-* voices"
            ]
        }
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {issue['problem']}")
        print(f"   Nguyên nhân: {issue['cause']}")
        print(f"   Giải pháp:")
        for line in issue['solution']:
            print(f"   {line}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  🎤 AUDIO PROCESSING WORKFLOW - COMPLETE DEMO")
    print("  Quy Trình Xử Lý Âm Thanh - Demo Đầy Đủ")
    print("=" * 70)
    
    print("\n📚 Tài liệu này minh họa:")
    print("   1. Cấu trúc thư mục Audio")
    print("   2. Cách tạo audio cho từng cảnh")
    print("   3. Tạo audio hàng loạt (batch)")
    print("   4. Tùy chỉnh giọng nói (rate, pitch)")
    print("   5. Thông tin file audio")
    print("   6. Xử lý lỗi thường gặp")
    
    try:
        # Demo 1: Create project structure
        dirs = demo_1_create_project_structure()
        
        if dirs:
            audio_dir = dirs['audio']
            
            # Demo 2: Generate single scene audio
            demo_2_generate_scene_audio(audio_dir)
            
            # Demo 3: Batch audio generation
            demo_3_batch_audio_generation(audio_dir)
        else:
            # If we can't create dirs, use a temp path for demos
            audio_dir = Path("/tmp/demo_audio")
            audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Demo 4: Custom voice settings
        demo_4_custom_voice_settings()
        
        # Demo 5: Audio file info
        demo_5_audio_file_info()
        
        # Demo 6: Troubleshooting
        demo_6_troubleshooting()
        
        print("\n" + "=" * 70)
        print("✅ Demo hoàn tất!")
        print("=" * 70)
        
        print("\n📚 Tài liệu chi tiết:")
        print("   - docs/AUDIO_PROCESSING_WORKFLOW.md")
        print("   - docs/TTS_SERVICE.md")
        print("   - examples/generate_scene_audio.py")
        
        print("\n🔗 Để sử dụng thực tế:")
        print("   1. Thêm Google API key vào config.json")
        print("   2. Chạy ứng dụng: python main_image2video.py")
        print("   3. Vào tab 'Video Bán Hàng'")
        print("   4. Tạo kịch bản và click 'Tạo Video'")
        print("   5. Audio sẽ tự động được tạo trong thư mục Audio/")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
