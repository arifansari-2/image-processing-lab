# Image Processing Lab — All Practicals

A professional Flask + OpenCV web application for demonstrating all 10 Image Processing practicals.

## Included practicals

1. Image representation, RGB/Grayscale, arithmetic and bitwise operations
2. 2-D geometric transformations: Translation, Rotation, Scaling, Shearing, Reflection, Cropping
3. Spatial enhancement: Histogram Equalization, Smoothing, Sharpening, Thresholding
4. Spatial filters: Averaging, Gaussian, Median, Bilateral
5. Image inpainting: Telea and Navier–Stokes
6. Lossless compression: Huffman statistics + PNG lossless output
7. Morphology: Erosion, Dilation, Opening, Closing
8. Correlation-based object detection / template matching
9. RGB, HSV, YCrCb and Lab colour spaces
10. Canny, Sobel and Prewitt edge detection

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Linux/macOS:
```bash
source .venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
python app.py
```

Open:
http://127.0.0.1:5000

## Deploy on Render

1. Create a GitHub repository and upload this folder.
2. Sign in to Render and create a new **Web Service** from the repository.
3. Render can use the included `render.yaml`, or set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Deploy.
5. Open the generated `.onrender.com` URL.

## Important practical notes

- Practical 5 needs a separate mask image. White pixels indicate damaged regions.
- Practical 8 needs a separate template image. The app uses normalized correlation/template matching and draws the best match.
- Practical 6 reports Huffman coding statistics and also returns the original image as the lossless PNG representation. File-size comparisons can vary by image format and content.
- Uploaded files are processed in memory; the app does not need a database or permanent upload folder.

## Suggested project demonstration flow

Upload image → choose practical → choose operation → adjust parameters → Run Processing → compare input/output → inspect metrics.

This project is intentionally designed so each practical can be demonstrated from one interface rather than using ten separate Python programs.
