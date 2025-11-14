# -*- coding: utf-8 -*-
import json
import re
from typing import Any, Dict, List

import requests

from services.core.key_manager import get_key

# Constants for validation
IDEA_RELEVANCE_THRESHOLD = 0.15  # Minimum word overlap ratio (15%)
MIN_WORD_LENGTH = 3  # Minimum word length for relevance checking (filters out words with <3 chars)
MAX_IDEA_DISPLAY_LENGTH = 100  # Maximum length for displaying idea in warnings

# Vietnamese character set for language detection
VIETNAMESE_CHARS = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ')

# Common stop words for relevance checking (Vietnamese and English)
STOP_WORDS = {
    'và', 'các', 'của', 'là', 'được', 'có', 'trong', 'cho', 'với', 'để',
    'một', 'này', 'đó', 'những', 'như', 'về', 'từ', 'bởi', 'khi', 'sẽ',
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been'
}

def _load_keys():
    """Load keys using unified key manager"""
    gk = get_key('google')
    ok = get_key('openai')
    return gk, ok

# Cache for domain prompts to avoid repeated string building
_domain_prompt_cache = {}

def _n_scenes(total_seconds:int):
    """
    Calculate number of scenes and their durations.
    
    For videos >120s: Use exact formula n = duration // 8 (no rounding up)
    For videos <=120s: Use original formula with rounding up
    
    Args:
        total_seconds: Total video duration in seconds
    
    Returns:
        tuple: (number_of_scenes, list_of_scene_durations)
    """
    total=max(3, int(total_seconds or 30))

    # For long videos (>120s), use exact division without rounding up
    if total > 120:
        n = max(1, total // 8)
    else:
        # For shorter videos, use original formula with rounding up
        n = max(1, (total+7)//8)

    # Distribute duration: all scenes are 8s except the last one gets remainder
    per=[8]*(n-1)+[max(1,total-8*(n-1))]
    return n, per

def _mode_from_duration(total_seconds:int):
    return "SHORT" if int(total_seconds) <= 7*60 else "LONG"

# Language code to display name mapping
LANGUAGE_NAMES = {
    'vi': 'Vietnamese (Tiếng Việt)',
    'en': 'English',
    'ja': 'Japanese (日本語)',
    'ko': 'Korean (한국어)',
    'zh': 'Chinese (中文)',
    'fr': 'French (Français)',
    'de': 'German (Deutsch)',
    'es': 'Spanish (Español)',
    'ru': 'Russian (Русский)',
    'th': 'Thai (ภาษาไทย)',
    'id': 'Indonesian (Bahasa Indonesia)'
}

def _escape_unescaped_strings(text: str) -> str:
    """
    Fix unescaped characters within JSON string values.
    
    This handles the "Unterminated string" error that occurs when JSON strings
    contain unescaped newlines, quotes, backslashes, or other special characters.
    
    Strategy:
    1. Find all JSON string values (text between quotes)
    2. Within each string, escape special characters:
       - Literal newlines -> \\n
       - Literal tabs -> \\t
       - Literal carriage returns -> \\r
       - Unescaped quotes -> \\"
       - Unescaped backslashes -> \\\\
    
    Args:
        text: JSON string with potentially unescaped characters
    
    Returns:
        JSON string with properly escaped characters
    """
    # This is a complex problem because we need to:
    # 1. Find string boundaries (opening and closing quotes)
    # 2. Skip already escaped characters
    # 3. Handle edge cases like quotes in property names vs values
    
    # Use a state machine approach to process character by character
    result = []
    in_string = False
    escape_next = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        # Handle escape sequences
        if escape_next:
            result.append(char)
            escape_next = False
            i += 1
            continue
        
        # Check for backslash (escape character)
        if char == '\\':
            result.append(char)
            escape_next = True
            i += 1
            continue
        
        # Check for quote (string boundary)
        if char == '"':
            result.append(char)
            in_string = not in_string
            i += 1
            continue
        
        # If we're inside a string, check for unescaped special characters
        if in_string:
            if char == '\n':
                # Unescaped newline - replace with \\n
                result.append('\\n')
                i += 1
                continue
            elif char == '\r':
                # Unescaped carriage return - replace with \\r
                result.append('\\r')
                i += 1
                continue
            elif char == '\t':
                # Unescaped tab - replace with \\t
                result.append('\\t')
                i += 1
                continue
        
        # Regular character - just append
        result.append(char)
        i += 1
    
    return ''.join(result)

def _fix_json_formatting(text: str, max_iterations: int = 10) -> str:
    """
    Apply comprehensive JSON formatting fixes for common LLM errors.
    Uses iterative application to handle multiple consecutive missing commas.

    Args:
        text: JSON string to fix
        max_iterations: Maximum number of iterations to prevent infinite loops (default: 10)

    Returns:
        Fixed JSON string
    """
    # Strategy: Apply fixes iteratively until no more changes are made
    # This handles cases like ["a" "b" "c"] which requires multiple passes
    
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        original_text = text
        
        # 1. Fix missing commas between objects in arrays/objects
        # These are safe to fix first as they have clear boundaries
        
        # Fix: }{ -> },{
        text = re.sub(r'\}\s*\{', '}, {', text)
        
        # Fix: ]{ -> ],[
        text = re.sub(r'\]\s*\{', '], {', text)
        
        # Fix: }[ -> },[
        text = re.sub(r'\}\s*\[', '}, [', text)
        
        # Fix: ][ -> ],[
        text = re.sub(r'\]\s*\[', '], [', text)
        
        # 2. Fix missing commas after closing brackets followed by property names
        # Pattern: ] "key": -> ], "key":  or  } "key": -> }, "key":
        text = re.sub(r'([\]}])(\s+)(")', r'\1,\2\3', text)
        
        # 3. Fix missing commas after primitives (numbers, booleans, null) followed by property names
        # Pattern: true "key": -> true, "key":  or  123 "key": -> 123, "key":
        text = re.sub(r'(\b(?:true|false|null|\d+(?:\.\d+)?)\b)(\s+)(")', r'\1,\2\3', text)
        
        # 4. Fix missing commas between string values and property names
        # This is the most complex case - need to match closing quote of value, whitespace, opening quote of key
        # Pattern: "value" "key": -> "value", "key":
        # We need to be careful not to match quotes within strings
        # Use a more specific pattern that looks for the colon after the second quote
        text = re.sub(r'(")\s+("(?:[^"\\]|\\.)*?"\s*:)', r'\1, \2', text)
        
        # 5. Fix missing commas between string values in arrays (not property names)
        # Pattern: "value1" "value2" -> "value1", "value2"
        # Use negative lookahead to ensure the second string is not a property name (not followed by colon)
        text = re.sub(r'("(?:[^"\\]|\\.)*?")(\s+)("(?:[^"\\]|\\.)*?")(?!\s*:)', r'\1,\2\3', text)
        
        # 6. Fix missing commas between primitive values in arrays
        # number followed by number/bool/null
        text = re.sub(r'(\b\d+(?:\.\d+)?)\s+(\b(?:\d+(?:\.\d+)?|true|false|null)\b)', r'\1, \2', text)
        
        # bool/null followed by number/bool/null
        text = re.sub(r'(\b(?:true|false|null))\s+(\b(?:\d+(?:\.\d+)?|true|false|null)\b)', r'\1, \2', text)
        
        # 7. Fix missing commas: string followed by number/bool/null
        text = re.sub(r'("(?:[^"\\]|\\.)*?")(\s+)(\b(?:\d+(?:\.\d+)?|true|false|null)\b)', r'\1,\2\3', text)
        
        # 8. Cleanup: Remove duplicate commas that might have been introduced
        text = re.sub(r',\s*,+', ',', text)
        
        # 9. Cleanup: Remove trailing commas before closing brackets
        text = re.sub(r',(\s*[\]}])', r'\1', text)
        
        # If no changes were made, we're done
        if text == original_text:
            break
    
    return text

def _fix_truncated_json(text: str) -> str:
    """
    Detect and repair truncated JSON by automatically closing unclosed structures.
    
    This handles cases where LLM responses are cut off mid-structure, resulting in
    incomplete JSON with missing closing brackets, braces, or quotes.
    
    Strategy:
    1. Track open/close brackets and braces using a stack
    2. Detect if JSON is truncated (unbalanced brackets)
    3. Auto-complete by closing all open structures in reverse order
    4. Handle special cases like unclosed strings and arrays
    
    Args:
        text: Potentially truncated JSON string
    
    Returns:
        Completed JSON string with all structures properly closed
    """
    if not text or not text.strip():
        return text
    
    text = text.strip()
    
    # Track open structures using a stack
    # Each entry is a tuple: (char, position)
    stack = []
    in_string = False
    escape_next = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        # Handle escape sequences in strings
        if escape_next:
            escape_next = False
            i += 1
            continue
        
        if char == '\\':
            escape_next = True
            i += 1
            continue
        
        # Handle string boundaries
        if char == '"':
            in_string = not in_string
            i += 1
            continue
        
        # Only track brackets/braces outside of strings
        if not in_string:
            if char == '{':
                stack.append(('{', i))
            elif char == '[':
                stack.append(('[', i))
            elif char == '}':
                if stack and stack[-1][0] == '{':
                    stack.pop()
            elif char == ']':
                if stack and stack[-1][0] == '[':
                    stack.pop()
        
        i += 1
    
    # If no unclosed structures and not in a string, JSON might be complete
    if not stack and not in_string:
        return text
    
    # JSON is truncated - need to close structures
    result = text
    
    # If we're in the middle of a string, close it
    if in_string:
        result += '"'
    
    # Check if the last non-whitespace character suggests incompleteness
    last_char = text.rstrip()[-1] if text.rstrip() else ''
    
    # If last character is a comma or colon, might need to add a placeholder
    # This handles cases like: "key": "value",  or  "array": [
    if last_char in [',', ':']:
        # Look at what's open on the stack
        if stack and stack[-1][0] == '[':
            # Inside an array - close the array
            pass  # Will be closed below
        elif last_char == ':':
            # After a key - add a placeholder value
            result += ' null'
    
    # Close all open structures in reverse order (LIFO)
    while stack:
        open_char, pos = stack.pop()
        if open_char == '{':
            result += '\n}'
        elif open_char == '[':
            result += '\n]'
    
    return result

def parse_llm_response_safe(response_text: str, source: str = "LLM") -> Dict[str, Any]:
    """
    Robust JSON parser with 6 fallback strategies to handle malformed LLM responses.

    Handles common LLM formatting errors including:
    - Truncated JSON (unclosed brackets, braces, strings)
    - Missing commas between properties
    - Missing commas between objects in arrays
    - Trailing commas
    - Duplicate commas
    - Markdown code blocks
    - Single quotes instead of double quotes

    Args:
        response_text: Raw text response from LLM
        source: Source identifier for logging (e.g., "Gemini", "OpenAI")

    Returns:
        Parsed JSON dictionary

    Raises:
        json.JSONDecodeError: If all parsing strategies fail
    """
    if not response_text or not response_text.strip():
        raise ValueError(f"Empty response from {source}")

    # Strategy 1: Direct JSON parse
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"[DEBUG] {source} Strategy 1 failed (direct parse): {e}")

    # Strategy 2: Fix truncated JSON (auto-complete unclosed structures)
    try:
        # Detect and fix truncated JSON by closing open brackets/braces
        completed = _fix_truncated_json(response_text)
        if completed != response_text:
            # JSON was modified (likely truncated) - try parsing
            return json.loads(completed)
    except json.JSONDecodeError as e:
        print(f"[DEBUG] {source} Strategy 2 failed (truncation fix): {e}")

    # Strategy 3: Extract from markdown code blocks
    try:
        # Remove markdown code blocks (```json ... ``` or ``` ... ```)
        if "```" in response_text:
            # Extract content between code blocks
            pattern = r'```(?:json)?\s*(.*?)\s*```'
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                cleaned = matches[0].strip()
                # Try direct parse first
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    # If direct parse fails, apply escape fixes first
                    cleaned = _escape_unescaped_strings(cleaned)
                    # Then apply formatting fixes
                    cleaned = _fix_json_formatting(cleaned)
                    return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[DEBUG] {source} Strategy 3 failed (markdown extraction): {e}")

    # Strategy 4: Fix common issues
    try:
        cleaned = response_text.strip()

        # Remove BOM if present
        if cleaned.startswith('\ufeff'):
            cleaned = cleaned[1:]

        # Remove invisible characters
        cleaned = cleaned.replace('\u200b', '')

        # Remove markdown code blocks
        cleaned = re.sub(r'```(?:json)?\s*', '', cleaned)
        cleaned = re.sub(r'\s*```', '', cleaned)

        # Replace single quotes with double quotes (simple approach)
        if "'" in cleaned and cleaned.count("'") > cleaned.count('"'):
            cleaned = cleaned.replace("'", '"')

        # Remove invalid control characters (ASCII 0-31 except whitespace)
        # This fixes the "Invalid control character" error
        cleaned = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', cleaned)

        # CRITICAL FIX: Escape unescaped special characters in strings
        # This fixes "Unterminated string" errors caused by literal newlines/quotes
        cleaned = _escape_unescaped_strings(cleaned)

        # Apply comprehensive JSON formatting fixes
        cleaned = _fix_json_formatting(cleaned)

        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[DEBUG] {source} Strategy 4 failed (common fixes): {e}")

    # Strategy 5: Find JSON by boundaries
    try:
        # Find first { and last }
        start = response_text.find('{')
        end = response_text.rfind('}')

        if start != -1 and end != -1 and end > start:
            json_str = response_text[start:end+1]

            # Remove invalid control characters
            json_str = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', json_str)

            # CRITICAL FIX: Escape unescaped special characters in strings
            # This fixes "Unterminated string" errors caused by literal newlines/quotes
            json_str = _escape_unescaped_strings(json_str)

            # Try to parse
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Apply comprehensive JSON formatting fixes
                json_str = _fix_json_formatting(json_str)
                return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"[DEBUG] {source} Strategy 5 failed (boundary extraction): {e}")

    # Strategy 6: Detailed error logging and re-raise
    print(f"[ERR] {source} All JSON parsing strategies failed!")
    print(f"[DEBUG] Response length: {len(response_text)} characters")
    print(f"[DEBUG] First 500 chars: {response_text[:500]}")
    print(f"[DEBUG] Last 500 chars: {response_text[-500:]}")

    # Try one last time to get a better error message
    try:
        json.loads(response_text)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"{source} JSON parsing failed after all strategies. Original error: {e.msg}",
            e.doc,
            e.pos
        )

