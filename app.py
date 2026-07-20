import os
import tempfile

import streamlit as st
from moviepy import AudioFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont


# =========================================================
# 基本設定
# =========================================================

st.set_page_config(
    page_title="TikTok一枚画像制作エージェント",
    page_icon="🎨",
    layout="centered",
)


TEMPLATE_PRESETS = {
    "一枚図鑑": {
        "description": "雑学・仕事・心理・仕組みなどを、複数の図解で分かりやすく整理します。",
        "layout": "中央メイン＋情報パネル",
        "visual_style": "教育イラスト",
        "density": "高密度",
        "mood": "モダン",
        "color": "明るくカラフル",
        "hero_size": "大きめ",
    },
    "映画ポスター": {
        "description": "格言・感動・物語・世界観を、映画のような強い一枚で表現します。",
        "layout": "中央メイン",
        "visual_style": "実写風",
        "density": "シンプル",
        "mood": "シネマティック",
        "color": "高コントラスト",
        "hero_size": "超大",
    },
    "ニュース・時事": {
        "description": "速報・歴史・ランキング・社会テーマなどを、ニュース特集風に整理します。",
        "layout": "雑誌グリッド",
        "visual_style": "ニュースグラフィック",
        "density": "高密度",
        "mood": "プロフェッショナル",
        "color": "赤・青系",
        "hero_size": "標準",
    },
    "比較図解": {
        "description": "人物・考え方・行動・ビフォーアフターなどの違いを、左右比較で見せます。",
        "layout": "左右比較",
        "visual_style": "フラットデザイン",
        "density": "標準",
        "mood": "分かりやすい",
        "color": "対照的な2色",
        "hero_size": "大きめ",
    },
}


LAYOUT_PROMPTS = {
    "中央メイン＋情報パネル": (
        "Place one large central visual in the upper-middle area and arrange multiple clear "
        "information panels around or below it."
    ),
    "中央メイン": (
        "Use one dominant central subject with a strong focal point and clear depth."
    ),
    "左右比較": (
        "Split the composition clearly into left and right sides for an instant comparison."
    ),
    "上下比較": (
        "Use a clear top-versus-bottom comparison with matching visual scales."
    ),
    "グリッド": (
        "Use a clean modular grid with clearly separated information cards."
    ),
    "雑誌グリッド": (
        "Use a polished editorial magazine grid with headline areas, data panels, and visual summaries."
    ),
    "タイムライン": (
        "Use a clear chronological timeline with arrows, dates, and visual milestones."
    ),
    "放射状": (
        "Arrange the information radially around one central concept."
    ),
    "フロー図": (
        "Use a step-by-step flow diagram with arrows and clear cause-and-effect relationships."
    ),
    "対角線構図": (
        "Use a dynamic diagonal composition with strong depth and energetic visual movement."
    ),
}


VISUAL_STYLE_PROMPTS = {
    "教育イラスト": (
        "Use polished educational illustrations suitable for a high-quality Japanese learning magazine."
    ),
    "実写風": (
        "Use realistic cinematic photography-style visuals with natural human expressions and detailed lighting."
    ),
    "ピクトグラム": (
        "Use simple, bold pictograms with large readable silhouettes, minimal detail, and strong visual clarity."
    ),
    "フラットデザイン": (
        "Use clean flat vector illustrations with simple shapes, clear outlines, and consistent iconography."
    ),
    "漫画風": (
        "Use lively Japanese comic-style illustrations with expressive faces and relatable scenes."
    ),
    "3Dイラスト": (
        "Use polished 3D illustrations with soft depth, smooth materials, and clear lighting."
    ),
    "シンプル線画": (
        "Use refined simple line art with minimal shading and strong readability."
    ),
    "水彩画風": (
        "Use tasteful watercolor-style illustrations while keeping the information easy to read."
    ),
    "ニュースグラフィック": (
        "Use professional broadcast-news graphics with charts, callouts, headline boxes, and clean icons."
    ),
}


DENSITY_PROMPTS = {
    "シンプル": (
        "Use 3 to 4 major information blocks, very short text, large visuals, and generous spacing."
    ),
    "標準": (
        "Use 5 to 6 information blocks with a balanced mix of text, icons, and diagrams."
    ),
    "高密度": (
        "Use 7 to 8 well-organized information blocks with diagrams, comparisons, and concise supporting details. "
        "Keep the poster information-rich but not cluttered."
    ),
}


