
from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import io
import math
import heapq
from collections import Counter
from PIL import Image

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

ALLOWED = {"png", "jpg", "jpeg", "bmp", "webp"}

def img_to_data_url(img, quality=92):
    if img is None:
        return None
    if len(img.shape) == 2:
        ok, buf = cv2.imencode(".png", img)
    else:
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        return None
    return "data:image/" + ("png" if len(img.shape) == 2 else "jpeg") + ";base64," + base64.b64encode(buf).decode()

def read_upload(file):
    if not file or not file.filename:
        raise ValueError("Please select an image.")
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED:
        raise ValueError("Supported formats: PNG, JPG, JPEG, BMP, WEBP.")
    data = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("The image could not be decoded.")
    return img

def gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img

def stats(img):
    g = gray(img)
    return {
        "width": int(img.shape[1]),
        "height": int(img.shape[0]),
        "channels": int(1 if len(img.shape) == 2 else img.shape[2]),
        "min": int(g.min()),
        "max": int(g.max()),
        "mean": round(float(g.mean()), 2),
    }

def huffman_stats(img):
    data = gray(img).flatten().tolist()
    freq = Counter(data)
    heap = [[count, [symbol, ""]] for symbol, count in freq.items()]
    heapq.heapify(heap)
    if len(heap) == 1:
        codes = {heap[0][1][0]: "0"}
    else:
        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            for pair in lo[1:]:
                pair[1] = "0" + pair[1]
            for pair in hi[1:]:
                pair[1] = "1" + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0], *lo[1:], *hi[1:]])
        codes = {symbol: code for _, *pairs in heap for symbol, code in pairs}
    bits = sum(freq[s] * len(codes[s]) for s in freq)
    original_bits = len(data) * 8
    ratio = original_bits / bits if bits else 0
    return {
        "unique_symbols": len(freq),
        "original_bits": original_bits,
        "encoded_bits": bits,
        "compression_ratio": round(ratio, 3),
        "space_saving": round((1 - bits / original_bits) * 100, 2) if original_bits else 0,
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/process", methods=["POST"])
def process():
    try:
        practical = request.form.get("practical", "1")
        operation = request.form.get("operation", "")
        img = read_upload(request.files.get("image"))
        result = img.copy()
        metric = {}
        note = ""
        title = operation

        # 1. Representation + arithmetic + bitwise
        if practical == "1":
            if operation == "grayscale":
                result = gray(img)
                title = "RGB → Grayscale"
                note = "The three RGB/BGR channels are converted into one intensity channel."
            elif operation == "rgb":
                result = img
                title = "RGB Image"
                note = "OpenCV loads color images in BGR order; the browser displays the result normally."
            elif operation == "add":
                value = int(request.form.get("value", 40))
                result = cv2.add(img, np.full_like(img, np.clip(value, 0, 255)))
                title = f"Image Addition (+{value})"
                note = "Pixel values are increased with saturation at 255."
            elif operation == "subtract":
                value = int(request.form.get("value", 40))
                result = cv2.subtract(img, np.full_like(img, np.clip(value, 0, 255)))
                title = f"Image Subtraction (-{value})"
                note = "Pixel values are decreased with saturation at 0."
            elif operation == "and":
                value = int(request.form.get("value", 128))
                result = cv2.bitwise_and(img, np.full_like(img, np.clip(value, 0, 255)))
                title = f"Bitwise AND ({value})"
                note = "Each channel is ANDed with the selected mask value."
            elif operation == "or":
                value = int(request.form.get("value", 128))
                result = cv2.bitwise_or(img, np.full_like(img, np.clip(value, 0, 255)))
                title = f"Bitwise OR ({value})"
                note = "Each channel is ORed with the selected mask value."
            elif operation == "xor":
                value = int(request.form.get("value", 128))
                result = cv2.bitwise_xor(img, np.full_like(img, np.clip(value, 0, 255)))
                title = f"Bitwise XOR ({value})"
                note = "Each channel is XORed with the selected mask value."
            else:
                raise ValueError("Choose an operation.")

        # 2. Geometric transformations
        elif practical == "2":
            h, w = img.shape[:2]
            if operation == "translation":
                tx, ty = float(request.form.get("tx", 50)), float(request.form.get("ty", 30))
                M = np.float32([[1, 0, tx], [0, 1, ty]])
                result = cv2.warpAffine(img, M, (w, h))
                title = f"Translation ({tx:g}, {ty:g})"
            elif operation == "rotation":
                angle = float(request.form.get("angle", 30))
                M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
                result = cv2.warpAffine(img, M, (w, h))
                title = f"Rotation ({angle:g}°)"
            elif operation == "scaling":
                scale = float(request.form.get("scale", 1.3))
                scale = max(0.1, min(scale, 4))
                result = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                title = f"Scaling ({scale:g}×)"
            elif operation == "shearing":
                shx = float(request.form.get("shx", 0.2))
                shy = float(request.form.get("shy", 0.0))
                M = np.float32([[1, shx, 0], [shy, 1, 0]])
                nw = int(w + abs(shx)*h)
                nh = int(h + abs(shy)*w)
                result = cv2.warpAffine(img, M, (nw, nh))
                title = f"Shearing (x={shx:g}, y={shy:g})"
            elif operation == "reflection":
                axis = request.form.get("axis", "horizontal")
                code = 1 if axis == "vertical" else 0
                result = cv2.flip(img, code)
                title = "Reflection — " + ("Vertical axis" if axis == "vertical" else "Horizontal axis")
            elif operation == "cropping":
                h0, w0 = img.shape[:2]
                x, y = int(request.form.get("x", 10)), int(request.form.get("y", 10))
                cw, ch = int(request.form.get("cw", w0//2)), int(request.form.get("ch", h0//2))
                x, y = max(0, min(x, w0-1)), max(0, min(y, h0-1))
                result = img[y:min(y+ch,h0), x:min(x+cw,w0)]
                title = "Cropping"
            else:
                raise ValueError("Choose a transformation.")

        # 3. Enhancement
        elif practical == "3":
            g = gray(img)
            if operation == "histogram":
                result = cv2.equalizeHist(g)
                title = "Histogram Equalization"
                note = "Redistributes grayscale intensities to improve global contrast."
            elif operation == "smoothing":
                k = int(request.form.get("kernel", 5))
                k = max(3, min(k, 31)); k += (k % 2 == 0)
                result = cv2.GaussianBlur(g, (k,k), 0)
                title = f"Spatial Smoothing ({k}×{k})"
            elif operation == "sharpening":
                k = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]], dtype=np.float32)
                result = cv2.filter2D(g, -1, k)
                title = "Spatial Sharpening"
            elif operation == "threshold":
                t = int(request.form.get("threshold", 127))
                _, result = cv2.threshold(g, t, 255, cv2.THRESH_BINARY)
                title = f"Thresholding (T={t})"
            else:
                raise ValueError("Choose an enhancement technique.")

        # 4. Spatial filters
        elif practical == "4":
            k = int(request.form.get("kernel", 5))
            k = max(3, min(k, 31)); k += (k % 2 == 0)
            if operation == "average":
                result = cv2.blur(img, (k,k))
                title = f"Averaging Filter ({k}×{k})"
            elif operation == "gaussian":
                result = cv2.GaussianBlur(img, (k,k), 0)
                title = f"Gaussian Filter ({k}×{k})"
            elif operation == "median":
                result = cv2.medianBlur(img, k)
                title = f"Median Filter ({k}×{k})"
            elif operation == "bilateral":
                d = int(request.form.get("diameter", 9))
                result = cv2.bilateralFilter(img, d, 75, 75)
                title = f"Bilateral Filter (d={d})"
            else:
                raise ValueError("Choose a filter.")

        # 5. Inpainting
        elif practical == "5":
            mask_file = request.files.get("mask")
            if not mask_file or not mask_file.filename:
                raise ValueError("Upload a black-and-white mask image for inpainting.")
            mask_data = np.frombuffer(mask_file.read(), np.uint8)
            mask = cv2.imdecode(mask_data, cv2.IMREAD_GRAYSCALE)
            if mask is None:
                raise ValueError("Mask could not be decoded.")
            mask = cv2.resize(mask, (img.shape[1], img.shape[0]))
            mask = np.where(mask > 127, 255, 0).astype(np.uint8)
            method = cv2.INPAINT_TELEA if operation == "telea" else cv2.INPAINT_NS
            result = cv2.inpaint(img, mask, 3, method)
            title = "Telea Inpainting" if operation == "telea" else "Navier–Stokes (NS) Inpainting"
            note = "White regions in the mask are treated as damaged areas."

        # 6. Lossless compression
        elif practical == "6":
            hs = huffman_stats(img)
            metric = hs
            # Also create a lossless PNG representation for visual/file-size comparison.
            ok, buf = cv2.imencode(".png", img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            if not ok:
                raise ValueError("PNG encoding failed.")
            png_bytes = buf.tobytes()
            original_size = int(request.files.get("image").content_length or 0)
            if original_size <= 0:
                original_size = len(img.tobytes())
            metric["input_file_bytes"] = original_size
            metric["png_file_bytes"] = len(png_bytes)
            metric["png_ratio"] = round(original_size / len(png_bytes), 3) if len(png_bytes) else 0
            title = "Lossless Compression — Huffman + PNG"
            note = "Huffman statistics are calculated on grayscale pixel symbols; PNG is the lossless visual output."
            result = img

        # 7. Morphology
        elif practical == "7":
            g = gray(img)
            _, binary = cv2.threshold(g, int(request.form.get("threshold", 127)), 255, cv2.THRESH_BINARY)
            k = int(request.form.get("kernel", 5)); k = max(3, min(k, 21)); k += (k % 2 == 0)
            kernel = np.ones((k,k), np.uint8)
            if operation == "erosion":
                result = cv2.erode(binary, kernel, iterations=1)
            elif operation == "dilation":
                result = cv2.dilate(binary, kernel, iterations=1)
            elif operation == "opening":
                result = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            elif operation == "closing":
                result = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            else:
                raise ValueError("Choose a morphological operation.")
            title = operation.title() + f" ({k}×{k})"

        # 8. Correlation / template matching
        elif practical == "8":
            tf = request.files.get("template")
            if not tf or not tf.filename:
                raise ValueError("Upload a template image for correlation-based detection.")
            td = np.frombuffer(tf.read(), np.uint8)
            template = cv2.imdecode(td, cv2.IMREAD_COLOR)
            if template is None:
                raise ValueError("Template image could not be decoded.")
            template = cv2.resize(template, (min(template.shape[1], img.shape[1]), min(template.shape[0], img.shape[0])))
            g1, g2 = gray(img), gray(template)
            if g2.shape[0] > g1.shape[0] or g2.shape[1] > g1.shape[1]:
                raise ValueError("Template must be smaller than the input image.")
            corr = cv2.matchTemplate(g1, g2, cv2.TM_CCOEFF_NORMED)
            _, maxv, _, maxloc = cv2.minMaxLoc(corr)
            x, y = maxloc
            th, tw = g2.shape
            result = img.copy()
            cv2.rectangle(result, (x,y), (x+tw,y+th), (0,255,0), 3)
            metric = {"correlation_score": round(float(maxv), 4), "x": int(x), "y": int(y), "template_width": int(tw), "template_height": int(th)}
            title = "Correlation-Based Object Detection"
            note = "The green rectangle marks the location with the highest normalized correlation."

        # 9. Color spaces
        elif practical == "9":
            if operation == "rgb":
                result = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif operation == "hsv":
                result = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            elif operation == "ycrcb":
                result = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            elif operation == "lab":
                result = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
            else:
                raise ValueError("Choose a color space.")
            title = operation.upper() + " Color Space"
            note = "The result is rendered as an RGB visualization; the underlying channels use the selected color-space encoding."

        # 10. Edge detection
        elif practical == "10":
            g = gray(img)
            if operation == "canny":
                lo, hi = int(request.form.get("low", 50)), int(request.form.get("high", 150))
                result = cv2.Canny(g, lo, hi)
                title = f"Canny Edge Detection ({lo}, {hi})"
            elif operation == "sobel":
                sx = cv2.Sobel(g, cv2.CV_64F, 1, 0, ksize=3)
                sy = cv2.Sobel(g, cv2.CV_64F, 0, 1, ksize=3)
                result = cv2.convertScaleAbs(cv2.magnitude(sx.astype(np.float32), sy.astype(np.float32)))
                title = "Sobel Edge Detection"
            elif operation == "prewitt":
                px = np.array([[-1,0,1],[-1,0,1],[-1,0,1]], dtype=np.float32)
                py = np.array([[-1,-1,-1],[0,0,0],[1,1,1]], dtype=np.float32)
                sx = cv2.filter2D(g, cv2.CV_32F, px)
                sy = cv2.filter2D(g, cv2.CV_32F, py)
                result = cv2.convertScaleAbs(cv2.magnitude(sx, sy))
                title = "Prewitt Edge Detection"
            else:
                raise ValueError("Choose an edge detector.")

        else:
            raise ValueError("Unknown practical.")

        return jsonify({
            "ok": True,
            "title": title,
            "note": note,
            "image": img_to_data_url(result),
            "input_stats": stats(img),
            "output_stats": stats(result),
            "metric": metric
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.errorhandler(413)
def too_large(e):
    return jsonify({"ok": False, "error": "File is too large. Maximum upload size is 12 MB."}), 413

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