def _detect_animal_content(idea, topic=None):
    """Detect if the content is about animals/wildlife
    
    Args:
        idea: Video idea text
        topic: Optional topic name
    
    Returns:
        bool: True if content is about animals/wildlife
    """
    if not idea:
        return False

    # Check topic first
    if topic and ("động vật" in topic.lower() or "thú cưng" in topic.lower() or "animal" in topic.lower() or "pet" in topic.lower() or "wildlife" in topic.lower()):
        return True

    # Common animal-related keywords in Vietnamese and English
    # Use word boundaries for better matching
    animal_keywords = [
        # Vietnamese - specific animals
        "động vật", "thú hoang", "thú cưng", "thú nuôi",
        "sư tử", "hổ", "voi", "khỉ", "gấu", "cáo", "chó sói",
        "hươu", "nai", "chuột", "thỏ", "chó hoang", "mèo hoang",
        "chim cánh cụt", "đại bàng", "diều hâu", "chim ưng",
        "cá heo", "cá voi", "cá mập", "bạch tuộc", "rùa biển", "hải cẩu", "sư tử biển",
        "rắn", "trăn", "thằn lằn", "cá sấu", "kỳ đà", "rồng komodo",
        "côn trùng", "bướm", "nhện",
        "động vật hoang dã", "sinh vật hoang dã", "loài vật", "bầy đàn",
        "tự nhiên hoang dã", "thiên nhiên hoang dã", "thế giới động vật",
        "chó", "mèo", "chó con", "mèo con", "cún", "miu",
        # English
        "wildlife", "wild animal", "nature documentary",
        "lion", "tiger", "elephant", "monkey", "bear", "fox", "wolf",
        "deer", "rabbit", "wild cat", "wild dog",
        "eagle", "hawk", "owl", "penguin",
        "dolphin", "whale", "shark", "octopus", "sea turtle", "seal", "sea lion",
        "snake", "python", "lizard", "crocodile", "alligator", "komodo dragon",
        "butterfly", "spider",
        "pack", "herd", "flock", "pride",
        # Pets
        "puppy", "kitten", "dog", "cat", "pet",
    ]

    # Normalize and check with word boundaries
    idea_lower = idea.lower()

    # Special case: exclude "python" if it's in a programming context
    if "python" in idea_lower and any(prog_word in idea_lower for prog_word in ["lập trình", "programming", "code", "tutorial", "học"]):
        # This is about Python programming, not python snake
        pass
    else:
        # Check for "python" as the snake
        if " python " in f" {idea_lower} ":
            return True

    # Use more precise matching - check if keyword appears as separate word or with spaces
    for keyword in animal_keywords:
        # Skip "python" as it's handled above
        if keyword == "python":
            continue
        # Check if keyword exists with word boundaries (spaces, start/end of string)
        if f" {keyword} " in f" {idea_lower} " or idea_lower.startswith(f"{keyword} ") or idea_lower.endswith(f" {keyword}"):
            return True

    return False


def _get_style_specific_guidance(style, idea=None, topic=None):
    """Get specific guidance based on video style to better match user's idea
    
    Args:
        style: Video style
        idea: Optional video idea text for detecting animal content
        topic: Optional topic name for detecting animal content
    
    Returns:
        str: Style-specific guidance text
    """
    # Normalize style once for all checks
    style_normalized = style.lower()

    # Check if content is about animals/wildlife - HIGHEST PRIORITY
    if _detect_animal_content(idea, topic):
        return """
═══════════════════════════════════════════════════════════════
🦁 PHONG CÁCH: PHIM TÀI LIỆU ĐỘNG VẬT (WILDLIFE DOCUMENTARY)
═══════════════════════════════════════════════════════════════

[VAI TRÒ & PHONG CÁCH]
Bạn là một đạo diễn phim tài liệu chuyên nghiệp về thế giới tự nhiên, theo phong cách của BBC Earth hoặc National Geographic. 
Mọi video bạn tạo ra đều phải đạt tiêu chuẩn điện ảnh (cinematic) và ưu tiên hàng đầu là chủ nghĩa hiện thực và tính chính xác về mặt sinh học.

[CHỈ THỊ CỐT LÕI VỀ ĐỘNG VẬT]
Khi tạo video về động vật, hãy tuân thủ nghiêm ngặt hình thái (ngoại hình) và động học (chuyển động) tự nhiên của loài đó. 
Chúng phải hành xử và di chuyển như động vật ngoài đời thực.

[RÀNG BUỘC NGHIÊM NGẶT - KHÔNG NHÂN HÓA NGOẠI HÌNH]
Tuyệt đối CẤM tạo ra bất kỳ hình thức nhân hóa ngoại hình nào. Điều này bao gồm, nhưng không giới hạn ở:

❌ CẤM TUYỆT ĐỐI:
• Tạo động vật đi bằng hai chân (trừ khi đó là hành vi tự nhiên của loài, như chim cánh cụt, gấu đứng lên)
• Gắn khuôn mặt người, biểu cảm của con người (như cười nhếch mép, nháy mắt có chủ ý) lên động vật
• Thêm bàn tay, ngón tay của người vào động vật
• Tạo ra các đặc điểm lai tạo, phi tự nhiên, quái dị (grotesque, hybrid, mutant)
• Cho động vật mặc quần áo, đeo kính, hoặc sử dụng các vật dụng của con người (trừ khi prompt của người dùng yêu cầu rõ ràng)
• Phong cách hoạt hình, anime, hoặc 3D-cartoon

✅ BẮT BUỘC:
• Động vật PHẢI di chuyển theo cách tự nhiên của loài (bốn chân, bò, bơi, bay...)
• Hành vi PHẢI thực tế: săn mồi, ăn uống, nghỉ ngơi, chơi đùa theo bản năng
• Biểu cảm PHẢI tự nhiên: không có nụ cười kiểu người, chỉ có biểu hiện tự nhiên của loài
• Môi trường sống PHẢI chính xác: rừng nhiệt đới, đại dương, sa mạc, cực địa theo đúng loài
• Ánh sáng và màu sắc PHẢI tự nhiên, cinematic như phim tài liệu BBC/NatGeo

[ĐỊNH HƯỚNG SÁNG TẠO]
Nếu người dùng yêu cầu một hành động (như "con mèo nói chuyện"), hãy thể hiện nó một cách tự nhiên nhất có thể:
• ✅ ĐÚNG: Quay cận cảnh một con mèo đang kêu "meow" về phía máy quay
• ❌ SAI: Một con mèo cử động miệng như người

[CẤU TRÚC PHIM TÀI LIỆU]
- Structure: Introduction → Behavior/Hunt → Challenge → Resolution/Survival
- Camera: Wide establishing shots, close-up details, slow motion action
- Narration: Educational, respectful, David Attenborough style
- Visual: Natural lighting, real habitats, authentic animal behavior
- Focus: Biology, ecology, survival, natural beauty
- Tone: Majestic, educational, awe-inspiring

[YÊU CẦU KỸ THUẬT]
• Mỗi cảnh PHẢI mô tả chính xác loài, môi trường, hành vi
• Camera angles phải như phim tài liệu thực: wide landscape, telephoto wildlife shots
• Không được có yếu tố hư cấu phi thực tế
• Ưu tiên tính giáo dục và chính xác khoa học
"""

    # Use early returns for better performance
    if "vlog" in style_normalized or "cá nhân" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
📹 PHONG CÁCH: VLOG CÁ NHÂN
═══════════════════════════════════════════════════════════════
- Tone: THÂN MẬT, chân thực, như nói chuyện với bạn bè
- Camera: POV, selfie shots, handheld natural movement
- Hook: Bắt đầu với câu chuyện cá nhân hoặc tình huống thực tế
- Dialogue: Tự nhiên, có thể ngập ngừng, không cần hoàn hảo
- Focus: Chia sẻ trải nghiệm, cảm xúc, bài học cá nhân
"""

    if "review" in style_normalized or "unboxing" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
📦 PHONG CÁCH: REVIEW/UNBOXING
═══════════════════════════════════════════════════════════════
- Structure: Intro (hook) → Specs/Features → Demo → Pros/Cons → Verdict
- Camera: Close-ups sản phẩm, hands-on shots, B-roll chi tiết
- Hook: "Điều này sẽ thay đổi cách bạn..." hoặc so sánh bất ngờ
- Visual: Chuyển cảnh nhanh, zoom vào chi tiết quan trọng
- Focus: Giá trị thực tế, so sánh, đánh giá trung thực
"""

    if "tutorial" in style_normalized or "hướng dẫn" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
🎓 PHONG CÁCH: TUTORIAL/HƯỚNG DẪN
═══════════════════════════════════════════════════════════════
- Structure: Problem → Solution steps → Result
- Camera: Over-shoulder, close-up hands, screen recording
- Hook: "Làm thế nào để..." hoặc "Bí quyết để..."
- Visual: Từng bước rõ ràng, text overlays, arrows/highlights
- Focus: Dễ hiểu, có thể làm theo, kết quả cụ thể
"""

    if "quảng cáo" in style_normalized or "tvc" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
📺 PHONG CÁCH: QUẢNG CÁO TVC
═══════════════════════════════════════════════════════════════
- Structure: Problem → Agitation → Solution → Call-to-Action
- Camera: Cinematic, professional lighting, perfect framing
- Hook: Dramatic problem hoặc lifestyle transformation
- Visual: High-end production, brand colors, lifestyle shots
- Focus: Emotional connection, brand message, clear CTA
"""

    if "music" in style_normalized or "mv" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
🎵 PHONG CÁCH: MUSIC VIDEO
═══════════════════════════════════════════════════════════════
- Structure: Theo beat và lyrics của nhạc
- Camera: Dynamic movement, artistic angles, rhythm-matching cuts
- Hook: Visual impact ngay từ giây đầu
- Visual: Metaphors, symbolism, artistic interpretation
- Focus: Mood, emotion, visual storytelling match với lyrics
"""

    if "horror" in style_normalized or "kinh dị" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
👻 PHONG CÁCH: HORROR/KINH DỊ
═══════════════════════════════════════════════════════════════
- Structure: Normal → Unsettling → Terror → Climax
- Camera: Low angles, shaky cam, jump scares, slow creepy zoom
- Hook: Mysterious hoặc creepy atmosphere ngay đầu
- Visual: Dark lighting, shadows, sudden movements
- Focus: Tension build-up, fear, suspense, twisted ending
"""

    if "sci-fi" in style_normalized or "khoa học" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
🚀 PHONG CÁCH: SCI-FI/KHOA HỌC VIỄN TƯỞNG
═══════════════════════════════════════════════════════════════
- Structure: World-building → Discovery → Conflict → Resolution
- Camera: Futuristic angles, wide establishing shots, tech close-ups
- Hook: "What if..." hoặc advanced technology reveal
- Visual: Futuristic design, tech elements, cool color palette
- Focus: Technology, future society, philosophical questions
"""

    if "fantasy" in style_normalized or "phép thuật" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
✨ PHONG CÁCH: FANTASY/PHÉP THUẬT
═══════════════════════════════════════════════════════════════
- Structure: Ordinary world → Magic discovery → Quest → Transformation
- Camera: Epic wide shots, magical effects emphasis, wonder moments
- Hook: Magic reveal hoặc mystical world introduction
- Visual: Rich colors, magical elements, fantastical creatures
- Focus: Wonder, magic system, hero's journey, imagination
"""

    if "anime" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
🎌 PHONG CÁCH: ANIME
═══════════════════════════════════════════════════════════════
- Structure: Character-driven với emotional peaks
- Camera: Dynamic angles, speed lines, dramatic close-ups
- Hook: Action sequence hoặc character intro
- Visual: Vibrant colors, exaggerated expressions, dramatic effects
- Focus: Character emotions, relationships, epic moments
"""

    if "tài liệu" in style_normalized or "documentary" in style_normalized or "phóng sự" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
📚 PHONG CÁCH: TÀI LIỆU/PHÓNG SỰ
═══════════════════════════════════════════════════════════════
- Structure: Question → Investigation → Discovery → Conclusion
- Camera: Observational, interviews, B-roll footage
- Hook: Surprising fact hoặc important question
- Visual: Real footage, data visualization, expert interviews
- Focus: Truth, education, insight, real stories
"""

    if "sitcom" in style_normalized or "hài" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
