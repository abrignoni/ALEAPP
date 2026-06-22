"""Offline geospatial helpers for artifacts.

Intentionally tile-free / network-free: rendering a GPS track must never fetch
map tiles from an online server during forensic processing (that would leak the
subject's coordinates to a third party and require connectivity). The track is
drawn on a blank canvas; for real geographic context the artifact should also
emit KML for the examiner to open in their own mapping tool.
"""

import io
import math

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover - Pillow is a project dependency
    Image = None


def render_gps_track_png(coords, size=600, pad=30):
    """Render a GPS track to PNG bytes, fully offline (no map tiles, no network).

    Args:
        coords: iterable of (latitude, longitude) pairs.
        size: max canvas dimension in pixels.
        pad: padding in pixels around the track.

    Returns:
        PNG bytes of the track polyline (green start dot, red end dot) on a blank
        canvas, or b'' when there is nothing to draw. Pair with
        check_in_embedded_media(source_file, png, name, force_type='image/png',
        force_extension='png').
    """
    if Image is None:
        return b''

    pts = []
    for coord in coords or []:
        try:
            lat, lon = float(coord[0]), float(coord[1])
        except (TypeError, ValueError, IndexError):
            continue
        pts.append((lat, lon))
    if not pts:
        return b''

    mean_lat = sum(p[0] for p in pts) / len(pts)
    # Equirectangular projection: scale longitude by cos(latitude) so the aspect
    # ratio is roughly correct for the area covered.
    xs = [p[1] * math.cos(math.radians(mean_lat)) for p in pts]
    ys = [p[0] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    spanx = (maxx - minx) or 1e-9
    spany = (maxy - miny) or 1e-9
    scale = (size - 2 * pad) / max(spanx, spany)

    width = max(int(spanx * scale) + 2 * pad, 2 * pad + 1)
    height = max(int(spany * scale) + 2 * pad, 2 * pad + 1)
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    px = [(pad + (x - minx) * scale, (height - pad) - (y - miny) * scale)
          for x, y in zip(xs, ys)]
    if len(px) > 1:
        draw.line(px, fill=(30, 90, 200), width=3, joint='curve')
    radius = 5
    draw.ellipse([px[0][0] - radius, px[0][1] - radius, px[0][0] + radius, px[0][1] + radius],
                 fill=(0, 160, 0))   # start
    draw.ellipse([px[-1][0] - radius, px[-1][1] - radius, px[-1][0] + radius, px[-1][1] + radius],
                 fill=(210, 0, 0))   # end

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
