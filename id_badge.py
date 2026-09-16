import datetime
import os
import base64
import calendar
from PIL import Image

def calculate_age():
    # User's birthdate: December 12, 2004
    birthdate = datetime.datetime(2021, 6, 1)
    now = datetime.datetime.now()
    
    years = now.year - birthdate.year
    if (now.month, now.day) < (birthdate.month, birthdate.day):
        years -= 1
    
    # Calculate last birthday date
    last_birthday_year = now.year if (now.month, now.day) >= (birthdate.month, birthdate.day) else now.year - 1
    last_birthday = datetime.datetime(last_birthday_year, birthdate.month, birthdate.day)
    
    # Calculate calendar months since last birthday
    temp_date = last_birthday
    months = 0
    while True:
        next_month_year = temp_date.year + (temp_date.month // 12)
        next_month = (temp_date.month % 12) + 1
        
        # Handle calendar month-end variations (e.g., Feb 30th)
        last_day_of_next_month = calendar.monthrange(next_month_year, next_month)[1]
        target_day = min(birthdate.day, last_day_of_next_month)
        next_date = datetime.datetime(next_month_year, next_month, target_day)
        
        if next_date > now:
            break
        temp_date = next_date
        months += 1
        
    days = (now - temp_date).days
    return f"{years} yr(s), {months} mo(s), {days} day(s)"

def encode_image_to_base64(image_path, crop_aspect=1.25):
    if not os.path.exists(image_path):
        return None

    try:
        img = Image.open(image_path)
        img = img.convert("RGB")

        w, h = img.size
        # Crop to match the badge's image slot aspect ratio
        if w / h > crop_aspect:
            new_w = int(h * crop_aspect)
            left = (w - new_w) / 2
            top = 0
            img = img.crop((left, top, left + new_w, h))
        else:
            new_h = int(w / crop_aspect)
            left = 0
            top = (h - new_h) / 2
            img = img.crop((left, top, w, top + new_h))

        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print("Error encoding image:", e)
        return None

def justify_dots_and_val(key_str, value_str, total_line_len):
    """
    Returns the key markup, dot leaders, and value formatted to make the section exactly total_line_len long.
    This guarantees right-alignment for values.
    """
    if isinstance(value_str, int):
        value_str = f"{'{:,}'.format(value_str)}"
    value_str = str(value_str)
    
    # Handle composite keys with dots
    if "." in key_str:
        parts = key_str.split(".")
        key_markup = f'<tspan class="key">{parts[0]}</tspan>.<tspan class="key">{parts[1]}</tspan>:'
    else:
        key_markup = f'<tspan class="key">{key_str}</tspan>:'
    
    # prefix length is len(key_str) + 1 (for ":")
    prefix_len = len(key_str) + 1
    dots_count = total_line_len - prefix_len - len(value_str)
    
    if dots_count <= 2:
        dot_map = {0: '', 1: ' ', 2: '. '}
        dots_str = dot_map[max(0, dots_count)]
    else:
        dots_str = ' ' + ('.' * (dots_count - 2)) + ' '
        
    return f'{key_markup}<tspan class="cc">{dots_str}</tspan><tspan class="value">{value_str}</tspan>'

def generate_svg(filename, is_dark_mode, uptime):
    # Left column image slot geometry (matches previous ASCII art bounding box)
    img_x, img_y, img_w, img_h = 15, 15, 355, 385
    profile_image = encode_image_to_base64("profile.png", crop_aspect=img_w / img_h)

    # Theme Specific Colors
    if is_dark_mode:
        bg = "#161b22"
        border = "#30363d"
        ascii_fallback = "#c9d1d9" # Exact color of inspiration ASCII
        user = "#58a6ff"
        host = "#3fb950"
        key = "#ffa657"
        val = "#a5d6ff"
        separator = "#616e7f"
    else:
        bg = "#f6f8fa"
        border = "#d0d7de"
        ascii_fallback = "#24292f" # Exact color of inspiration ASCII
        user = "#0969da"
        host = "#1a7f37"
        key = "#953800"
        val = "#0a3069"
        separator = "#c2cfde"

    svg_parts = []
    svg_parts.append('<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="415px" font-size="16px">')
    
    svg_parts.append(f'''  <defs>
    <style>
      @font-face {{
        src: local('Consolas'), local('Consolas Bold');
        font-family: 'ConsolasFallback';
        font-display: swap;
        -webkit-size-adjust: 109%;
        size-adjust: 109%;
      }}
      .key {{ fill: {key}; }}
      .value {{ fill: {val}; }}
      .cc {{ fill: {separator}; }}
      text, tspan {{
        white-space: pre;
      }}
    </style>
  </defs>''')

    # Card Container
    svg_parts.append(f'  <rect width="985px" height="415px" fill="{bg}" rx="15" stroke="{border}" stroke-width="1"/>')
    
    # Left Column (Profile Image)
    if profile_image:
        svg_parts.append(
            f'  <clipPath id="profileClip"><rect x="{img_x}" y="{img_y}" width="{img_w}" height="{img_h}" rx="10"/></clipPath>'
        )
        svg_parts.append(
            f'  <image x="{img_x}" y="{img_y}" width="{img_w}" height="{img_h}" '
            f'href="{profile_image}" clip-path="url(#profileClip)" preserveAspectRatio="xMidYMid slice"/>'
        )

    # Right Column (Stats)
    svg_parts.append(f'  <text x="390" y="30" fill="{ascii_fallback}">')
    svg_parts.append(f'    <tspan x="390" y="30"><tspan class="user">YasminCastro</tspan></tspan> -———————————————————————————————————————————-—-')
    
    # Empty dot leader line at y=50 for top-spacing balance
    svg_parts.append(f'    <tspan x="390" y="50" class="cc">. </tspan>')
    
    svg_parts.append(f'    <tspan x="390" y="70" class="cc">. </tspan>{justify_dots_and_val("Uptime", uptime, 58)}')
    svg_parts.append(f'    <tspan x="390" y="90" class="cc">. </tspan>{justify_dots_and_val("Host", "yascastro.com.br", 58)}')
    svg_parts.append(f'    <tspan x="390" y="110" class="cc">. </tspan>{justify_dots_and_val("Kernel", "Fullstack Developer", 58)}')
    svg_parts.append(f'    <tspan x="390" y="130" class="cc">. </tspan>{justify_dots_and_val("IDE", "VS Code", 58)}')
    svg_parts.append(f'    <tspan x="390" y="150" class="cc">. </tspan>')

    svg_parts.append(f'    <tspan x="390" y="170" class="cc">. </tspan>{justify_dots_and_val("Languages.Programming", "TypeScript, Python, SQL", 58)}')
    svg_parts.append(f'    <tspan x="390" y="190" class="cc">. </tspan>{justify_dots_and_val("Languages.Computer", "HTML, CSS, JSON, GraphQL", 58)}')
    svg_parts.append(f'    <tspan x="390" y="210" class="cc">. </tspan>{justify_dots_and_val("Languages.Frameworks", "React, Angular, Next.js, Express.js", 58)}')
    svg_parts.append(f'    <tspan x="390" y="230" class="cc">. </tspan>{justify_dots_and_val("Languages.Real", "Portuguese, English", 58)}')
    svg_parts.append(f'    <tspan x="390" y="250" class="cc">. </tspan>')

    svg_parts.append(f'    <tspan x="390" y="270" class="cc">. </tspan>{justify_dots_and_val("Hobbies.Software", "Problem Solving, System Design", 58)}')
    svg_parts.append(f'    <tspan x="390" y="290" class="cc">. </tspan>{justify_dots_and_val("Hobbies.Real", "3D Printing, Movies, Music", 58)}')
    svg_parts.append(f'    <tspan x="390" y="310" class="cc">. </tspan>')

    # Contact Details
    svg_parts.append(f'    <tspan x="390" y="330">- Contact</tspan> -——————————————————————————————————————————————-—-')
    svg_parts.append(f'    <tspan x="390" y="350" class="cc">. </tspan>{justify_dots_and_val("Email", "yasminsdcastro@gmail.com", 58)}')
    svg_parts.append(f'    <tspan x="390" y="370" class="cc">. </tspan>{justify_dots_and_val("LinkedIn", "YasminCastro", 58)}')
    svg_parts.append(f'    <tspan x="390" y="390" class="cc">. </tspan>{justify_dots_and_val("Website", "yascastro.com.br", 58)}')

    svg_parts.append('  </text>')

    svg_parts.append('</svg>')

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))

def main():
    uptime = calculate_age()
    generate_svg("id_badge_light.svg", False, uptime)
    generate_svg("id_badge_dark.svg", True, uptime)

if __name__ == "__main__":
    main()