MOOD_PROMPTS = {
    "モダン": "Use a modern, clean, contemporary editorial atmosphere.",
    "大人っぽい": "Use a mature, sophisticated, calm visual atmosphere for adult viewers.",
    "ポップ": "Use a lively, cheerful, energetic pop design.",
    "かわいい": "Use a friendly, cute, approachable atmosphere without becoming childish.",
    "高級感": "Use a premium, refined, elegant visual atmosphere.",
    "近未来": "Use a futuristic, technology-inspired atmosphere with clean digital elements.",
    "シネマティック": "Use dramatic cinematic lighting, emotional depth, and powerful visual storytelling.",
    "ミニマル": "Use a minimal, uncluttered, highly refined atmosphere.",
    "レトロ": "Use a tasteful retro editorial atmosphere with nostalgic visual cues.",
    "プロフェッショナル": "Use a professional, credible, businesslike editorial atmosphere.",
    "分かりやすい": "Prioritize immediate clarity, simple visual logic, and beginner-friendly presentation.",
}


COLOR_PROMPTS = {
    "明るくカラフル": "Use bright, clean, tasteful colors with strong but balanced accents.",
    "青系": "Use a blue-based palette with white and small accent colors.",
    "暖色系": "Use a warm palette based on orange, yellow, and soft red tones.",
    "赤・青系": "Use a professional red-and-blue news-style palette with white space.",
    "パステル": "Use soft pastel colors with gentle contrast.",
    "ビビッド": "Use vivid colors with strong contrast while preserving readability.",
    "モノクロ": "Use a monochrome palette with one restrained accent color.",
    "高コントラスト": "Use high-contrast cinematic colors with strong highlights and shadows.",
    "ダーク": "Use a dark background with dramatic highlights and luminous accents.",
    "対照的な2色": "Use two clearly contrasting colors to separate the compared sides.",
}


HERO_SIZE_PROMPTS = {
    "小さめ": "Keep the main subject relatively small so supporting information dominates.",
    "標準": "Use a balanced main subject size with equal emphasis on supporting panels.",
    "大きめ": "Make the main subject occupy approximately 30 to 45 percent of the frame.",
    "超大": "Make the main subject occupy approximately 45 to 60 percent of the frame.",
}


TEMPLATE_BASE_PROMPTS = {
    "一枚図鑑": """
Create a professional Japanese vertical infographic poster about '{selected_idea}'.

Target audience: Japanese TikTok viewers.

Create a high-quality educational magazine infographic that makes the topic understandable at a glance.

Include:
- a large Japanese title area
- one clear main visual
- several separated information panels
- a short summary area

Use short, natural Japanese headings and simple Japanese labels.
Avoid long paragraphs.
Do not make the image textless.
Use icons, illustrations, charts, arrows, symbols, comparison boxes, and diagrams where useful.
Keep typography large and readable.
Use clean Japanese editorial design.
Optimize the image for TikTok viewing.
Portrait orientation, height-to-width ratio 4:3.
""",
    "映画ポスター": """
Create a highly detailed Japanese cinematic movie poster inspired by '{selected_idea}'.

Target audience: Japanese TikTok viewers.

Use powerful visual storytelling, one dominant main subject, dramatic lighting, strong shadows, and a clear emotional atmosphere.
The image should feel like a premium live-action film poster.
Use minimal but readable Japanese text only when necessary.
Avoid dense paragraphs and avoid infographic-style clutter.
Leave a clear title area and create a memorable focal point.
No real brand logos.
Optimize the image for TikTok viewing.
Portrait orientation, height-to-width ratio 4:3.
""",
    "ニュース・時事": """
Create a Japanese news-style vertical infographic poster about '{selected_idea}'.

Target audience: Japanese TikTok viewers.

Use modern magazine and broadcast-news editorial design.
Include a strong headline area, 4 to 6 organized information panels, charts, icons, comparison boxes, callouts, and visual explanations.
Use short, natural Japanese headings and concise labels.
Avoid long paragraphs.
Make the information easy to scan at first glance.
Use strong visual hierarchy and a bright, professional layout.
Optimize the image for TikTok viewing.
Portrait orientation, height-to-width ratio 4:3.
""",
    "比較図解": """
Create a professional Japanese vertical comparison infographic about '{selected_idea}'.

Target audience: Japanese TikTok viewers.

Present the topic as a clear visual comparison.
Use a left-versus-right, before-versus-after, good-versus-bad, or two-type structure depending on the topic.
Keep both sides visually balanced and use the same comparison criteria.
Include short Japanese headings, concise labels, icons, arrows, and simple diagrams.
Avoid long paragraphs.
Make the differences understandable within a few seconds.
Use clean, modern editorial design.
Optimize the image for TikTok viewing.
Portrait orientation, height-to-width ratio 4:3.
""",
}