😂 PHONG CÁCH: SITCOM/HÀI KỊCH
═══════════════════════════════════════════════════════════════
- Structure: Setup → Escalation → Punchline
- Camera: Multi-cam, reaction shots, comic timing
- Hook: Funny situation hoặc character quirk
- Visual: Bright lighting, expressive acting, sight gags
- Focus: Humor, timing, relatable situations, callbacks
"""

    if "phim ngắn" in style_normalized or "short film" in style_normalized:
        return """
═══════════════════════════════════════════════════════════════
🎬 PHONG CÁCH: PHIM NGẮN
═══════════════════════════════════════════════════════════════
- Structure: Classic 3-act với twist ending
- Camera: Cinematic composition, meaningful shots, visual metaphors
- Hook: Intriguing premise hoặc character dilemma
- Visual: Artistic, symbolic, every shot tells story
- Focus: Complete story arc, character development, message
"""

    # Default: Cinematic for all other styles including "Điện ảnh", "3D/CGI", "Stop-motion", "Quay thực"
    return """
═══════════════════════════════════════════════════════════════
🎥 PHONG CÁCH: ĐIỆN ẢNH (CINEMATIC)
═══════════════════════════════════════════════════════════════
- Structure: Professional 3-Act structure
- Camera: Cinematic composition, smooth movements, perfect framing
- Hook: Visual impact hoặc intriguing scenario
- Visual: Film-quality lighting, color grading, depth
- Focus: Story depth, character arc, visual excellence
"""


def _schema_prompt(idea, style_vi, out_lang, n, per, mode, topic=None, domain=None):
    # Get target language display name
    target_language = LANGUAGE_NAMES.get(out_lang, 'Vietnamese (Tiếng Việt)')

    # OPTIMIZATION: For long scenarios (>300s), use concise prompt to reduce LLM processing time
    # Long prompts take longer for LLM to process, especially for 480s+ scenarios
    is_long_scenario = sum(per) > 300  # True for 5+ minute videos

    # Check if domain requires no-character narration (like PANORA Science Narrator)
    # These domains use voiceover narration addressing audience directly ("You", "Your body")
    # instead of creating fictional characters
    no_character_domains = [
        ("KHOA HỌC GIÁO DỤC", "PANORA - Nhà Tường thuật Khoa học"),
    ]
    requires_no_characters = (domain, topic) in no_character_domains if domain and topic else False
    
    # Log the domain/topic selection for debugging
    if domain and topic:
        print(f"[INFO] Using domain='{domain}', topic='{topic}', no_characters={requires_no_characters}")

    # ===== CHECK FOR CUSTOM SYSTEM PROMPT =====
    # Check if custom system prompt exists for this domain+topic
    custom_prompt = None
    if domain and topic:
        try:
            from services.domain_custom_prompts import get_custom_prompt
            custom_prompt = get_custom_prompt(domain, topic)
            if custom_prompt:
                print(f"[INFO] Using CUSTOM system prompt for {domain}/{topic}")
        except ImportError:
            print(f"[WARN] Could not load custom prompts module")
    
    # If custom prompt exists, use simplified prompt structure
    if custom_prompt:
        # Build minimal prompt with ONLY custom prompt + language + schema
        target_language = LANGUAGE_NAMES.get(out_lang, 'Vietnamese (Tiếng Việt)')
        
        # Language instruction
        language_instruction = f"""
TARGET LANGUAGE: {target_language}
ALL text_tgt, prompt_tgt, title_tgt, outline_tgt, screenplay_tgt, voiceover_tgt fields MUST be in {target_language}.
"""
        
        # Schema for no-character domains (PANORA)
        schema = f"""
Return ONLY valid JSON (no extra text):

{{
  "title_vi": "Tiêu đề hấp dẫn",
  "title_tgt": "Title in {target_language}",
  "hook_summary": "Hook 3 giây đầu",
  "outline_vi": "Dàn ý theo 5 giai đoạn",
  "outline_tgt": "Outline in {target_language}",
  "screenplay_vi": "Screenplay với VOICEOVER ngôi thứ hai và VISUAL DESCRIPTION",
  "screenplay_tgt": "Screenplay in {target_language}",
  "emotional_arc": "Cung cảm xúc",
  "scenes": [
    {{
      "prompt_vi": "Mô tả hình ảnh y khoa/khoa học - KHÔNG có tên nhân vật",
      "prompt_tgt": "Visual description in {target_language} - NO character names",
      "duration": {per[0] if per else 8},
      "voiceover_vi": "Lời thoại ngôi thứ hai (Bạn, Cơ thể của bạn)",
      "voiceover_tgt": "Second-person narration in {target_language}",
      "location": "Không gian y khoa cụ thể",
      "time_of_day": "Day/Night",
      "camera_shot": "Wide/Close-up/etc",
      "lighting_mood": "Bright/Dark/etc",
      "emotion": "Cảm xúc",
      "story_beat": "Setup/Rising/Twist/Climax/Resolution",
      "transition_from_previous": "Kết nối với cảnh trước",
      "visual_elements": ["Hologram", "3D simulation", "Data overlay"],
      "visual_notes": "Props, colors, medical accuracy"
    }}
  ]
}}

CRITICAL: NO character names, use second-person voiceover, {n} scenes total.
"""
        
        # Return simplified prompt with custom system prompt
        return f"""{custom_prompt}

{language_instruction}

INPUT:
- Ý tưởng: "{idea}"
- Phong cách: "{style_vi}"
- Số cảnh: {n} (mỗi cảnh 8s; cảnh cuối {per[-1]}s)
- Ngôn ngữ đích: {target_language}

{schema}
"""
    
    # ===== END CUSTOM PROMPT CHECK =====

    # Get style-specific guidance with animal detection
    style_guidance = _get_style_specific_guidance(style_vi, idea=idea, topic=topic)

    # Build language instruction
    language_instruction = f"""
IMPORTANT LANGUAGE REQUIREMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 TARGET LANGUAGE: {target_language}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**CRITICAL - MUST FOLLOW:**
1. ALL "text_tgt" fields in dialogues MUST be in {target_language}
2. ALL "prompt_tgt" fields MUST be in {target_language}
3. "title_tgt", "outline_tgt", "screenplay_tgt" MUST be in {target_language}
4. Scene descriptions in "prompt_tgt" should match cultural context of {target_language}
5. Character names can stay in original form but dialogue MUST be {target_language}

**Example for Vietnamese (vi):**
  "text_vi": "Xin chào",
  "text_tgt": "Xin chào"  ← SAME as source

**Example for English (en):**
  "text_vi": "Xin chào",
  "text_tgt": "Hello"  ← TRANSLATED to English

**Example for Japanese (ja):**
  "text_vi": "Xin chào", 
  "text_tgt": "こんにちは"  ← TRANSLATED to Japanese

