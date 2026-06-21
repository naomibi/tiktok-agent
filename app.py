import streamlit as st
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip
import tempfile
import os
from PIL import Image, ImageDraw, ImageFont

def create_title_overlay(title_text, base_image_path, overlay_path):
    base = Image.open(base_image_path)
    w, h = base.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 黄色の角丸ボックス
    box_w = int(w * 0.86)
    box_h = int(h * 0.18)
    box_x = int((w - box_w) / 2)
    box_y = int(h * 0.42)

    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=35,
        fill=(255, 215, 0, 245)
    )

    # フォント設定
    font_path = "C:/Windows/Fonts/meiryob.ttc"

    font_big = ImageFont.truetype(font_path, int(w * 0.075))
    font_small = ImageFont.truetype(font_path, int(w * 0.055))

    line1 = "1枚図鑑"
    line2 = f"【{title_text}】"

    # 文字位置計算
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

st.title("TikTok一枚画像制作エージェント")

theme = st.text_input(
    "投稿テーマを入力してください",
    "AI時代の仕事"
)

genre = st.selectbox(
    "ジャンルを選択してください",
    ["一枚画像図鑑", "格言映画ポスター", "サッカールール", "時事ネタ"]
)

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
    f"{theme}図鑑"
]

if st.button("ネタ候補を作る"):
    st.subheader("ネタ候補を作成しました")

selected_idea = st.selectbox(
    "画像化したいネタを選択してください",
    ideas
)

st.write("選択されたネタ")
st.success(selected_idea)

idea_detail = ""

if "基本ルール5選" in selected_idea:
    idea_detail = """
Explain five important rules.
Use numbered sections.
Use icons and diagrams.
Make it educational and easy to understand.
"""

elif "みんなが知らない" in selected_idea:
    idea_detail = """
Focus on surprising and little-known facts.
Create curiosity and strong visual impact.
Use mysterious and eye-catching elements.
"""

elif "一枚で理解" in selected_idea:
    idea_detail = """
Summarize the whole topic in one image.
Use visual hierarchy and infographic layout.
Make the concept understandable at a glance.
"""

elif "初心者ガイド" in selected_idea:
    idea_detail = """
Design for complete beginners.
Explain basic concepts step by step.
Use simple illustrations and beginner-friendly icons.
"""

elif "あるある" in selected_idea:
    idea_detail = """
Create funny and relatable scenes.
Use humor and emotional expressions.
Make viewers smile instantly.
"""

elif "歴史" in selected_idea:
    idea_detail = """
Show historical timeline.
Use chronological flow.
Visualize important events and transitions.
"""

elif "仕組み" in selected_idea:
    idea_detail = """
Explain how it works.
Use arrows, flow diagrams and process illustrations.
Visualize relationships between components.
"""

elif "人生が変わる理由" in selected_idea:
    idea_detail = """
Show before-and-after comparison.
Emphasize transformation and emotional impact.
Use dramatic visual storytelling.
"""

elif "意外な事実" in selected_idea:
    idea_detail = """
Highlight surprising facts.
Use shocking comparisons and strong visual contrast.
Create a sense of discovery.
"""

elif "図鑑" in selected_idea:
    idea_detail = """
Create encyclopedia style layout.
Divide information into several clearly separated sections.
Use icons and labels.
"""

if genre == "一枚画像図鑑":
    prompt = f"""
Create a professional Japanese vertical infographic poster about '{selected_idea}'.

Target audience: Japanese TikTok viewers.

The image should look like a high-quality educational magazine infographic.

Include short Japanese headings and simple Japanese labels.

Use readable Japanese text, but avoid long paragraphs.

Do not make it textless.

Do not leave the poster too empty.

Use 5 to 8 information blocks.

Each block should contain:
- a short Japanese heading
- a simple icon or illustration
- a very short explanation

Use icons, illustrations, charts, arrows, symbols, comparison boxes and diagrams.

Make the structure clear:
- large title area
- main visual explanation
- several small information panels
- summary area

Use clean Japanese editorial design.

Bright, clean, colorful, modern, easy to read.

High information density, but not cluttered.

Strong visual impact.

TikTok optimized.

Vertical composition.

4:3 aspect ratio.

{idea_detail}
"""

elif genre == "サッカールール":
    prompt = f"""
Create a professional Japanese soccer rule infographic poster about '{selected_idea}'.

Target audience: Japanese beginners and children.

Include short Japanese headings and simple Japanese labels.

Use readable Japanese text, but avoid long paragraphs.

Use a soccer field diagram, arrows, player icons, zones, lines and movement paths.

Explain the rule visually and clearly.

Use 4 to 6 explanation panels.

Each panel should contain:
- a short Japanese heading
- a simple diagram
- a short explanation

No real players.

No real team logos.

Modern sports design.

Bright, clean, educational, easy to understand.

High information density, but not cluttered.

Strong visual impact.

TikTok optimized.

Vertical composition.

4:3 aspect ratio.

{idea_detail}
"""