IDEA_DETAIL_PROMPTS = {
    "基本ルール5選": """
Explain five important rules.
Use clearly numbered sections from 1 to 5.
Use icons and diagrams.
Make each rule short, concrete, and easy to understand.
""",
    "みんなが知らない": """
Focus on surprising and little-known facts.
Create curiosity and strong visual impact.
Use mysterious or eye-catching visual elements without reducing clarity.
""",
    "一枚で理解": """
Summarize the whole topic in one image.
Use clear visual hierarchy.
Make the concept understandable at a glance.
""",
    "初心者ガイド": """
Design for complete beginners.
Explain the basic concepts step by step.
Use simple illustrations and beginner-friendly icons.
""",
    "あるある": """
Create funny and relatable scenes.
Use humor and expressive emotions.
Make viewers recognize the situation instantly.
""",
    "歴史": """
Show a historical timeline.
Use chronological flow.
Visualize important events, transitions, and turning points.
""",
    "仕組み": """
Explain how it works.
Use arrows, flow diagrams, and process illustrations.
Visualize relationships between the components.
""",
    "人生が変わる理由": """
Show a clear before-and-after transformation.
Emphasize emotional impact and meaningful change.
""",
    "意外な事実": """
Highlight surprising facts.
Use striking comparisons and a sense of discovery.
""",
    "図鑑": """
Create an encyclopedia-style layout.
Divide information into clearly separated sections with icons and labels.
""",
}


IMPROVEMENT_RULES = {
    "映画ポスター感が弱い": (
        "Add stronger cinematic lighting, dramatic shadows, emotional depth, and a premium movie-poster composition."
    ),
    "インパクトが弱い": (
        "Make the main subject larger and use stronger contrast, bolder hierarchy, and more emotional intensity."
    ),
    "背景がごちゃごちゃ": (
        "Simplify the background, reduce unnecessary objects, and create one clear focal point."
    ),
    "人物が小さい": (
        "Make the main person or subject occupy approximately 40 to 60 percent of the frame."
    ),
    "構図が単調": (
        "Use a more dynamic diagonal, low-angle, or depth-rich composition."
    ),
    "色が地味": (
        "Use more vivid but tasteful colors, stronger highlights, and clearer accent colors."
    ),
    "余白が足りない": (
        "Create clean breathing room and preserve clear space around the title and main visual."
    ),
    "TikTok縦長に合っていない": (
        "Use portrait orientation with a height-to-width ratio of 4:3 and keep important elements within a mobile-safe area."
    ),
    "日本語文字が入ってしまう": (
        "Do not include any Japanese text, letters, logos, or readable words inside the image."
    ),
    "意味が伝わりにくい": (
        "Make the visual metaphor and information flow clearer and understandable at a glance."
    ),
    "文字が少なすぎる": (
        "Add short Japanese headings and concise labels to every major information block."
    ),
    "情報量が少ない": (
        "Increase the number of useful information panels, diagrams, comparisons, and concise supporting facts."
    ),
    "図解が弱い": (
        "Use more arrows, process diagrams, comparison boxes, icons, and visual relationships instead of plain text."
    ),
}


# =========================================================
# 補助関数
# =========================================================