⚠️ DO NOT mix languages - stick to {target_language} for ALL target fields!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # Detect if user provided detailed screenplay vs just idea
    # Indicators: SCENE, ACT, INT./EXT., character profiles, dàn ý, kịch bản, screenplay
    idea_lower = (idea or "").lower()
    has_screenplay_markers = any(marker in idea_lower for marker in [
        'scene ', 'act 1', 'act 2', 'act 3', 'int.', 'ext.',
        'kịch bản', 'screenplay', 'dàn ý', 'hồ sơ nhân vật',
        'fade in', 'fade out', 'close up', 'cut to'
    ])

    # Adjust instructions based on input type
    if has_screenplay_markers:
        input_type_instruction = """
**QUAN TRỌNG**: Người dùng đã cung cấp kịch bản CHI TIẾT. Nhiệm vụ của bạn:
1. TUÂN THỦ chặt chẽ nội dung, nhân vật, và cấu trúc câu chuyện đã cho
2. Chỉ điều chỉnh nhẹ để phù hợp format video (visual prompts, timing)
3. GIỮ NGUYÊN ý tưởng gốc, tính cách nhân vật, và luồng cảm xúc
4. KHÔNG sáng tạo lại hoặc thay đổi concept cốt lõi
"""
        base_role = """
Bạn là **Biên kịch Chuyển đổi Format AI**. Nhận **kịch bản chi tiết** và chuyển đổi thành **format video tối ưu** mà KHÔNG thay đổi nội dung gốc.
Mục tiêu: GIỮ NGUYÊN câu chuyện và nhân vật, chỉ tối ưu hóa cho video format."""
    else:
        input_type_instruction = """
**QUAN TRỌNG**: Người dùng đã cung cấp Ý TƯỞNG. Nhiệm vụ của bạn:
1. PHÁT TRIỂN chính xác theo ý tưởng mà người dùng đưa ra
2. GIỮ NGUYÊN chủ đề, bối cảnh, nhân vật trong ý tưởng gốc
3. Chỉ thêm chi tiết, cảm xúc, và cấu trúc để tạo kịch bản hoàn chỉnh
4. KHÔNG thay đổi concept cốt lõi hoặc tạo câu chuyện hoàn toàn khác
5. Nếu ý tưởng đề cập nhân vật/địa điểm/sự kiện cụ thể → PHẢI xuất hiện trong kịch bản
"""
        base_role = """
Bạn là **Biên kịch Đa năng AI Cao cấp**. Nhận **ý tưởng thô sơ** và phát triển thành **kịch bản phim/video SIÊU HẤP DẪN**.
Mục tiêu: TẠO NỘI DUNG VIRAL dựa CHÍNH XÁC trên ý tưởng của người dùng, giữ chân người xem từ giây đầu tiên."""

    # OPTIMIZATION: Use concise rules for long scenarios to speed up LLM processing
    # FURTHER OPTIMIZATION: Drastically reduce prompt length for faster generation
    # Include generic principles only when NO domain-specific prompt is provided
    if is_long_scenario:
        # Ultra-condensed version for 5+ minute videos - essential rules only
        if domain and topic:
            # Domain-specific: Only include technical requirements
            if requires_no_characters:
                # No-character domains (like PANORA): Remove all character-related instructions
                base_rules = f"""
{base_role}

{input_type_instruction}

**TARGET LANGUAGE**: {target_language} - ALL text_tgt, prompt_tgt, title_tgt, outline_tgt fields MUST be in this language.

{style_guidance}

**TECHNICAL REQUIREMENTS**:
1. Use voiceover (VO) narration addressing the audience directly
2. Scene prompts: Visual descriptions only (no character names or personas)
3. Scene continuity: Logical connection between scenes
"""
            else:
                # Standard character-based storytelling
                base_rules = f"""
{base_role}

{input_type_instruction}

**TARGET LANGUAGE**: {target_language} - ALL text_tgt, prompt_tgt, title_tgt, outline_tgt fields MUST be in this language.

{style_guidance}

**TECHNICAL REQUIREMENTS**:
1. Character visual_identity: NEVER change across scenes
2. Scene prompts: Include full character descriptions
3. Scene continuity: Logical connection between scenes
"""
        else:
            # Generic: Include full storytelling principles
            base_rules = f"""
{base_role}

{input_type_instruction}

**TARGET LANGUAGE**: {target_language} - ALL text_tgt, prompt_tgt, title_tgt, outline_tgt fields MUST be in this language.

{style_guidance}

**CORE RULES**:
1. Strong hook (first 3s): action/question/twist
2. Each scene: clear emotion + story beat
3. Character visual_identity: NEVER change across scenes
4. Scene prompts: Include full character descriptions
5. Pacing: Plot twist at midpoint, mini-hooks every 15-20s
"""
    else:
        # Optimized version for shorter videos - reduced verbosity for faster generation
        if domain and topic:
            # Domain-specific: Only include technical requirements
            if requires_no_characters:
                # No-character domains (like PANORA): Remove all character-related instructions
                base_rules = f"""
{base_role}

{input_type_instruction}

**TARGET LANGUAGE**: {target_language} - ALL text_tgt, prompt_tgt, title_tgt, outline_tgt fields MUST be in this language.

{style_guidance}

**VOICEOVER NARRATION**: Use second-person narration addressing the audience ("You", "Your body", "Your brain")
- NO character names or fictional personas
- NO dialogue between characters
- Scene descriptions focus on visual elements only

**SCENE CONTINUITY**: Scenes connect logically (location, time, lighting consistent)
**STYLE CONSISTENCY**: All scenes use "{style_vi}" style consistently
""".strip()
            else:
                # Standard character-based storytelling
                base_rules = f"""
{base_role}

{input_type_instruction}

**TARGET LANGUAGE**: {target_language} - ALL text_tgt, prompt_tgt, title_tgt, outline_tgt fields MUST be in this language.

{style_guidance}

**CHARACTER BIBLE** (2-4 characters):
- key_trait: Core personality
- motivation: Deep drive
- visual_identity: Detailed appearance (face, eyes, hair, clothing, accessories) - NEVER changes
- archetype, fatal_flaw, goals

**CHARACTER CONSISTENCY (CRITICAL)**:
- Scene prompts MUST include FULL visual_identity from character_bible
- NEVER change appearance across scenes (face, hair, clothing, accessories)
- Format: "[Name]: [full visual_identity], doing [action]"

**SCENE CONTINUITY**: Scenes connect logically (location, time, lighting consistent)
**STYLE CONSISTENCY**: All scenes use "{style_vi}" style consistently
""".strip()
        else:
            # Generic: Include full storytelling principles
            base_rules = f"""
{base_role}

{input_type_instruction}

**TARGET LANGUAGE**: {target_language} - ALL text_tgt, prompt_tgt, title_tgt, outline_tgt fields MUST be in this language.

{style_guidance}

**KEY PRINCIPLES**:
1. **HOOK** (first 3s): Dramatic action/shocking question/twist - NO slow intro
2. **EMOTION**: Each scene has clear emotion shift (Tension→Relief, Joy→Sadness)
3. **PACING**: {mode} format - Fast tempo for SHORT, plot twist at midpoint for LONG
4. **VISUAL**: Specific actions, camera movements (zoom=tension, cuts=action), lighting mood
5. **CINEMATIC**: Slow-mo, montage, POV shots, visual metaphors

**CHARACTER BIBLE** (2-4 characters):
- key_trait: Core personality
- motivation: Deep drive
- visual_identity: Detailed appearance (face, eyes, hair, clothing, accessories) - NEVER changes
- archetype, fatal_flaw, goals

**CHARACTER CONSISTENCY (CRITICAL)**:
- Scene prompts MUST include FULL visual_identity from character_bible
- NEVER change appearance across scenes (face, hair, clothing, accessories)
- Format: "[Name]: [full visual_identity], doing [action]"

**SCENE CONTINUITY**: Scenes connect logically (location, time, lighting consistent)
**STYLE CONSISTENCY**: All scenes use "{style_vi}" style consistently
**SCENE QUALITY**: Visual & specific descriptions, natural dialogue, varied shots, setup/payoff
""".strip()

    # Build schema conditionally based on whether characters are allowed
    if requires_no_characters:
        # No-character schema (PANORA and similar domains)
        schema = f"""
Trả về **JSON hợp lệ** theo schema EXACT (không thêm ký tự ngoài JSON):

{{
  "title_vi": "Tiêu đề HẤP DẪN, gây tò mò (VI)",
  "title_tgt": "Compelling title in {target_language}",
  "hook_summary": "Mô tả hook 3s đầu - điều gì khiến người xem PHẢI xem tiếp?",
  "outline_vi": "Dàn ý theo {mode}: Cấu trúc theo giai đoạn + key emotional beats + major plot points",
  "outline_tgt": "Outline in {target_language}",
  "screenplay_vi": "Screenplay chi tiết: VOICEOVER narration addressing audience in second person (Bạn, Cơ thể của bạn, Não của bạn)\\nVISUAL DESCRIPTION (3D/2D medical simulations, holograms, data overlays)\\n- Bao gồm camera angles, lighting, mood, transitions\\n- KHÔNG có nhân vật hư cấu, KHÔNG có tên riêng",
  "screenplay_tgt": "Full screenplay in {target_language} with second-person voiceover",
  "emotional_arc": "Cung cảm xúc của story: [Start emotion] → [Peaks & Valleys] → [End emotion]",
  "scenes": [
    {{
      "prompt_vi":"Visual prompt CỤ THỂ (visual elements, lighting, camera, mood) - 2-3 câu mô tả hình ảnh y khoa/khoa học - KHÔNG có tên nhân vật",
      "prompt_tgt":"Detailed visual prompt in {target_language} - NO character names, focus on scientific/medical visuals",
      "duration": 8,
      "voiceover_vi": "Lời thoại bằng ngôi thứ hai, nói chuyện trực tiếp với khán giả",
      "voiceover_tgt": "Second-person narration in {target_language}",
      "location": "Location cụ thể (phòng thí nghiệm, không gian y khoa, v.v.)",
      "time_of_day": "Day/Night/etc",
      "camera_shot": "Wide/Close-up/POV/Tracking/etc + movement",
      "lighting_mood": "Bright/Dark/Warm/Cold/High-contrast/etc",
      "emotion": "Cảm xúc chủ đạo của scene",
      "story_beat": "Plot point: Setup/Rising action/Twist/Climax/Resolution",
      "transition_from_previous": "How this scene connects to previous scene",
      "style_notes": "Specific {style_vi} style elements in this scene",
      "visual_elements": ["Mô tả các yếu tố hình ảnh: hologram, data overlay, 3D simulation, etc."],
      "visual_notes": "Props, colors, symbolism, transitions, scientific accuracy"
    }}
  ]
}}

**NOTE**: Scene 1=strong hook, NO character names or fictional personas, use second-person voiceover addressing audience
""".strip()
    else:
        # Standard character-based schema
        schema = f"""
Trả về **JSON hợp lệ** theo schema EXACT (không thêm ký tự ngoài JSON):

{{
  "title_vi": "Tiêu đề HẤP DẪN, gây tò mò (VI)",
  "title_tgt": "Compelling title in {target_language}",
  "hook_summary": "Mô tả hook 3s đầu - điều gì khiến người xem PHẢI xem tiếp?",
  "character_bible": [{{"name":"","role":"","key_trait":"","motivation":"","default_behavior":"","visual_identity":"","archetype":"","fatal_flaw":"","goal_external":"","goal_internal":""}}],
  "character_bible_tgt": [{{"name":"","role":"","key_trait":"","motivation":"","default_behavior":"","visual_identity":"","archetype":"","fatal_flaw":"","goal_external":"","goal_internal":""}}],
  "outline_vi": "Dàn ý theo {mode}: ACT structure + key emotional beats + major plot points",
  "outline_tgt": "Outline in {target_language}",
  "screenplay_vi": "Screenplay chi tiết: INT./EXT. LOCATION - TIME\\nACTION (visual, cinematic)\\nDIALOGUE\\n- Bao gồm camera angles, lighting, mood, transitions",
  "screenplay_tgt": "Full screenplay in {target_language}",
  "emotional_arc": "Cung cảm xúc của story: [Start emotion] → [Peaks & Valleys] → [End emotion]",
  "scenes": [
    {{
      "prompt_vi":"Visual prompt SIÊU CỤ THỂ (action, lighting, camera, mood, characters with FULL details) - 2-3 câu cinematic",
      "prompt_tgt":"Detailed visual prompt in {target_language} with FULL character details",
      "duration": 8,
      "characters": ["Nhân vật xuất hiện (FULL visual_identity)"],
      "location": "Location cụ thể",
      "time_of_day": "Day/Night/Golden hour/etc (MUST be consistent with previous scene if same location)",
      "camera_shot": "Wide/Close-up/POV/Tracking/etc + movement",
      "lighting_mood": "Bright/Dark/Warm/Cold/High-contrast/etc (MUST match time_of_day)",
      "emotion": "Cảm xúc chủ đạo của scene",
      "story_beat": "Plot point: Setup/Rising action/Twist/Climax/Resolution",
      "transition_from_previous": "How this scene connects to previous scene (location/action/time continuity)",
      "style_notes": "Specific {style_vi} style elements in this scene",
      "dialogues": [
        {{"speaker":"Tên","text_vi":"Thoại tự nhiên, có subtext","text_tgt":"Natural line in {target_language}","emotion":"angry/sad/happy/etc"}}
      ],
      "visual_notes": "Props, colors, symbolism, transitions, continuity elements from previous scene"
    }}
  ]
}}

**NOTE**: Scene 1=strong hook, prompts=visual & cinematic, include full character details in each scene
""".strip()

    # Adjust input label based on detected type
    input_label = "Kịch bản chi tiết" if has_screenplay_markers else "Ý tưởng thô"

    # Add idea adherence reminder (concise version)
    idea_adherence_reminder = ""
    if not has_screenplay_markers:
        idea_adherence_reminder = f"""
⚠️ CRITICAL: Script MUST be based on idea: "{idea}"
Use mentioned characters/locations/events. Don't create unrelated stories.
"""

    return f"""{base_rules}
{idea_adherence_reminder}
ĐẦU VÀO:
- {input_label}: "{idea}"
- Phong cách: "{style_vi}"
- Chế độ: {mode}
- Số cảnh kỹ thuật: {n} (mỗi cảnh 8s; cảnh cuối {per[-1]}s)
- Ngôn ngữ đích: {target_language}

{schema}
"""

def _call_openai(prompt, api_key, model="gpt-4-turbo"):
    """FIXED: Changed from gpt-5 to gpt-4-turbo"""
    url="https://api.openai.com/v1/chat/completions"
    headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"}
    data={
        "model": model,
        "messages":[
            {"role":"system","content":"You output strictly JSON when asked."},
            {"role":"user","content": prompt}
        ],
        "response_format":{"type":"json_object"},
        "temperature":0.9
    }
    r=requests.post(url,headers=headers,json=data,timeout=240); r.raise_for_status()
    txt=r.json()["choices"][0]["message"]["content"]
    return parse_llm_response_safe(txt, "OpenAI")