else:
    prompt = f"""
Create a Japanese news-style infographic poster about '{selected_idea}'.

Target audience: Japanese TikTok viewers.

Use modern magazine editorial design.

Use charts, icons, comparison boxes and visual explanations.

Use 4 to 6 information panels.

Include short Japanese headings.

Avoid long paragraphs.

Strong visual hierarchy.

Bright and professional design.

High information density.

Easy to understand at first glance.

Strong visual impact.

Use clean infographic layout.

Vertical composition.

4:3 aspect ratio.

{idea_detail}
"""

st.subheader("画像生成プロンプト")
st.code(prompt)
st.subheader("画像が気に入らない場合")

problems = st.multiselect(
    "不満点を選んでください",
    [
        "映画ポスター感が弱い",
        "インパクトが弱い",
        "背景がごちゃごちゃ",
        "人物が小さい",
        "構図が単調",
        "色が地味",
        "余白が足りない",
        "TikTok縦長に合っていない",
        "日本語文字が入ってしまう",
        "意味が伝わりにくい",
        "文字が少なすぎる",
        "情報量が少ない",
        "図解が弱い"
    ]
)

improvement_rules = {
    "映画ポスター感が弱い": "Add dramatic cinematic lighting, strong contrast, epic movie poster composition, dramatic shadows.",
    "インパクトが弱い": "Make the main subject larger, use bold composition, stronger visual contrast, and more emotional intensity.",
    "背景がごちゃごちゃ": "Simplify the background, reduce unnecessary objects, create a clear focal point.",
    "人物が小さい": "Make the main character occupy 40 to 60 percent of the frame.",
    "構図が単調": "Use a dynamic low-angle or diagonal composition with strong depth.",
    "色が地味": "Use more vivid but tasteful colors, stronger highlights, and cinematic color grading.",
    "余白が足りない": "Leave clear empty space at the top for title overlay.",
    "TikTok縦長に合っていない": "Optimize for a vertical TikTok composition, 9:16 aspect ratio.",
    "日本語文字が入ってしまう": "Do not include any Japanese text, letters, logos, or readable words inside the image.",
    "意味が伝わりにくい": "Make the visual metaphor clearer and easier to understand at a glance."
}

if st.button("修正版プロンプトを作る"):
    improved_prompt = prompt + "\n\nAdditional improvement instructions:\n"

    for problem in problems:
        improved_prompt += f"- {improvement_rules[problem]}\n"

    st.subheader("修正版プロンプト")
    st.code(improved_prompt)
    st.subheader("TikTok投稿文")

caption = f"""
【{selected_idea}】

保存してあとで見返そう！

知らないと損する
「{selected_idea}」を一枚で解説します。

あなたはいくつ知っていましたか？

コメントで教えてください。

"""

st.text_area(
    "投稿文",
    caption,
    height=200
)

hashtags = """
#AI
#雑学
#図鑑
#学び
#知識
#豆知識
#tiktok教室
#今日の雑学
#一枚図鑑
#おすすめ
"""

st.subheader("ハッシュタグ")

st.code(hashtags)
st.subheader("完成画像アップロード")

uploaded_file = st.file_uploader(
    "ChatGPTで生成した画像をアップロードしてください",
    type=["png", "jpg", "jpeg"]
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
    list(bgm_options.keys())
)

if uploaded_file is not None:
    st.image(
        uploaded_file,
        caption="アップロードされた画像",
        use_container_width=True
    )

    st.success("画像を読み込みました。次はこの画像を動画化できます。")

    video_title = st.text_input(
        "動画タイトル",
        selected_idea
    )
    if st.button("タイトル付き動画を作る"):

        # 一時フォルダ取得
        temp_dir = tempfile.gettempdir()

        # 画像を一時保存
        image_path = os.path.join(
            temp_dir,
            uploaded_file.name
        )

        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 画像クリップ作成（30秒表示）
        image_clip = (
            ImageClip(image_path)
            .with_duration(30)
        )

        # タイトル画像を作成
        overlay_path = os.path.join(
            temp_dir,
            "title_overlay.png"
        )

        create_title_overlay(
            video_title,
            image_path,
            overlay_path
        )

        # 黄色タイトルを5秒だけ表示
        title_clip = (
            ImageClip(overlay_path)
            .with_duration(5)
        )

        # 合成
        final_video = CompositeVideoClip(
            [image_clip, title_clip]
        )

        # 出力先
        output_path = os.path.join(
            temp_dir,
            "tiktok_output.mp4"
        )

        bgm_path = bgm_options[selected_bgm]

        if bgm_path is not None and os.path.exists(bgm_path):
            audio_clip = (
                AudioFileClip(bgm_path)
                .subclipped(0, 30)
                .with_volume_scaled(0.25)
            )

            final_video = final_video.with_audio(audio_clip)

        # 動画出力
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            ffmpeg_params=["-pix_fmt", "yuv420p"]
        )

        st.success("動画作成完了！")

        with open(output_path, "rb") as file:
            st.download_button(
                "動画をダウンロード",
                file,
                file_name="tiktok_output.mp4"
            )