def create_title_overlay(title_text, base_image_path, overlay_path, template_name):
    base = Image.open(base_image_path)
    w, h = base.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    box_w = int(w * 0.86)
    box_h = int(h * 0.18)
    box_x = int((w - box_w) / 2)
    box_y = int(h * 0.42)

    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=35,
        fill=(255, 215, 0, 245),
    )

    font_path = "meiryob.ttc"
    font_big = ImageFont.truetype(font_path, int(w * 0.075))
    font_small = ImageFont.truetype(font_path, int(w * 0.055))

    line1_map = {
        "一枚図鑑": "1枚図鑑",
        "映画ポスター": "AI映画ポスター",
        "ニュース・時事": "AI NEWS",
        "比較図解": "比較図解",
    }

    line1 = line1_map.get(template_name, "TikTok図解")
    line2 = f"【{title_text}】"

    line1_box = draw.textbbox((0, 0), line1, font=font_big)
    line2_box = draw.textbbox((0, 0), line2, font=font_small)

    line1_w = line1_box[2] - line1_box[0]
    line2_w = line2_box[2] - line2_box[0]

    line1_x = int((w - line1_w) / 2)
    line2_x = int((w - line2_w) / 2)

    line1_y = box_y + int(box_h * 0.18)
    line2_y = box_y + int(box_h * 0.55)

    draw.text((line1_x, line1_y), line1, font=font_big, fill=(0, 0, 0, 255))
    draw.text((line2_x, line2_y), line2, font=font_small, fill=(0, 0, 0, 255))

    overlay.save(overlay_path)


def get_idea_detail(selected_idea):
    for keyword, detail in IDEA_DETAIL_PROMPTS.items():
        if keyword in selected_idea:
            return detail
    return ""


def resolve_setting(selected_value, preset_value):
    return preset_value if selected_value == "テンプレート推奨" else selected_value


def build_image_prompt(
    selected_idea,
    template_name,
    generation_mode,
    layout_choice,
    visual_style_choice,
    density_choice,
    mood_choice,
    color_choice,
    hero_size_choice,
    additional_request,
):
    preset = TEMPLATE_PRESETS[template_name]

    if generation_mode == "かんたんモード":
        layout = preset["layout"]
        visual_style = preset["visual_style"]
        density = preset["density"]
        mood = preset["mood"]
        color = preset["color"]
        hero_size = preset["hero_size"]
    else:
        layout = resolve_setting(layout_choice, preset["layout"])
        visual_style = resolve_setting(visual_style_choice, preset["visual_style"])
        density = resolve_setting(density_choice, preset["density"])
        mood = resolve_setting(mood_choice, preset["mood"])
        color = resolve_setting(color_choice, preset["color"])
        hero_size = resolve_setting(hero_size_choice, preset["hero_size"])

    prompt_parts = [
        TEMPLATE_BASE_PROMPTS[template_name].format(selected_idea=selected_idea).strip(),
        get_idea_detail(selected_idea).strip(),
        "Detailed visual direction:",
        f"- Layout: {LAYOUT_PROMPTS[layout]}",
        f"- Visual style: {VISUAL_STYLE_PROMPTS[visual_style]}",
        f"- Information density: {DENSITY_PROMPTS[density]}",
        f"- Mood: {MOOD_PROMPTS[mood]}",
        f"- Color palette: {COLOR_PROMPTS[color]}",
        f"- Main subject size: {HERO_SIZE_PROMPTS[hero_size]}",
        (
            "- Japanese typography: use large, natural, easy-to-read Japanese text. "
            "Keep each heading short and avoid garbled or meaningless characters."
        ),
        (
            "- Mobile readability: emphasize the title, main visual, and section headings so they remain clear on a smartphone screen."
        ),
    ]

    if additional_request.strip():
        prompt_parts.extend(
            [
                "",
                "Additional user request:",
                additional_request.strip(),
            ]
        )

    return "\n\n".join(part for part in prompt_parts if part)


def build_caption(selected_idea, template_name):
    lead_map = {
        "一枚図鑑": "知らないと損する内容を、一枚で分かりやすく解説します。",
        "映画ポスター": "この言葉やテーマを、AI映画ポスター風に表現してみました。",
        "ニュース・時事": "いま知っておきたいポイントを、ニュース特集風に整理しました。",
        "比較図解": "違いを一枚で比較すると、意外なポイントが見えてきます。",
    }

    return f"""【{selected_idea}】

保存してあとで見返そう！

{lead_map[template_name]}

あなたはどう思いましたか？

コメントで教えてください。
"""


