import cv2
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# SALT-AND-PEPPER NOISE REMOVAL USING MEDIAN FILTER
# ============================================================

# ---------- 1. LOAD INPUT IMAGE ----------
image = cv2.imread("input.png", cv2.IMREAD_GRAYSCALE)

if image is None:
    print("ERROR: input.png not found!")
    print("Keep input.png in the same folder as this Python file.")
    exit()

print("=" * 60)
print("   SALT-AND-PEPPER NOISE REMOVAL USING MEDIAN FILTER")
print("=" * 60)

print("\nOriginal Image Loaded Successfully")
print("Image Size:", image.shape)


# ---------- 2. ADD SALT-AND-PEPPER NOISE ----------
def add_salt_pepper_noise(image, noise_amount=0.05):

    noisy = image.copy()

    total_pixels = image.size
    noisy_pixels = int(total_pixels * noise_amount)

    # Fixed seed for reproducible demo
    np.random.seed(42)

    rows = np.random.randint(0, image.shape[0], noisy_pixels)
    cols = np.random.randint(0, image.shape[1], noisy_pixels)

    half = noisy_pixels // 2

    # Pepper noise = black pixels
    noisy[rows[:half], cols[:half]] = 0

    # Salt noise = white pixels
    noisy[rows[half:], cols[half:]] = 255

    return noisy


noise_density = 0.05
noisy_image = add_salt_pepper_noise(image, noise_density)


# ---------- 3. APPLY MEDIAN FILTER ----------
median_3 = cv2.medianBlur(noisy_image, 3)
median_5 = cv2.medianBlur(noisy_image, 5)
median_7 = cv2.medianBlur(noisy_image, 7)


# ---------- 4. MSE CALCULATION ----------
def calculate_mse(original, processed):

    original = original.astype(np.float64)
    processed = processed.astype(np.float64)

    mse = np.mean((original - processed) ** 2)

    return mse


# ---------- 5. PSNR CALCULATION ----------
def calculate_psnr(original, processed):

    mse = calculate_mse(original, processed)

    if mse == 0:
        return float("inf")

    max_pixel = 255.0

    psnr = 10 * np.log10((max_pixel ** 2) / mse)

    return psnr


# ---------- 6. CALCULATE RESULTS ----------
mse_3 = calculate_mse(image, median_3)
psnr_3 = calculate_psnr(image, median_3)

mse_5 = calculate_mse(image, median_5)
psnr_5 = calculate_psnr(image, median_5)

mse_7 = calculate_mse(image, median_7)
psnr_7 = calculate_psnr(image, median_7)


# ---------- 7. DISPLAY RESULTS IN TERMINAL ----------
print("\n" + "=" * 60)
print("                 PERFORMANCE RESULTS")
print("=" * 60)

print("\nFilter        MSE                 PSNR (dB)")
print("-" * 60)

print(f"3 x 3       {mse_3:<18.4f} {psnr_3:.2f} dB")
print(f"5 x 5       {mse_5:<18.4f} {psnr_5:.2f} dB")
print(f"7 x 7       {mse_7:<18.4f} {psnr_7:.2f} dB")

print("-" * 60)


# ---------- 8. FIND BEST PSNR ----------
psnr_values = {
    "3 x 3": psnr_3,
    "5 x 5": psnr_5,
    "7 x 7": psnr_7
}

best_filter = max(psnr_values, key=psnr_values.get)

print("\nBest PSNR:", best_filter)
print("Higher PSNR indicates better similarity to the original image.")


# ---------- 9. PROFESSIONAL DISPLAY ----------
fig = plt.figure(figsize=(16, 10))

fig.suptitle(
    "Salt-and-Pepper Noise Removal using Median Filter",
    fontsize=18,
    fontweight="bold"
)


# Original
ax1 = plt.subplot(2, 4, 1)
ax1.imshow(image, cmap="gray")
ax1.set_title("Original Image", fontsize=12, fontweight="bold")
ax1.axis("off")


# Noisy
ax2 = plt.subplot(2, 4, 2)
ax2.imshow(noisy_image, cmap="gray")
ax2.set_title(
    "Salt & Pepper Noise\n(5% Noise)",
    fontsize=12,
    fontweight="bold"
)
ax2.axis("off")


# 3x3
ax3 = plt.subplot(2, 4, 3)
ax3.imshow(median_3, cmap="gray")
ax3.set_title(
    f"3×3 Median Filter\nPSNR: {psnr_3:.2f} dB",
    fontsize=12,
    fontweight="bold"
)
ax3.axis("off")


# 5x5
ax4 = plt.subplot(2, 4, 4)
ax4.imshow(median_5, cmap="gray")
ax4.set_title(
    f"5×5 Median Filter\nPSNR: {psnr_5:.2f} dB",
    fontsize=12,
    fontweight="bold"
)
ax4.axis("off")


# 7x7
ax5 = plt.subplot(2, 4, 5)
ax5.imshow(median_7, cmap="gray")
ax5.set_title(
    f"7×7 Median Filter\nPSNR: {psnr_7:.2f} dB",
    fontsize=12,
    fontweight="bold"
)
ax5.axis("off")


# ---------- HISTOGRAM ----------
ax6 = plt.subplot(2, 4, 6)

ax6.hist(
    noisy_image.ravel(),
    bins=256,
    alpha=0.6,
    label="Noisy"
)

ax6.hist(
    median_5.ravel(),
    bins=256,
    alpha=0.6,
    label="Filtered (5×5)"
)

ax6.set_title(
    "Histogram Comparison",
    fontsize=12,
    fontweight="bold"
)

ax6.set_xlabel("Pixel Intensity")
ax6.set_ylabel("Frequency")
ax6.legend()


# ---------- METRICS TABLE ----------
ax7 = plt.subplot(2, 4, 7)
ax7.axis("off")

table_data = [
    ["Filter", "MSE", "PSNR"],
    ["3×3", f"{mse_3:.2f}", f"{psnr_3:.2f} dB"],
    ["5×5", f"{mse_5:.2f}", f"{psnr_5:.2f} dB"],
    ["7×7", f"{mse_7:.2f}", f"{psnr_7:.2f} dB"]
]

table = ax7.table(
    cellText=table_data,
    cellLoc="center",
    loc="center",
    colWidths=[0.30, 0.35, 0.40]
)

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 2.0)

ax7.set_title(
    "Performance Comparison",
    fontsize=12,
    fontweight="bold",
    pad=15
)


# ---------- PROJECT FLOW ----------
ax8 = plt.subplot(2, 4, 8)
ax8.axis("off")

flow_text = (
    "PROCESS FLOW\n\n"
    "Original Image\n"
    "       ↓\n"
    "Add 5% Noise\n"
    "       ↓\n"
    "Median Filtering\n"
    "       ↓\n"
    "MSE + PSNR\n"
    "       ↓\n"
    "Quality Comparison"
)

ax8.text(
    0.5,
    0.5,
    flow_text,
    ha="center",
    va="center",
    fontsize=12,
    fontweight="bold"
)

ax8.set_title(
    "Processing Pipeline",
    fontsize=12,
    fontweight="bold"
)


plt.tight_layout(rect=[0, 0, 1, 0.94])

plt.show()