def _call_gemini(prompt, api_key, model="gemini-2.5-flash", timeout=None, duration_seconds=None, progress_callback=None):
    """
    Call Gemini API with Vertex AI support and intelligent retry logic for 503 errors
    
    Strategy:
    0. Try Vertex AI first if configured (better rate limits, less 503 errors)
    1. Dynamic timeout based on script duration (5-10 minutes for long scripts)
    2. Aggressive exponential backoff for 503 errors (10s → 20s → 30s → 60s) to handle server overload
    3. Use all available API keys (up to 15) with proper rotation
    4. Fallback to alternative models (gemini-1.5-flash, gemini-2.0-flash-exp)
    5. Add minimum delay between all API calls (5s) to prevent rate limiting and reduce 503 errors
    6. Detailed progress reporting
    
    Args:
        prompt: Text prompt for Gemini
        api_key: Primary API key
        model: Model name (default: gemini-2.5-flash)
        timeout: Request timeout in seconds (default: auto-calculated)
        duration_seconds: Script duration to calculate appropriate timeout
        progress_callback: Optional callback(message, percent) for progress updates
    """
    import time
    import json

    from services.core.api_config import gemini_text_endpoint
    from services.core.key_manager import get_all_keys

    # Helper function for progress reporting
    def report_progress(msg):
        if progress_callback:
            progress_callback(msg, None)
        print(f"[INFO] {msg}")

    # ===== STRATEGY 0: Try Vertex AI first =====
    # Check if Vertex AI is enabled in config
    try:
        from utils import config as cfg
        config = cfg.load()
        
        vertex_config = config.get('vertex_ai', {})
        
        if vertex_config.get('enabled', False):
            try:
                from services.vertex_ai_client import VertexAIClient
                from services.core.api_config import VERTEX_AI_TEXT_MODEL
                from services.vertex_service_account_manager import get_vertex_account_manager
                
                # Calculate appropriate timeout
                if timeout is None:
                    if duration_seconds and duration_seconds > 120:
                        if duration_seconds >= 460:
                            timeout = 600
                        elif duration_seconds >= 300:
                            timeout = 480
                        elif duration_seconds >= 180:
                            timeout = 360
                        else:
                            timeout = 300
                    else:
                        timeout = 180
                
                # Try to get service account from manager
                account_mgr = get_vertex_account_manager()
                account_mgr.load_from_config(config)
                account = account_mgr.get_next_account()
                
                if not account:
                    report_progress("[TEXT GEN] Không có Vertex AI service account khả dụng, sử dụng AI Studio API")
                    # Continue to AI Studio fallback
                else:
                    report_progress(f"[TEXT GEN] Đang thử Vertex AI với account: {account.name}")
                    
                    # Use Vertex AI model if specified, otherwise use default
                    vertex_model = VERTEX_AI_TEXT_MODEL if model == "gemini-2.5-flash" else model
                    
                    report_progress(f"Trying Vertex AI with model {vertex_model}...")
                    
                    vertex_client = VertexAIClient(
                        model=vertex_model,
                        project_id=account.project_id,
                        location=account.location,
                        api_key=api_key,
                        use_vertex=True,
                        credentials_json=account.credentials_json
                    )
                    
                    # Generate content - VertexAIClient handles retries internally
                    result = vertex_client.generate_content(
                        prompt=prompt,
                        system_instruction="You are a professional AI assistant. Generate valid JSON output when requested.",
                        temperature=0.9,
                        timeout=timeout,
                        max_retries=5
                    )
                    
                    report_progress("✓ Vertex AI generation successful")
                    return parse_llm_response_safe(result, "Vertex AI")
                
            except Exception as e:
                report_progress(f"Vertex AI failed: {e}. Falling back to AI Studio API...")
                # Continue to AI Studio fallback below
    except Exception as e:
        # Config file error or Vertex AI import error - continue to AI Studio
        pass
    
    # ===== AI Studio fallback (original logic) =====
    report_progress("Using AI Studio API...")

    # Dynamic timeout calculation based on script duration and complexity
    if timeout is None:
        if duration_seconds and duration_seconds > 120:
            # For long scripts (>2 min), use much longer timeouts
            if duration_seconds >= 460:
                # 460+ second scripts need 8-10 minutes
                timeout = 600  # 10 minutes
            elif duration_seconds >= 300:
                # 5+ minute scripts need 6-8 minutes
                timeout = 480  # 8 minutes
            elif duration_seconds >= 180:
                # 3+ minute scripts need 4-6 minutes
                timeout = 360  # 6 minutes
            else:
                # 2+ minute scripts need 3-5 minutes
                timeout = 300  # 5 minutes
            report_progress(f"Using {timeout}s timeout for {duration_seconds}s script")
        else:
            # For short scripts, calculate based on prompt length
            base_timeout = 60
            prompt_length = len(prompt)
            if prompt_length > 10000:
                extra_time = ((prompt_length - 10000) // 5000) * 10
                timeout = min(base_timeout + extra_time, 120)
            else:
                timeout = base_timeout

    # Build key rotation list - try ALL available keys for 503 errors
    keys = [api_key]
    all_keys = get_all_keys('google')
    keys.extend([k for k in all_keys if k != api_key])
    
    # Use all available keys (up to 15) instead of limiting to 5
    # This allows the system to try all keys before giving up
    max_attempts = len(keys)
    
    report_progress(f"Gemini API: {len(keys)} keys available, will retry up to {max_attempts} times")

    last_error = None
    failed_keys = set()  # Track keys that consistently fail
    key_failure_count = {}  # Track failure count per key
    
    # Track last successful call time to enforce minimum delay
    last_call_time = 0

    # Fallback models to try if primary model fails
    fallback_models = []
    if model == "gemini-2.5-flash":
        # Use reliable fallback models that are known to be available
        # gemini-2.0-flash-exp is used successfully in vision_prompt_generator.py
        fallback_models = ["gemini-1.5-flash", "gemini-2.0-flash-exp"]

    # Try primary model first
    models_to_try = [model] + fallback_models

    for model_idx, current_model in enumerate(models_to_try):
        if model_idx > 0:
            report_progress(f"Primary model failed, trying fallback model: {current_model}")
        
        for attempt in range(max_attempts):
            # Enforce minimum delay between API calls to prevent rate limiting
            # Gemini free tier: 15 RPM = 4s per request minimum
            # Increased to 5s to reduce 503 errors
            min_delay_between_calls = 5.0
            time_since_last_call = time.time() - last_call_time
            if last_call_time > 0 and time_since_last_call < min_delay_between_calls:
                delay_needed = min_delay_between_calls - time_since_last_call
                report_progress(f"Rate limit protection: waiting {delay_needed:.1f}s before next call...")
                time.sleep(delay_needed)
            
            # Get next key, allowing more retries per key (up to 5 instead of 2)
            key = None
            for k in keys:
                if k not in failed_keys or key_failure_count.get(k, 0) < 5:
                    key = k
                    keys.remove(k)
                    keys.append(k)  # Move to end for round-robin
                    break
            
            if not key:
                # All keys have failed multiple times, reset and try again
                failed_keys.clear()
                key_failure_count.clear()
                key = keys[0]
            
            key_display = f"...{key[-4:]}" if len(key) > 4 else "****"
            
            try:
                # Build endpoint
                url = gemini_text_endpoint(key) if current_model == "gemini-2.5-flash" else \
                      f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={key}"

                headers = {"Content-Type": "application/json"}
                data = {
                    "system_instruction": {
                        "parts": [{"text": "You are a professional AI assistant. Generate valid JSON output when requested."}]
                    },
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.9, "response_mime_type": "application/json"}
                }

                # Report attempt
                report_progress(f"Attempt {attempt+1}/{max_attempts} with key {key_display} using {current_model}")

                # Make request with dynamic timeout (separate connection and read timeout)
                connection_timeout = 60  # 60 seconds to establish connection
                read_timeout = timeout  # Full timeout for reading response
                
                # Record call time for rate limiting
                last_call_time = time.time()
                
                r = requests.post(url, headers=headers, json=data, timeout=(connection_timeout, read_timeout))

                # Check for 503 specifically
                if r.status_code == 503:
                    last_error = requests.HTTPError(f"503 Service Unavailable", response=r)
                    failed_keys.add(key)  # Mark key as temporarily failing
                    key_failure_count[key] = key_failure_count.get(key, 0) + 1
                    
                    if attempt < max_attempts - 1:
                        # Aggressive exponential backoff for 503: 10s, 20s, 30s, 40s, 50s (capped at 60s)
                        # 503 errors indicate server overload, need longer delays
                        backoff = min(10 * (attempt + 1), 60)
                        
                        remaining = max_attempts - attempt - 1
                        report_progress(f"HTTP 503 error. Retrying with different key in {backoff}s ({remaining} attempts remaining)...")
                        time.sleep(backoff)
                    else:
                        report_progress(f"HTTP 503 error on final attempt with {current_model}")
                    continue

                # Check for rate limit (429)
                if r.status_code == 429:
                    last_error = requests.HTTPError(f"429 Rate Limit", response=r)
                    failed_keys.add(key)  # Mark key as rate-limited
                    key_failure_count[key] = key_failure_count.get(key, 0) + 1
                    
                    if attempt < max_attempts - 1:
                        # Use exponential backoff for rate limits: 8s, 12s, 16s, 20s
                        # Rate limits need longer delays to give keys time to recover
                        backoff = min(8 + 4 * attempt, 20)
                        remaining = max_attempts - attempt - 1
                        report_progress(f"Rate limit (429). Trying next key in {backoff}s ({remaining} attempts remaining)...")
                        time.sleep(backoff)
                    else:
                        report_progress(f"Rate limit (429) on final attempt with {current_model}")
                    continue

                # Raise for other HTTP errors (4xx client errors should fail fast)
                if 400 <= r.status_code < 500 and r.status_code not in [429, 503]:
                    # Client errors (400, 401, 403, 404) - don't retry
                    r.raise_for_status()

                # For other 5xx errors, retry with moderate backoff
                if 500 <= r.status_code < 600:
                    last_error = requests.HTTPError(f"{r.status_code} Server Error", response=r)
                    failed_keys.add(key)
                    key_failure_count[key] = key_failure_count.get(key, 0) + 1
                    
                    if attempt < max_attempts - 1:
                        # Moderate backoff for 5xx errors: 5s, 10s, 15s, 20s
                        backoff = min(5 * (attempt + 1), 20)
                        remaining = max_attempts - attempt - 1
                        report_progress(f"HTTP {r.status_code} error. Retrying in {backoff}s ({remaining} attempts remaining)...")
                        time.sleep(backoff)
                    continue

                # Success!
                r.raise_for_status()

                # Parse response
                out = r.json()
                txt = out["candidates"][0]["content"]["parts"][0]["text"]
                
                # Report success
                if model_idx > 0:
                    report_progress(f"Success with fallback model {current_model} using key {key_display}")
                else:
                    report_progress(f"Success with {current_model}")
                
                return parse_llm_response_safe(txt, "Gemini")

            except requests.exceptions.HTTPError as e:
                # HTTP errors already handled above
                if hasattr(e, 'response') and e.response and e.response.status_code == 503:
                    last_error = e
                    failed_keys.add(key)
                    key_failure_count[key] = key_failure_count.get(key, 0) + 1
                    
                    if attempt < max_attempts - 1:
                        # Aggressive exponential backoff for 503: 10s, 20s, 30s, 40s, 50s (capped at 60s)
                        # 503 errors indicate server overload, need longer delays
                        backoff = min(10 * (attempt + 1), 60)
                        
                        remaining = max_attempts - attempt - 1
                        report_progress(f"HTTP 503 error. Retrying with different key in {backoff}s ({remaining} attempts remaining)...")
                        time.sleep(backoff)
                    continue
                else:
                    # Other HTTP errors - don't retry current model
                    last_error = e
                    break

            except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout) as e:
                # Retry timeout errors with next key
                last_error = e
                failed_keys.add(key)
                key_failure_count[key] = key_failure_count.get(key, 0) + 1
                
                if attempt < max_attempts - 1:
                    backoff = 5  # 5s delay for timeouts
                    remaining = max_attempts - attempt - 1
                    report_progress(f"Request timeout ({timeout}s). Trying next key in {backoff}s ({remaining} attempts remaining)...")
                    time.sleep(backoff)
                    continue
                else:
                    # Last attempt - will try fallback model if available
                    report_progress(f"Request timeout on final attempt with {current_model}")
                    break

            except Exception as e:
                # Non-HTTP, non-timeout errors - raise immediately
                last_error = e
                raise

        # If we get here, all attempts with current model failed
        # Continue to next model if available
        if model_idx < len(models_to_try) - 1:
            continue
        else:
            break

    # All retries and fallback models exhausted
    if last_error:
        # Check if it's a timeout error and provide helpful message
        if isinstance(
            last_error,
            (requests.exceptions.Timeout, requests.exceptions.ReadTimeout)
        ):
            raise RuntimeError(
                f"Gemini API request timed out after {timeout}s (tried {max_attempts} retries with smart delays across {len(models_to_try)} models). "
                f"For long scripts ({duration_seconds}s), generation can take several minutes. "
                f"Suggestions: (1) Check your internet connection and firewall settings, "
                f"(2) Verify your API keys are valid and not rate-limited, "
                f"(3) Try again in a few moments, "
                f"(4) Consider breaking the script into shorter segments."
            ) from last_error
        # Check if it's a 503 error and provide helpful message
        elif (
            isinstance(last_error, requests.exceptions.HTTPError) and
            (
                (
                    hasattr(last_error, 'response') and
                    last_error.response is not None and
                    last_error.response.status_code == 503
                ) or
                "503" in str(last_error)
            )
        ):
            raise RuntimeError(
                f"Gemini API service unavailable after {max_attempts} retries with smart delays across {len(models_to_try)} models (HTTP 503). "
                f"This error indicates that Google's Gemini servers are temporarily overloaded or under maintenance. "
                f"We tried {', '.join(models_to_try)} but all returned 503 errors. "
                f"Suggestions: (1) Wait 2-5 minutes and try again (servers often recover quickly), "
                f"(2) Try during off-peak hours for better availability, "
                f"(3) Check Google's service status at https://status.cloud.google.com/, "
                f"(4) All {len(keys)} API keys were attempted with proper rate limiting."
            ) from last_error
        # Check if it's a 429 rate limit error and provide helpful message
        elif (
            isinstance(last_error, requests.exceptions.HTTPError) and
            (
                (
                    hasattr(last_error, 'response') and
                    last_error.response is not None and
                    last_error.response.status_code == 429
                ) or
                "429" in str(last_error)
            )
        ):
            raise RuntimeError(
                f"Gemini API rate limit exceeded after {max_attempts} retries with smart delays across {len(keys)} API key(s) (HTTP 429). "
                f"This error indicates you've exceeded Google's request quota limits. "
                f"We tried all {len(keys)} available API key(s) with {', '.join(models_to_try)} model(s) with proper rate limiting delays, but all were rate-limited. "
                f"Suggestions: (1) Wait 1-2 minutes before retrying - quotas often reset quickly, "
                f"(2) Reduce the frequency of requests or add delays between operations, "
                f"(3) Check your API quota limits at https://aistudio.google.com/app/apikey, "
                f"(4) Consider upgrading your API plan for higher quota limits, "
                f"(5) If you have multiple API keys, ensure they are correctly configured in config.json under 'google_keys'. "
                f"Note: Even if keys work individually, rapid successive requests can trigger rate limits."
            ) from last_error
        else:
            # For other errors, use the generic message
            raise RuntimeError(f"Gemini API failed after {max_attempts} attempts: {last_error}") from last_error
    else:
        raise RuntimeError("Gemini API failed with unknown error")

def _calculate_text_similarity(text1, text2):
    """
    Calculate similarity between two texts using Jaccard similarity algorithm.
    
    Jaccard similarity = |intersection| / |union| of word sets
    Returns a value between 0.0 (completely different) and 1.0 (identical).
    
    Args:
        text1: First text string
        text2: Second text string
    
    Returns:
        float: Similarity score between 0.0 and 1.0
    """
    if not text1 or not text2:
        return 0.0

    # Normalize: lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    # Jaccard similarity: intersection / union
    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0

def _validate_scene_uniqueness(scenes, similarity_threshold=0.8):
    """
    Validate that scenes are unique (not duplicates).
    Checks both prompt_vi and prompt_tgt for similarity.
    
    Args:
        scenes: List of scene dicts with prompt_vi/prompt_tgt
        similarity_threshold: Maximum allowed similarity (default 0.8 = 80%)
    
    Returns:
        List of duplicate pairs found: [(scene1_idx, scene2_idx, similarity), ...]
    """
    duplicates = []

    for i in range(len(scenes)):
        for j in range(i + 1, len(scenes)):
            scene1 = scenes[i]
            scene2 = scenes[j]

            # Check both Vietnamese and target prompts
            prompt1_vi = scene1.get("prompt_vi", "")
            prompt2_vi = scene2.get("prompt_vi", "")
            prompt1_tgt = scene1.get("prompt_tgt", "")
            prompt2_tgt = scene2.get("prompt_tgt", "")

            # Calculate similarity for both language versions
            sim_vi = _calculate_text_similarity(prompt1_vi, prompt2_vi)
            sim_tgt = _calculate_text_similarity(prompt1_tgt, prompt2_tgt)

            # Use the higher similarity score
            max_sim = max(sim_vi, sim_tgt)

            if max_sim >= similarity_threshold:
                duplicates.append((i + 1, j + 1, max_sim))  # 1-based indexing for display

    return duplicates