def build_hashtags(template_name):
    common = [
        "#AI",
        "#雑学",
        "#学び",
        "#知識",
        "#TikTok教室",
        "#今日の雑学",
        "#おすすめ",
    ]

    template_tags = {
        "一枚図鑑": ["#図鑑", "#一枚図鑑", "#豆知識"],
        "映画ポスター": ["#映画ポスター", "#AIアート", "#名言"],
        "ニュース・時事": ["#ニュース", "#時事ネタ", "#解説"],
        "比較図解": ["#比較", "#図解", "#違い"],
    }

    return "\n".join(common + template_tags[template_name])


# =========================================================
# UI
# =========================================================

st.title("TikTok一枚画像制作エージェント")

theme = st.text_input(
    "投稿テーマを入力してください",
    "AI時代の仕事",
)

template_name = st.selectbox(
    "テンプレートを選択してください",
    list(TEMPLATE_PRESETS.keys()),
)

st.caption(TEMPLATE_PRESETS[template_name]["description"])

ideas = [
    f"{theme}の基本ルール5選",
    f"みんなが知らない{theme}",
    f"{theme}を一枚で理解",
    f"{theme}初心者ガイド",
    f"{theme}あるある",
    f"{theme}の歴史",
    f"{theme}の仕組み",
    f"{theme}で人生が変わる理由",
    f"{theme}の意外な事実",
    f"{theme}図鑑",
]

if st.button("ネタ候補を作る"):
    st.success("ネタ候補を作成しました。下の一覧から選んでください。")

selected_idea = st.selectbox(
    "画像化したいネタを選択してください",
    ideas,
)

st.write("選択されたネタ")
st.success(selected_idea)

st.divider()

generation_mode = st.radio(
    "画像生成モード",
    ["かんたんモード", "こだわりモード"],
    horizontal=True,
    help=(
        "かんたんモードはテンプレートの推奨設定を自動使用します。"
        "こだわりモードでは構図や絵のタッチなどを個別に変更できます。"
    ),
)

layout_choice = "テンプレート推奨"
visual_style_choice = "テンプレート推奨"
density_choice = "テンプレート推奨"
mood_choice = "テンプレート推奨"
color_choice = "テンプレート推奨"
hero_size_choice = "テンプレート推奨"
additional_request = ""

if generation_mode == "かんたんモード":
    preset = TEMPLATE_PRESETS[template_name]
    st.info(
        "テンプレートの推奨設定を自動で使います。\n\n"
        f"- 構図：{preset['layout']}\n"
        f"- 絵のタッチ：{preset['visual_style']}\n"
        f"- 情報量：{preset['density']}\n"
        f"- 雰囲気：{preset['mood']}\n"
        f"- 配色：{preset['color']}\n"
        f"- 主役サイズ：{preset['hero_size']}"
    )

else:
    st.subheader("こだわり設定")

    layout_choice = st.selectbox(
        "構図",
        ["テンプレート推奨"] + list(LAYOUT_PROMPTS.keys()),
    )

    visual_style_choice = st.selectbox(
        "絵のタッチ",
        ["テンプレート推奨"] + list(VISUAL_STYLE_PROMPTS.keys()),
    )

    density_choice = st.selectbox(
        "情報量",
        ["テンプレート推奨", "シンプル", "標準", "高密度"],
        help="文字量・図解量・情報ブロック数をまとめて調整します。",
    )

    mood_choice = st.selectbox(
        "雰囲気",
        ["テンプレート推奨"] + list(MOOD_PROMPTS.keys()),
    )

    color_choice = st.selectbox(
        "配色",
        ["テンプレート推奨"] + list(COLOR_PROMPTS.keys()),
    )

    hero_size_choice = st.selectbox(
        "主役サイズ",
        ["テンプレート推奨", "小さめ", "標準", "大きめ", "超大"],
    )

    additional_request = st.text_area(
        "追加要望（任意）",
        placeholder=(
            "例：文字をもっと大きくしてください。\n"
            "中央の人物を笑顔にしてください。\n"
            "黄色をアクセントにしてください。"
        ),
        height=140,
    )

