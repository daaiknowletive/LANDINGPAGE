import os
import numpy as np
from PIL import Image

def main():
    assets_dir = r"career-counseling\assets"
    os.makedirs(assets_dir, exist_ok=True)

    master_path = r"career-counseling\Knowletive Logo_S.jpg.jpeg"
    print(f"Loading master logo from {master_path}...")
    im = Image.open(master_path).convert("RGB")
    W, H = im.size

    # Helper function for alpha unmixing
    def unmix_to_rgba(crop_img, t_bg=252.0, t_fg=35.0):
        arr = np.array(crop_img, dtype=np.float32)
        min_ch = np.min(arr, axis=2)
        alpha = (t_bg - min_ch) / (t_bg - t_fg)
        alpha = np.clip(alpha, 0.0, 1.0)
        
        alpha_safe = np.maximum(alpha, 1e-4)[:, :, None]
        unmixed = (arr - 255.0 * (1.0 - alpha_safe)) / alpha_safe
        unmixed = np.clip(unmixed, 0, 255).astype(np.uint8)
        
        rgba = np.dstack((unmixed, (alpha * 255).astype(np.uint8)))
        return Image.fromarray(rgba, "RGBA")

    # 1. Full Vertical Logo Cutout
    # Bounding box on 8333 canvas: x=900..7470, y=1910..6410
    pad = 80
    crop_full = im.crop((max(0, 900 - pad), max(0, 1910 - pad), min(W, 7470 + pad), min(H, 6410 + pad)))
    # Resize to 1200 width for crisp retina display
    target_w = 1200
    target_h = int(target_w * crop_full.height / crop_full.width)
    crop_full_resampled = crop_full.resize((target_w, target_h), Image.Resampling.LANCZOS)
    full_rgba = unmix_to_rgba(crop_full_resampled)
    full_rgba.save(os.path.join(assets_dir, "knowletive-logo-full.png"), optimize=True)
    print("Saved knowletive-logo-full.png")

    # 2. Standalone Icon Cutout (Book & Graduate figure)
    # y=1910..4490, x=2400..5930
    pad_icon = 40
    crop_icon = im.crop((2400 - pad_icon, 1910 - pad_icon, 5930 + pad_icon, 4490 + pad_icon))
    # Resample to 600 width
    icon_w = 600
    icon_h = int(icon_w * crop_icon.height / crop_icon.width)
    crop_icon_resampled = crop_icon.resize((icon_w, icon_h), Image.Resampling.LANCZOS)
    icon_rgba = unmix_to_rgba(crop_icon_resampled)
    icon_rgba.save(os.path.join(assets_dir, "knowletive-icon.png"), optimize=True)
    print("Saved knowletive-icon.png")

    # Favicon version (128x128 square)
    fav_size = max(icon_rgba.width, icon_rgba.height) + 40
    fav_canvas = Image.new("RGBA", (fav_size, fav_size), (0, 0, 0, 0))
    fav_x = (fav_size - icon_rgba.width) // 2
    fav_y = (fav_size - icon_rgba.height) // 2
    fav_canvas.paste(icon_rgba, (fav_x, fav_y), icon_rgba)
    favicon = fav_canvas.resize((64, 64), Image.Resampling.LANCZOS)
    favicon.save(os.path.join(assets_dir, "favicon.png"), optimize=True)
    print("Saved favicon.png")

    # 3. Horizontal Lockup Cutout
    # We combine the icon on the left with the Wordmark + Tagline on the right.
    # First, let's crop wordmark + tagline:
    # Wordmark: y=4750..5750, x=900..7470
    # Tagline: y=5920..6410, x=900..7470
    crop_text = im.crop((900, 4740, 7470, 6410))
    # Text ratio: width = 6570, height = 1670 (ratio ~ 3.93)
    # Let's say text height in horizontal lockup is about equal or slightly smaller than icon height
    h_icon = 400
    w_icon = int(h_icon * (5930 - 2400) / (4490 - 1910)) # ~ 547 px
    icon_scaled = crop_icon.resize((w_icon, h_icon), Image.Resampling.LANCZOS)
    icon_part = unmix_to_rgba(icon_scaled)

    h_text = int(h_icon * 0.82) # ~ 328 px
    w_text = int(h_text * crop_text.width / crop_text.height) # ~ 1289 px
    text_scaled = crop_text.resize((w_text, h_text), Image.Resampling.LANCZOS)
    text_part = unmix_to_rgba(text_scaled)

    gap = 70
    total_w = w_icon + gap + w_text
    total_h = max(h_icon, h_text)

    horiz_canvas = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    # Paste icon vertically centered
    y_icon = (total_h - h_icon) // 2
    horiz_canvas.paste(icon_part, (0, y_icon), icon_part)
    # Paste text vertically centered
    y_text = (total_h - h_text) // 2
    horiz_canvas.paste(text_part, (w_icon + gap, y_text), text_part)

    # Scale down total horizontal lockup to standard crisp retina size: height ~ 90px
    retina_h = 96
    retina_w = int(retina_h * total_w / total_h)
    horiz_final = horiz_canvas.resize((retina_w, retina_h), Image.Resampling.LANCZOS)
    horiz_final.save(os.path.join(assets_dir, "knowletive-logo-horizontal.png"), optimize=True)
    # Also save high-res version
    horiz_canvas.save(os.path.join(assets_dir, "knowletive-logo-horizontal-large.png"), optimize=True)
    print("Saved knowletive-logo-horizontal.png & -large.png")

    # 4. White / Dark-mode Horizontal Lockup (for footer & dark cards)
    # For dark backgrounds: keep the blue and orange icon as-is, make the navy text white!
    text_arr = np.array(text_part)
    # text_arr has shape (H, W, 4)
    # Where alpha > 0, set RGB to (255, 255, 255)
    white_text_arr = text_arr.copy()
    white_text_arr[:, :, 0] = 255
    white_text_arr[:, :, 1] = 255
    white_text_arr[:, :, 2] = 255
    white_text_part = Image.fromarray(white_text_arr, "RGBA")

    horiz_white_canvas = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    horiz_white_canvas.paste(icon_part, (0, y_icon), icon_part)
    horiz_white_canvas.paste(white_text_part, (w_icon + gap, y_text), white_text_part)
    horiz_white_final = horiz_white_canvas.resize((retina_w, retina_h), Image.Resampling.LANCZOS)
    horiz_white_final.save(os.path.join(assets_dir, "knowletive-logo-white-horizontal.png"), optimize=True)
    horiz_white_canvas.save(os.path.join(assets_dir, "knowletive-logo-white-horizontal-large.png"), optimize=True)
    print("Saved knowletive-logo-white-horizontal.png")

    # 5. Full Vertical Logo White (for dark modal / footer)
    full_arr = np.array(full_rgba)
    # In full vertical, icon is at top, text is at bottom.
    # We only want to turn the text white, keeping the icon's orange & blue intact!
    # Icon is in upper part: approx top 55% of height
    split_y = int(full_rgba.height * 0.53)
    full_white_arr = full_arr.copy()
    full_white_arr[split_y:, :, 0] = 255
    full_white_arr[split_y:, :, 1] = 255
    full_white_arr[split_y:, :, 2] = 255
    full_white_part = Image.fromarray(full_white_arr, "RGBA")
    full_white_part.save(os.path.join(assets_dir, "knowletive-logo-white-full.png"), optimize=True)
    print("Saved knowletive-logo-white-full.png")

    print("ALL CUTOUTS SUCCESSFULLY CREATED!")

if __name__ == "__main__":
    main()