def _enforce_character_consistency(scenes, character_bible):
    """
    Store character visual identity details for reference.
    Character consistency is now handled via the character_details field in build_prompt_json(),
    not by modifying the scene prompts (which would cause TTS to read technical info).
    
    This function now only validates that character_bible data exists,
    without modifying scene prompts.
    
    Args:
        scenes: List of scene dicts
        character_bible: List of character dicts with visual_identity field
    
    Returns:
        Scenes unchanged (character consistency handled elsewhere)
    """
    # BUG FIX: Do NOT modify prompt_vi or prompt_tgt
    # Character consistency is handled by build_prompt_json() via character_details field
    # Modifying prompts here causes "CHARACTER CONSISTENCY: ..." to appear in voiceover text
    return scenes

def _validate_idea_relevance(idea, generated_content, threshold=0.15):
    """
    Validate that the generated content is related to the original idea.
    
    This helps catch cases where the LLM generates completely unrelated content.
    Uses word overlap as a simple but effective similarity metric.
    
    Args:
        idea: Original user idea/concept
        generated_content: Dict with title, outline, screenplay from LLM
        threshold: Minimum word overlap ratio (default 0.15 = 15%)
    
    Returns:
        tuple: (is_valid: bool, similarity: float, warning_message: str or None)
    """
    if not idea or not generated_content:
        return True, 0.0, None

    # Extract key content from generated script
    title = generated_content.get("title_vi", "") or generated_content.get("title_tgt", "")
    outline = generated_content.get("outline_vi", "") or generated_content.get("outline_tgt", "")
    screenplay = generated_content.get("screenplay_vi", "") or generated_content.get("screenplay_tgt", "")

    # Combine all generated text
    generated_text = f"{title} {outline} {screenplay}".lower()
    idea_text = idea.lower()

    # Extract important words from idea (filter out common stop words)
    # Use module-level constant for better maintainability
    idea_words = [w for w in idea_text.split() if len(w) >= MIN_WORD_LENGTH and w not in STOP_WORDS]

    if not idea_words:
        return True, 0.0, None  # Can't validate if no meaningful words

    # Count how many idea words appear in generated content
    matched_words = [w for w in idea_words if w in generated_text]
    similarity = len(matched_words) / len(idea_words) if idea_words else 0.0

    is_valid = similarity >= threshold

    if not is_valid:
        # Smart truncation: only add '...' if idea is actually longer than max length
        idea_display = idea if len(idea) <= MAX_IDEA_DISPLAY_LENGTH else idea[:MAX_IDEA_DISPLAY_LENGTH] + '...'
        warning = (
            f"⚠️ CẢNH BÁO: Kịch bản có thể không liên quan đến ý tưởng!\n"
            f"   Ý tưởng: '{idea_display}'\n"
            f"   Độ liên quan: {similarity*100:.1f}% (ngưỡng tối thiểu: {threshold*100:.1f}%)\n"
            f"   Từ khóa trong ý tưởng: {', '.join(idea_words[:10])}\n"
            f"   Từ khóa xuất hiện: {', '.join(matched_words[:10]) if matched_words else 'Không có'}"
        )
        return False, similarity, warning

    return True, similarity, None


def _validate_scene_continuity(scenes: List[Dict[str, Any]]) -> List[str]:
    """
    Validate scene continuity to ensure scenes can be assembled into a complete video.
    Checks for:
    1. Location continuity (sudden jumps without explanation)
    2. Time continuity (day/night consistency)
    3. Character presence (characters appearing/disappearing without reason)
    
    Args:
        scenes: List of scene dicts
        
    Returns:
        List of continuity issue warnings
    """
    if not scenes or len(scenes) < 2:
        return []

    issues = []

    for i in range(1, len(scenes)):
        prev_scene = scenes[i-1]
        curr_scene = scenes[i]

        # Check location continuity
        prev_loc = prev_scene.get("location", "").lower()
        curr_loc = curr_scene.get("location", "").lower()
        transition = curr_scene.get("transition_from_previous", "").lower()

        # If location changes dramatically without transition explanation
        if prev_loc and curr_loc and prev_loc != curr_loc:
            if not transition or len(transition) < 10:
                issues.append(
                    f"Scene {i} -> {i+1}: Location jump from '{prev_loc}' to '{curr_loc}' "
                    f"without clear transition explanation"
                )

        # Check time continuity
        prev_time = prev_scene.get("time_of_day", "").lower()
        curr_time = curr_scene.get("time_of_day", "").lower()

        # Detect illogical time jumps (e.g., night -> day in same location without explanation)
        if prev_time and curr_time and prev_loc == curr_loc:
            time_keywords = {
                "day": ["day", "morning", "afternoon", "noon"],
                "night": ["night", "evening", "dusk", "dawn"],
            }

            prev_is_day = any(kw in prev_time for kw in time_keywords["day"])
            prev_is_night = any(kw in prev_time for kw in time_keywords["night"])
            curr_is_day = any(kw in curr_time for kw in time_keywords["day"])
            curr_is_night = any(kw in curr_time for kw in time_keywords["night"])

            if (prev_is_day and curr_is_night) or (prev_is_night and curr_is_day):
                if not transition or "time" not in transition:
                    issues.append(
                        f"Scene {i} -> {i+1}: Time jump from {prev_time} to {curr_time} "
                        f"in same location without explanation"
                    )

        # Check character continuity
        prev_chars = set(prev_scene.get("characters", []))
        curr_chars = set(curr_scene.get("characters", []))

        # Characters disappearing
        disappeared = prev_chars - curr_chars
        if disappeared and len(prev_chars) > 1:  # Only flag if multiple characters
            issues.append(
                f"Scene {i} -> {i+1}: Characters {disappeared} disappeared without explanation"
            )

        # New characters appearing
        appeared = curr_chars - prev_chars
        if appeared and i > 1:  # After first scene
            # This is less critical, but note it
            pass  # New characters can appear, so we don't flag this as an issue

    return issues


def _validate_dialogue_language(scenes, target_lang):
    """
    Validate that dialogue text_tgt fields are in the correct target language.
    
    This is a simple heuristic check - we look for signs that dialogues
    might be in the wrong language (e.g., Vietnamese text when English is expected).
    
    Args:
        scenes: List of scene dicts with dialogues
        target_lang: Target language code (e.g., 'en', 'ja', 'vi')
    
    Returns:
        tuple: (is_valid: bool, warning_message: str or None)
    """
    if not scenes or target_lang == 'vi':
        # Can't validate Vietnamese or if no scenes
        return True, None

    issues = []

    for scene_idx, scene in enumerate(scenes, 1):
        dialogues = scene.get("dialogues", [])
        for dlg_idx, dlg in enumerate(dialogues, 1):
            if isinstance(dlg, dict):
                text_tgt = dlg.get("text_tgt", "")
                if text_tgt:
                    # Simple heuristic: check for Vietnamese characters using module constant
                    has_vietnamese = any(c.lower() in VIETNAMESE_CHARS for c in text_tgt)

                    # If target is not Vietnamese but text has Vietnamese chars
                    if has_vietnamese and target_lang != 'vi':
                        speaker = dlg.get("speaker", "Unknown")
                        issues.append(
                            f"Scene {scene_idx}, Dialogue {dlg_idx} ({speaker}): "
                            f"Contains Vietnamese characters but target language is {LANGUAGE_NAMES.get(target_lang, target_lang)}"
                        )

    if issues:
        warning = (
            f"⚠️ CẢNH BÁO: Một số lời thoại có thể không đúng ngôn ngữ đích!\n\n"
            f"Phát hiện {len(issues)} vấn đề:\n" +
            "\n".join(f"- {issue}" for issue in issues[:5])  # Show first 5
        )
        if len(issues) > 5:
            warning += f"\n... và {len(issues) - 5} vấn đề khác"

        return False, warning

    return True, None

def _generate_single_scene(scene_num, total_scenes, idea, style, output_lang, duration, previous_scenes, character_bible, outline, provider, api_key, progress_callback, domain=None, topic=None):
    """
    Generate a single scene with context from previous scenes.
    
    Args:
        scene_num: Current scene number (1-indexed)
        total_scenes: Total number of scenes
        idea: Original video idea
        style: Video style
        output_lang: Output language code
        duration: Duration for this scene in seconds
        previous_scenes: List of previously generated scenes for context
        character_bible: Character bible from previous generation or empty list
        outline: Story outline for consistency
        provider: LLM provider
        api_key: API key
        progress_callback: Progress callback function
        domain: Optional domain for custom prompt handling
        topic: Optional topic for custom prompt handling
        
    Returns:
        Dict with scene data
    """
    def report_progress(msg, percent):
        if progress_callback:
            progress_callback(msg, percent)
    
    target_language = LANGUAGE_NAMES.get(output_lang, 'Vietnamese (Tiếng Việt)')
    
    # Check if domain requires no-character narration
    no_character_domains = [
        ("KHOA HỌC GIÁO DỤC", "PANORA - Nhà Tường thuật Khoa học"),
    ]
    requires_no_characters = (domain, topic) in no_character_domains if domain and topic else False
    
    # Build context from previous scenes
    context = ""
    if previous_scenes:
        context = "\n**PREVIOUS SCENES CONTEXT (for continuity):**\n"
        for i, prev in enumerate(previous_scenes[-3:], start=max(1, scene_num-3)):  # Last 3 scenes
            context += f"\nScene {i}:\n"
            context += f"- Location: {prev.get('location', 'N/A')}\n"
            context += f"- Time: {prev.get('time_of_day', 'N/A')}\n"
            if not requires_no_characters:
                context += f"- Characters: {', '.join(prev.get('characters', []))}\n"
            context += f"- Emotion: {prev.get('emotion', 'N/A')}\n"
            context += f"- Story Beat: {prev.get('story_beat', 'N/A')}\n"
            if 'prompt_vi' in prev:
                context += f"- Visual: {prev['prompt_vi'][:150]}...\n"
    
    # Build character context (skip for no-character domains)
    char_context = ""
    if character_bible and not requires_no_characters:
        char_context = "\n**CHARACTER BIBLE (maintain consistency):**\n"
        for char in character_bible:
            char_context += f"\n{char.get('name', 'Unknown')}:\n"
            char_context += f"- Role: {char.get('role', '')}\n"
            char_context += f"- Visual: {char.get('visual_identity', '')}\n"
            char_context += f"- Trait: {char.get('key_trait', '')}\n"
    
    # Determine story position
    if scene_num == 1:
        story_position = "OPENING - Create strong hook (3s)"
    elif scene_num == total_scenes:
        story_position = "ENDING - Resolution/conclusion"
    elif scene_num == total_scenes // 2:
        story_position = "MIDPOINT - Plot twist/turning point"
    else:
        story_position = f"MIDDLE - Rising action (Scene {scene_num}/{total_scenes})"
    
    # Get style guidance
    style_guidance = _get_style_specific_guidance(style, idea=idea)
    
    # Build prompt based on domain requirements
    if requires_no_characters:
        # No-character scene prompt (PANORA and similar)
        prompt = f"""You are a science education content creator. Generate Scene {scene_num} of {total_scenes} for a video.

**STORY POSITION**: {story_position}

**ORIGINAL IDEA**: {idea}

**STYLE**: {style}
{style_guidance}

**TARGET LANGUAGE**: {target_language}
- ALL text_tgt, prompt_tgt, voiceover_tgt fields MUST be in {target_language}

**STORY OUTLINE**: {outline if outline else "Develop naturally based on idea"}

{context}

**SCENE {scene_num} REQUIREMENTS**:
- Duration: {duration} seconds
- Connect logically to previous scene (location, time, visual continuity)
- Clear emotion and story beat
- Scientific/medical visual elements (3D simulations, holograms, data overlays)
- Second-person voiceover addressing audience ("Bạn", "Cơ thể của bạn", "Não của bạn")

**CRITICAL**: NO character names, NO fictional personas, NO dialogue between characters

Return ONLY valid JSON (no extra text):

{{
  "prompt_vi": "Mô tả hình ảnh y khoa/khoa học bằng tiếng Việt - KHÔNG có tên nhân vật",
  "prompt_tgt": "Scientific/medical visual description in {target_language} - NO character names",
  "duration": {duration},
  "voiceover_vi": "Lời thoại ngôi thứ hai bằng tiếng Việt (Bạn, Cơ thể của bạn)",
  "voiceover_tgt": "Second-person narration in {target_language}",
  "location": "Specific scientific/medical location",
  "time_of_day": "Day/Night (if relevant)",
  "camera_shot": "Wide/Close-up/Tracking (focusing on scientific elements)",
  "lighting_mood": "Bright/Dark/Clinical (appropriate for medical/scientific content)",
  "emotion": "Primary emotion of this scene",
  "story_beat": "Setup/Rising action/Twist/Climax/Resolution",
  "transition_from_previous": "How this connects to previous scene",
  "style_notes": "Specific {style} style elements",
  "visual_elements": ["List of visual elements: hologram, 3D simulation, data overlay, etc."],
  "visual_notes": "Props, colors, scientific accuracy, data overlays"
}}

CRITICAL: Use second-person voiceover only, NO character names or fictional personas."""
    else:
        # Standard character-based scene prompt
        prompt = f"""You are an expert screenplay writer. Generate Scene {scene_num} of {total_scenes} for a video.

**STORY POSITION**: {story_position}

**ORIGINAL IDEA**: {idea}

**STYLE**: {style}
{style_guidance}

**TARGET LANGUAGE**: {target_language}
- ALL text_tgt, prompt_tgt fields MUST be in {target_language}

**STORY OUTLINE**: {outline if outline else "Develop naturally based on idea"}

{char_context}

{context}

**SCENE {scene_num} REQUIREMENTS**:
- Duration: {duration} seconds
- Connect logically to previous scene (location, time, character continuity)
- Clear emotion and story beat
- Specific visual details (actions, lighting, camera movement)
- Natural dialogue in {target_language}

Return ONLY valid JSON (no extra text):

{{
  "prompt_vi": "Visual description in Vietnamese with specific actions, lighting, camera",
  "prompt_tgt": "Visual description in {target_language} with full character details",
  "duration": {duration},
  "characters": ["Character names appearing in this scene"],
  "location": "Specific location",
  "time_of_day": "Day/Night/Dawn/Dusk (consistent with previous if same location)",
  "camera_shot": "Wide/Close-up/POV/Tracking with movement",
  "lighting_mood": "Bright/Dark/Warm/Cold (must match time_of_day)",
  "emotion": "Primary emotion of this scene",
  "story_beat": "Setup/Rising action/Twist/Climax/Resolution",
  "transition_from_previous": "How this connects to previous scene",
  "style_notes": "Specific {style} style elements",
  "dialogues": [
    {{"speaker": "Name", "text_vi": "Vietnamese dialogue", "text_tgt": "Dialogue in {target_language}", "emotion": "emotion"}}
  ],
  "visual_notes": "Props, colors, symbolism, continuity details"
}}

CRITICAL: Maintain character visual_identity consistency. If characters appeared before, use EXACT same appearance."""
    
    # Call LLM
    gk, ok = _load_keys()
    if provider.lower().startswith("gemini"):
        key = api_key or gk
        if not key:
            raise RuntimeError("Chưa cấu hình Google API Key cho Gemini.")
        
        # Note: Progress is managed by the parent function (generate_script_scene_by_scene)
        result = _call_gemini(prompt, key, "gemini-2.5-flash", timeout=None, duration_seconds=None, progress_callback=None)
    else:
        key = api_key or ok
        if not key:
            raise RuntimeError("Chưa cấu hình OpenAI API Key cho GPT-4 Turbo.")
        
        # Note: Progress is managed by the parent function (generate_script_scene_by_scene)
        result = _call_openai(prompt, key, "gpt-4-turbo")
    
    return result