prompt = build_image_prompt(
    selected_idea=selected_idea,
    template_name=template_name,
    generation_mode=generation_mode,
    layout_choice=layout_choice,
    visual_style_choice=visual_style_choice,
    density_choice=density_choice,
    mood_choice=mood_choice,
    color_choice=color_choice,
    hero_size_choice=hero_size_choice,
    additional_request=additional_request,
)

st.subheader("画像生成プロンプト")
st.code(prompt, language=None)

st.subheader("画像が気に入らない場合")

problems = st.multiselect(
    "不満点を選んでください",
    list(IMPROVEMENT_RULES.keys()),
)

if st.button("修正版プロンプトを作る"):
    if not problems:
        st.warning("不満点を1つ以上選択してください。")
    else:
        improvement_text = "\n".join(
            f"- {IMPROVEMENT_RULES[problem]}" for problem in problems
        )
        improved_prompt = (
            f"{prompt}\n\n"
            "Additional improvement instructions:\n"
            f"{improvement_text}"
        )

        st.subheader("修正版プロンプト")
        st.code(improved_prompt, language=None)

st.subheader("投稿文")

caption = build_caption(selected_idea, template_name)

st.text_area(
    "投稿文",
    caption,
    height=200,
)

st.subheader("ハッシュタグ")

hashtags = build_hashtags(template_name)
st.code(hashtags, language=None)

st.subheader("完成画像アップロード")

uploaded_file = st.file_uploader(
    "ChatGPTで生成した画像をアップロードしてください",
    type=["png", "jpg", "jpeg"],
)

bgm_options = {
    "BGMなし": None,
    "モチベーション系": "assets/bgm/motivational.mp3",
    "学習・図鑑系": "assets/bgm/educational.mp3",
    "感動・前向き系": "assets/bgm/inspiring.mp3",
    "バトル・迫力系": "assets/bgm/battle.mp3",
}

selected_bgm = st.selectbox(
    "BGMを選択してください",
    list(bgm_options.keys()),
)

if uploaded_file is not None:
    st.image(
        uploaded_file,
        caption="アップロードされた画像",
        use_container_width=True,
    )

    st.success("画像を読み込みました。次はこの画像を動画化できます。")

    video_title = st.text_input(
        "動画タイトル",
        selected_idea,
    )

    if st.button("タイトル付き動画を作る"):
        temp_dir = tempfile.gettempdir()

        original_extension = os.path.splitext(uploaded_file.name)[1] or ".png"
        image_path = os.path.join(temp_dir, f"uploaded_tiktok_image{original_extension}")

        with open(image_path, "wb") as file:
            file.write(uploaded_file.getbuffer())

        image_clip = ImageClip(image_path).with_duration(30)

        overlay_path = os.path.join(temp_dir, "title_overlay.png")

        create_title_overlay(
            video_title,
            image_path,
            overlay_path,
            template_name,
        )

        title_clip = ImageClip(overlay_path).with_duration(5)

        final_video = CompositeVideoClip([image_clip, title_clip])

        output_path = os.path.join(temp_dir, "tiktok_output.mp4")
        bgm_path = bgm_options[selected_bgm]
        audio_clip = None

        try:
            if bgm_path is not None:
                if not os.path.exists(bgm_path):
                    st.warning(
                        f"選択したBGMファイルが見つからないため、BGMなしで動画を作成します：{bgm_path}"
                    )
                else:
                    audio_source = AudioFileClip(bgm_path)
                    audio_duration = min(30, audio_source.duration)
                    audio_clip = (
                        audio_source
                        .subclipped(0, audio_duration)
                        .with_volume_scaled(0.25)
                    )
                    final_video = final_video.with_audio(audio_clip)

            with st.spinner("動画を作成しています。しばらくお待ちください。"):
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    ffmpeg_params=["-pix_fmt", "yuv420p"],
                    logger=None,
                )

            st.success("動画作成完了！")

            with open(output_path, "rb") as file:
                st.download_button(
                    "動画をダウンロード",
                    file,
                    file_name="tiktok_output.mp4",
                    mime="video/mp4",
                )

        except Exception as error:
            st.error(f"動画作成中にエラーが発生しました：{error}")

        finally:
            final_video.close()
            image_clip.close()
            title_clip.close()

            if audio_clip is not None:
                audio_clip.close()