def generate_script_scene_by_scene(idea, style, duration_seconds, provider='Gemini 2.5', api_key=None, output_lang='vi', domain=None, topic=None, voice_config=None, progress_callback=None):
    """
    Generate video script scene-by-scene for long videos to avoid JSON truncation.
    
    This function generates each scene individually with context from previous scenes,
    avoiding the issue of large JSON responses being truncated by the LLM.
    
    Args:
        idea: Video idea/concept
        style: Video style
        duration_seconds: Total duration
        provider: LLM provider (Gemini/OpenAI)
        api_key: Optional API key
        output_lang: Output language code
        domain: Optional domain expertise
        topic: Optional topic within domain
        voice_config: Optional voice configuration dict
        progress_callback: Optional function(message: str, percent: int) for progress updates
    
    Returns:
        Script data dict with scenes, character_bible, etc.
    """
    def report_progress(msg, percent):
        if progress_callback:
            progress_callback(msg, percent)
    
    report_progress("Đang chuẩn bị scene-by-scene generation...", 5)
    
    gk, ok = _load_keys()
    n, per = _n_scenes(duration_seconds)
    mode = _mode_from_duration(duration_seconds)
    target_language = LANGUAGE_NAMES.get(output_lang, 'Vietnamese (Tiếng Việt)')
    
    report_progress(f"Tính toán: {n} cảnh cần tạo (total {duration_seconds}s)", 10)
    
    # Check if domain requires no-character narration (like PANORA)
    no_character_domains = [
        ("KHOA HỌC GIÁO DỤC", "PANORA - Nhà Tường thuật Khoa học"),
    ]
    requires_no_characters = (domain, topic) in no_character_domains if domain and topic else False
    
    # Check if custom prompt exists
    custom_prompt = None
    if domain and topic:
        try:
            from services.domain_custom_prompts import get_custom_prompt
            custom_prompt = get_custom_prompt(domain, topic)
            if custom_prompt:
                print(f"[INFO] Scene-by-scene using custom prompt for {domain}/{topic}")
        except ImportError:
            pass
    
    # Step 1: Generate metadata (title, character bible, outline)
    report_progress("Đang tạo metadata (title, character bible, outline)...", 15)
    
    # Build metadata prompt based on domain requirements
    if requires_no_characters:
        # No-character metadata prompt (PANORA and similar)
        system_instruction = custom_prompt if custom_prompt else "You are a science education content creator."
        metadata_prompt = f"""{system_instruction}

Create metadata for a {duration_seconds}s video.

**IDEA**: {idea}
**STYLE**: {style}
**MODE**: {mode} ({n} scenes)
**TARGET LANGUAGE**: {target_language}

**CRITICAL**: NO character names, NO fictional personas. Use second-person narration addressing the audience.

Generate ONLY valid JSON (no extra text):

{{
  "title_vi": "Tiêu đề hấp dẫn (Vietnamese)",
  "title_tgt": "Title in {target_language}",
  "hook_summary": "What makes viewer watch first 3s?",
  "character_bible": [],
  "character_bible_tgt": [],
  "outline_vi": "Dàn ý theo 5 giai đoạn: VẤN ĐỀ → PHẢN ỨNG → LEO THANG → ĐIỂM GIỚI HẠN → TOÀN CẢNH",
  "outline_tgt": "5-stage outline in {target_language}",
  "screenplay_vi": "Screenplay với VOICEOVER ngôi thứ hai (Bạn, Cơ thể của bạn) và VISUAL DESCRIPTION (3D/2D y tế, hologram)",
  "screenplay_tgt": "Screenplay in {target_language} with second-person voiceover",
  "emotional_arc": "Emotional journey: [Start] → [Peaks & Valleys] → [End]"
}}

NO character names. Focus on scientific/medical visuals and second-person narration."""
    else:
        # Standard character-based metadata prompt
        metadata_prompt = f"""You are an expert screenplay writer. Create metadata for a {duration_seconds}s video.

**IDEA**: {idea}
**STYLE**: {style}
**MODE**: {mode} ({n} scenes)
**TARGET LANGUAGE**: {target_language}

Generate ONLY valid JSON (no extra text):

{{
  "title_vi": "Engaging Vietnamese title",
  "title_tgt": "Title in {target_language}",
  "hook_summary": "What makes viewer watch first 3s?",
  "character_bible": [
    {{
      "name": "Character name",
      "role": "Role in story",
      "key_trait": "Core personality",
      "motivation": "Deep drive",
      "default_behavior": "Typical behavior",
      "visual_identity": "Detailed appearance (face, eyes, hair, clothing, accessories) - NEVER changes",
      "archetype": "Character archetype",
      "fatal_flaw": "Character flaw",
      "goal_external": "External goal",
      "goal_internal": "Internal goal"
    }}
  ],
  "character_bible_tgt": [
    {{
      "name": "Character name",
      "role": "Role in {target_language}",
      "key_trait": "Trait in {target_language}",
      "motivation": "Motivation in {target_language}",
      "default_behavior": "Behavior in {target_language}",
      "visual_identity": "Appearance in {target_language}",
      "archetype": "Archetype in {target_language}",
      "fatal_flaw": "Flaw in {target_language}",
      "goal_external": "External goal in {target_language}",
      "goal_internal": "Internal goal in {target_language}"
    }}
  ],
  "outline_vi": "Story outline in Vietnamese: ACT structure + key emotional beats + major plot points",
  "outline_tgt": "Story outline in {target_language}",
  "screenplay_vi": "Brief screenplay overview in Vietnamese",
  "screenplay_tgt": "Brief screenplay overview in {target_language}",
  "emotional_arc": "Emotional journey: [Start] → [Peaks & Valleys] → [End]"
}}

Create 2-4 characters maximum. Focus on strong, memorable characters."""
    
    # Call LLM for metadata
    if provider.lower().startswith("gemini"):
        key = api_key or gk
        if not key:
            raise RuntimeError("Chưa cấu hình Google API Key cho Gemini.")
        metadata = _call_gemini(metadata_prompt, key, "gemini-2.5-flash", timeout=None, duration_seconds=None, progress_callback=None)
    else:
        key = api_key or ok
        if not key:
            raise RuntimeError("Chưa cấu hình OpenAI API Key cho GPT-4 Turbo.")
        metadata = _call_openai(metadata_prompt, key, "gpt-4-turbo")
    
    report_progress("Metadata đã tạo xong", 25)
    
    # Step 2: Generate scenes one by one
    scenes = []
    character_bible = metadata.get("character_bible", [])
    outline = metadata.get("outline_vi", "")
    
    for scene_num in range(1, n + 1):
        # Calculate progress percentage (25% to 90%)
        scene_progress = 25 + int((scene_num / n) * 65)
        report_progress(f"Đang tạo cảnh {scene_num}/{n}...", scene_progress)
        
        try:
            scene = _generate_single_scene(
                scene_num=scene_num,
                total_scenes=n,
                idea=idea,
                style=style,
                output_lang=output_lang,
                duration=per[scene_num - 1],
                previous_scenes=scenes,
                character_bible=character_bible,
                outline=outline,
                provider=provider,
                api_key=api_key,
                progress_callback=progress_callback,
                domain=domain,
                topic=topic
            )
            
            # Ensure duration is set correctly
            scene["duration"] = int(per[scene_num - 1])
            scenes.append(scene)
            
            report_progress(f"✓ Cảnh {scene_num}/{n} hoàn tất", scene_progress)
            
        except Exception as e:
            report_progress(f"⚠ Lỗi tại cảnh {scene_num}: {str(e)}", scene_progress)
            # Try one more time
            try:
                scene = _generate_single_scene(
                    scene_num=scene_num,
                    total_scenes=n,
                    idea=idea,
                    style=style,
                    output_lang=output_lang,
                    duration=per[scene_num - 1],
                    previous_scenes=scenes,
                    character_bible=character_bible,
                    outline=outline,
                    provider=provider,
                    api_key=api_key,
                    progress_callback=progress_callback,
                    domain=domain,
                    topic=topic
                )
                scene["duration"] = int(per[scene_num - 1])
                scenes.append(scene)
                report_progress(f"✓ Cảnh {scene_num}/{n} hoàn tất (retry)", scene_progress)
            except Exception as retry_error:
                raise RuntimeError(f"Failed to generate scene {scene_num} after retry: {str(retry_error)}")
    
    # Step 3: Combine metadata and scenes
    report_progress("Đang xác thực kịch bản...", 92)
    
    result = metadata.copy()
    result["scenes"] = scenes
    
    # Run validations
    continuity_issues = _validate_scene_continuity(scenes) if scenes else []
    if continuity_issues:
        print(f"[WARN] Scene continuity issues detected: {continuity_issues}")
        result["scene_continuity_warnings"] = continuity_issues
    
    # Enforce character consistency
    if character_bible:
        report_progress("Đang tối ưu character consistency...", 95)
        result["scenes"] = _enforce_character_consistency(scenes, character_bible)
    
    # Store voice configuration
    if voice_config:
        result["voice_config"] = voice_config
    
    report_progress("Hoàn tất scene-by-scene generation!", 100)
    
    return result


def generate_script(idea, style, duration_seconds, provider='Gemini 2.5', api_key=None, output_lang='vi', domain=None, topic=None, voice_config=None, progress_callback=None):
    """
    Generate video script with optional domain/topic expertise and voice settings
    
    Args:
        idea: Video idea/concept
        style: Video style
        duration_seconds: Total duration
        provider: LLM provider (Gemini/OpenAI)
        api_key: Optional API key
        output_lang: Output language code
        domain: Optional domain expertise (e.g., "Marketing & Branding")
        topic: Optional topic within domain (e.g., "Giới thiệu sản phẩm")
        voice_config: Optional voice configuration dict with provider, voice_id, language_code
        progress_callback: Optional function(message: str, percent: int) for progress updates
    
    Returns:
        Script data dict with scenes, character_bible, etc.
    """
    def report_progress(msg, percent):
        """Helper to report progress if callback is provided"""
        if progress_callback:
            progress_callback(msg, percent)

    report_progress("Đang chuẩn bị...", 5)

    # OPTIMIZATION: Use scene-by-scene generation for long videos (>3 minutes)
    # This avoids JSON truncation issues with large responses
    if duration_seconds > 180:  # 3 minutes
        report_progress(f"Video dài ({duration_seconds}s) - Sử dụng scene-by-scene generation", 8)
        return generate_script_scene_by_scene(
            idea=idea,
            style=style,
            duration_seconds=duration_seconds,
            provider=provider,
            api_key=api_key,
            output_lang=output_lang,
            domain=domain,
            topic=topic,
            voice_config=voice_config,
            progress_callback=progress_callback
        )

    gk, ok=_load_keys()
    n, per = _n_scenes(duration_seconds)
    mode = _mode_from_duration(duration_seconds)

    report_progress("Đang xây dựng prompt...", 10)

    # Build base prompt
    prompt=_schema_prompt(idea=idea, style_vi=style, out_lang=output_lang, n=n, per=per, mode=mode, topic=topic, domain=domain)

    # Prepend expert intro if domain/topic selected AND no custom prompt exists
    # Custom prompts (from domain_custom_prompts.py) already contain full system instructions
    # Adding expert_intro would duplicate/conflict with custom prompts
    if domain and topic:
        # Check if custom prompt exists for this domain/topic
        has_custom_prompt = False
        try:
            from services.domain_custom_prompts import get_custom_prompt
            custom_prompt = get_custom_prompt(domain, topic)
            has_custom_prompt = custom_prompt is not None
        except ImportError:
            pass  # No custom prompts module, proceed with expert intro
        
        # Only add expert intro if NO custom prompt exists
        if not has_custom_prompt:
            report_progress(f"Đang thêm chuyên môn {domain}...", 15)
            try:
                from services.domain_prompts import build_expert_intro
                # Map language code to vi/en for domain prompts
                prompt_lang = "vi" if output_lang == "vi" else "en"

                # OPTIMIZATION: Use cached domain prompt if available
                cache_key = f"{domain}|{topic}|{prompt_lang}"
                if cache_key in _domain_prompt_cache:
                    expert_intro = _domain_prompt_cache[cache_key]
                else:
                    expert_intro = build_expert_intro(domain, topic, prompt_lang)
                    _domain_prompt_cache[cache_key] = expert_intro

                prompt = f"{expert_intro}\n\n{prompt}"
            except Exception as e:
                # Log but don't fail if domain prompt loading fails
                print(f"[WARN] Could not load domain prompt: {e}")
        else:
            # Custom prompt is already included in _schema_prompt, no need to add expert intro
            print(f"[INFO] Using custom prompt for {domain}/{topic}, skipping expert intro")

    # Call LLM
    if provider.lower().startswith("gemini"):
        key=api_key or gk
        if not key: raise RuntimeError("Chưa cấu hình Google API Key cho Gemini.")

        # OPTIMIZATION: More informative progress for long scenarios
        # Updated message to reflect improved timeout and retry logic
        if duration_seconds > 300:  # 5+ minutes
            report_progress(f"Đang chờ phản hồi từ Gemini... (kịch bản {duration_seconds}s có thể mất 5-10 phút với retry tự động)", 25)
        elif duration_seconds > 120:  # 2+ minutes
            report_progress("Đang chờ phản hồi từ Gemini... (có thể mất 3-5 phút với retry tự động)", 25)
        else:
            report_progress("Đang chờ phản hồi từ Gemini... (có thể mất 1-2 phút)", 25)
        
        res=_call_gemini(prompt, key, "gemini-2.5-flash", timeout=None, duration_seconds=duration_seconds, progress_callback=progress_callback)
        report_progress("Đã nhận phản hồi từ Gemini", 50)
    else:
        key=api_key or ok
        if not key: raise RuntimeError("Chưa cấu hình OpenAI API Key cho GPT-4 Turbo.")

        # OPTIMIZATION: More informative progress for long scenarios
        # Updated to reflect actual performance
        if duration_seconds > 300:
            report_progress(f"Đang chờ phản hồi từ OpenAI... (kịch bản {duration_seconds}s có thể mất 1-2 phút)", 25)
        elif duration_seconds > 120:
            report_progress("Đang chờ phản hồi từ OpenAI... (có thể mất 30-60 giây)", 25)
        else:
            report_progress("Đang chờ phản hồi từ OpenAI... (có thể mất 20-40 giây)", 25)

        # FIXED: Use gpt-4-turbo instead of gpt-5
        res=_call_openai(prompt,key,"gpt-4-turbo")
        report_progress("Đã nhận phản hồi từ OpenAI", 50)
    if "scenes" not in res: raise RuntimeError("LLM không trả về đúng schema.")

    report_progress("Đang xác thực kịch bản...", 60)

    # OPTIMIZATION: Run all validation checks in parallel using ThreadPoolExecutor
    # This reduces validation time from ~2-3 seconds to <1 second
    import concurrent.futures

    scenes = res.get("scenes", [])
    character_bible = res.get("character_bible", [])

    # Define validation tasks
    def validate_duplicates():
        duplicates = _validate_scene_uniqueness(scenes, similarity_threshold=0.8)
        if duplicates:
            dup_msg = ", ".join([f"Scene {i} & {j} ({sim*100:.0f}% similar)" for i, j, sim in duplicates])
            print(f"[WARN] Duplicate scenes detected: {dup_msg}")
        return duplicates

    def validate_relevance():
        is_relevant, relevance_score, warning_msg = _validate_idea_relevance(idea, res, threshold=IDEA_RELEVANCE_THRESHOLD)
        if not is_relevant and warning_msg:
            print(warning_msg)
        return is_relevant, relevance_score, warning_msg

    def validate_dialogues():
        dialogue_valid, dialogue_warning = _validate_dialogue_language(scenes, output_lang)
        if not dialogue_valid and dialogue_warning:
            print(dialogue_warning)
        return dialogue_valid, dialogue_warning

    def validate_continuity():
        continuity_issues = _validate_scene_continuity(scenes) if scenes else []
        if continuity_issues:
            print(f"[WARN] Scene continuity issues detected: {continuity_issues}")
        return continuity_issues

    # Run all validations in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_duplicates = executor.submit(validate_duplicates)
        future_relevance = executor.submit(validate_relevance)
        future_dialogues = executor.submit(validate_dialogues)
        future_continuity = executor.submit(validate_continuity)

        # Wait for all to complete
        duplicates = future_duplicates.result()
        is_relevant, relevance_score, warning_msg = future_relevance.result()
        dialogue_valid, dialogue_warning = future_dialogues.result()
        continuity_issues = future_continuity.result()

    # Store validation results
    if not is_relevant and warning_msg:
        res["idea_relevance_warning"] = warning_msg
    res["idea_relevance_score"] = relevance_score

    if not dialogue_valid and dialogue_warning:
        res["dialogue_language_warning"] = dialogue_warning

    if continuity_issues:
        res["scene_continuity_warnings"] = continuity_issues

    report_progress("Đang tối ưu character consistency...", 80)

    # ISSUE #2 FIX: Enforce character consistency
    if character_bible:
        res["scenes"] = _enforce_character_consistency(scenes, character_bible)

    # Store voice configuration in result for consistency
    if voice_config:
        report_progress("Đang lưu voice config...", 90)
        res["voice_config"] = voice_config

    report_progress("Đang điều chỉnh thời lượng cảnh...", 95)

    # ép durations
    for i,d in enumerate(per):
        if i < len(res["scenes"]): res["scenes"][i]["duration"]=int(d)

    report_progress("Hoàn tất!", 100)

    return res


def generate_social_media(script_data, provider='Gemini 2.5', api_key=None):
    """
    Generate social media content in 3 different tones
    
    Args:
        script_data: Script data dictionary with title, outline, screenplay
        provider: LLM provider (Gemini/OpenAI)
        api_key: Optional API key
    
    Returns:
        Dictionary with 3 social media versions (casual, professional, funny)
    """
    gk, ok = _load_keys()

    # Extract key elements from script
    title = script_data.get("title_vi") or script_data.get("title_tgt", "")
    outline = script_data.get("outline_vi") or script_data.get("outline_tgt", "")
    screenplay = script_data.get("screenplay_vi") or script_data.get("screenplay_tgt", "")

    # Build prompt
    prompt = f"""Bạn là chuyên gia Social Media Marketing. Dựa trên kịch bản video sau, hãy tạo 3 phiên bản nội dung mạng xã hội với các tone khác nhau.

**KỊCH BẢN VIDEO:**
Tiêu đề: {title}
Dàn ý: {outline}

**YÊU CẦU:**
Tạo 3 phiên bản post cho mạng xã hội, mỗi phiên bản bao gồm:
1. Title (tiêu đề hấp dẫn)
2. Description (mô tả chi tiết 2-3 câu)
3. Hashtags (5-10 hashtags phù hợp)
4. CTA (Call-to-action mạnh mẽ)
5. Best posting time (thời gian đăng tối ưu)

**3 PHIÊN BẢN:**
- Version 1: Casual/Friendly (TikTok/YouTube Shorts) - Tone thân mật, gần gũi, emoji nhiều
- Version 2: Professional (LinkedIn/Facebook) - Tone chuyên nghiệp, uy tín, giá trị cao
- Version 3: Funny/Engaging (TikTok/Instagram Reels) - Tone hài hước, vui nhộn, viral

Trả về JSON với format:
{{
  "casual": {{
    "title": "...",
    "description": "...",
    "hashtags": ["#tag1", "#tag2", ...],
    "cta": "...",
    "best_time": "...",
    "platform": "TikTok/YouTube Shorts"
  }},
  "professional": {{
    "title": "...",
    "description": "...",
    "hashtags": ["#tag1", "#tag2", ...],
    "cta": "...",
    "best_time": "...",
    "platform": "LinkedIn/Facebook"
  }},
  "funny": {{
    "title": "...",
    "description": "...",
    "hashtags": ["#tag1", "#tag2", ...],
    "cta": "...",
    "best_time": "...",
    "platform": "TikTok/Instagram Reels"
  }}
}}
"""

    # Call LLM
    if provider.lower().startswith("gemini"):
        key = api_key or gk
        if not key:
            raise RuntimeError("Chưa cấu hình Google API Key cho Gemini.")
        res = _call_gemini(prompt, key, "gemini-2.5-flash")
    else:
        key = api_key or ok
        if not key:
            raise RuntimeError("Chưa cấu hình OpenAI API Key cho GPT-4 Turbo.")
        res = _call_openai(prompt, key, "gpt-4-turbo")

    return res


def generate_thumbnail_design(script_data, provider='Gemini 2.5', api_key=None):
    """
    Generate detailed thumbnail design specifications
    
    Args:
        script_data: Script data dictionary with title, outline, screenplay
        provider: LLM provider (Gemini/OpenAI)
        api_key: Optional API key
    
    Returns:
        Dictionary with thumbnail design specifications
    """
    gk, ok = _load_keys()

    # Extract key elements from script
    title = script_data.get("title_vi") or script_data.get("title_tgt", "")
    outline = script_data.get("outline_vi") or script_data.get("outline_tgt", "")
    character_bible = script_data.get("character_bible", [])

    # Build character summary
    char_summary = ""
    if character_bible:
        char_summary = "Nhân vật chính:\n"
        for char in character_bible[:3]:  # Top 3 characters
            char_summary += f"- {char.get('name', 'Unknown')}: {char.get('visual_identity', 'N/A')}\n"

    # Build prompt
    prompt = f"""Bạn là chuyên gia Thiết kế Thumbnail cho YouTube/TikTok. Dựa trên kịch bản video sau, hãy tạo specifications chi tiết cho thumbnail.

**KỊCH BẢN VIDEO:**
Tiêu đề: {title}
Dàn ý: {outline}
{char_summary}

**YÊU CẦU:**
Tạo specifications chi tiết cho thumbnail bao gồm:
1. Concept (ý tưởng tổng thể)
2. Color Palette (bảng màu với mã hex, 3-5 màu)
3. Typography (text overlay, font, size, effects)
4. Layout (composition, focal point, rule of thirds)
5. Visual Elements (các yếu tố cần có: người, vật, background)
6. Style Guide (phong cách tổng thể: photorealistic, cartoon, minimalist...)

Thumbnail phải:
- Nổi bật trong feed (high contrast, bold colors)
- Gây tò mò (create curiosity gap)
- Dễ đọc trên mobile (text lớn, rõ ràng)
- Phù hợp với nội dung video

Trả về JSON với format:
{{
  "concept": "Ý tưởng tổng thể cho thumbnail...",
  "color_palette": [
    {{"name": "Primary", "hex": "#FF5733", "usage": "Background"}},
    {{"name": "Accent", "hex": "#33FF57", "usage": "Text highlight"}},
    ...
  ],
  "typography": {{
    "main_text": "Text chính trên thumbnail",
    "font_family": "Tên font (ví dụ: Montserrat Bold)",
    "font_size": "72-96pt",
    "effects": "Drop shadow, outline, glow..."
  }},
  "layout": {{
    "composition": "Mô tả cách bố trí (ví dụ: Character trái, text phải)",
    "focal_point": "Điểm nhấn chính",
    "rule_of_thirds": "Sử dụng rule of thirds như thế nào"
  }},
  "visual_elements": {{
    "subject": "Nhân vật/Chủ thể chính",
    "props": ["Vật dụng 1", "Vật dụng 2"],
    "background": "Mô tả background",
    "effects": ["Effect 1", "Effect 2"]
  }},
  "style_guide": "Phong cách tổng thể (ví dụ: Bold and dramatic with high contrast...)"
}}
"""

    # Call LLM
    if provider.lower().startswith("gemini"):
        key = api_key or gk
        if not key:
            raise RuntimeError("Chưa cấu hình Google API Key cho Gemini.")
        res = _call_gemini(prompt, key, "gemini-2.5-flash")
    else:
        key = api_key or ok
        if not key:
            raise RuntimeError("Chưa cấu hình OpenAI API Key cho GPT-4 Turbo.")
        res = _call_openai(prompt, key, "gpt-4-turbo")

    return res
