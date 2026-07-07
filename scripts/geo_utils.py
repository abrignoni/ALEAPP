"""Offline geospatial helpers for artifacts.

Intentionally tile-free / network-free: rendering a GPS track must never fetch
map tiles from an online server during forensic processing (that would leak the
subject's coordinates to a third party and require connectivity). The track is
drawn on a blank canvas; for real geographic context the artifact also emits a
route KML for the examiner to open in their own mapping tool.
"""

import io
import math

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - Pillow is a project dependency
    Image = None


def _font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1 has no size arg
        return ImageFont.load_default()


def _norm_coords(coords):
    pts = []
    for coord in coords or []:
        try:
            lat, lon = float(coord[0]), float(coord[1])
        except (TypeError, ValueError, IndexError):
            continue
        pts.append((lat, lon))
    return pts


def _arrowhead(draw, x, y, dx, dy, s, color):
    n = math.hypot(dx, dy) or 1
    dx, dy = dx / n, dy / n
    perpx, perpy = -dy, dx
    tip = (x + dx * s, y + dy * s)
    base1 = (x - dx * s * 0.4 + perpx * s * 0.7, y - dy * s * 0.4 + perpy * s * 0.7)
    base2 = (x - dx * s * 0.4 - perpx * s * 0.7, y - dy * s * 0.4 - perpy * s * 0.7)
    draw.polygon([tip, base1, base2], fill=color)


def render_gps_track_png(coords, title='', subtitle='', size=600, pad=46):
    """Render a GPS track to PNG bytes, fully offline (no map tiles, no network).

    The image shows the track polyline (green start dot, red end dot) with
    direction-of-travel chevrons, a north arrow, a distance scale bar, an optional
    caption (title/subtitle), and a start/end coordinate footer that anchors the
    route to real-world latitude/longitude.

    Args:
        coords: iterable of (latitude, longitude) pairs.
        title: bold caption line (e.g. the activity type).
        subtitle: secondary caption line (e.g. date / distance / duration).
        size: max canvas dimension in pixels.
        pad: padding in pixels around the track.

    Returns:
        PNG bytes, or b'' when there is nothing to draw. Pair with
        check_in_embedded_media(source, png, name, force_type='image/png',
        force_extension='png').
    """
    if Image is None:
        return b''
    pts = _norm_coords(coords)
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

    top = 44 if (title or subtitle) else 0
    bot = 50
    width = max(int(spanx * scale) + 2 * pad, 300)
    height = int(spany * scale) + 2 * pad + top + bot
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    px = [(pad + (x - minx) * scale, (height - pad - bot) - (y - miny) * scale)
          for x, y in zip(xs, ys)]

    f_title, f_sub, f_sm, f_xs = _font(18), _font(13), _font(12), _font(11)
    if title:
        draw.text((pad, 9), title, fill=(25, 25, 25), font=f_title)
    if subtitle:
        draw.text((pad, 30), subtitle, fill=(115, 115, 115), font=f_sub)

    if len(px) > 1:
        draw.line(px, fill=(30, 90, 200), width=3, joint='curve')
        for frac in (0.25, 0.5, 0.75):
            i = int(frac * (len(px) - 1))
            j = min(i + 1, len(px) - 1)
            _arrowhead(draw, px[i][0], px[i][1], px[j][0] - px[i][0], px[j][1] - px[i][1],
                       7, (30, 90, 200))

    radius = 6
    draw.ellipse([px[0][0] - radius, px[0][1] - radius, px[0][0] + radius, px[0][1] + radius],
                 fill=(0, 160, 0))
    draw.ellipse([px[-1][0] - radius, px[-1][1] - radius, px[-1][0] + radius, px[-1][1] + radius],
                 fill=(210, 0, 0))
    draw.text((px[0][0] + 9, px[0][1] - 6), 'Start', fill=(0, 120, 0), font=f_sm)
    draw.text((px[-1][0] + 9, px[-1][1] - 6), 'End', fill=(180, 0, 0), font=f_sm)

    # north arrow (top-right)
    nx, ny = width - 26, top + 22
    draw.line([(nx, ny + 12), (nx, ny - 12)], fill=(90, 90, 90), width=2)
    _arrowhead(draw, nx, ny - 12, 0, -1, 6, (90, 90, 90))
    draw.text((nx - 4, ny + 13), 'N', fill=(90, 90, 90), font=f_xs)

    # distance scale bar (offline: derived from the track's own extent)
    m_per_px = 111320.0 / scale
    nice = min([10, 25, 50, 100, 250, 500, 1000, 2000, 5000],
               key=lambda v: abs(v - m_per_px * ((width - 2 * pad) / 4)))
    bar = nice / m_per_px
    bx, by = pad, height - 30
    draw.line([(bx, by), (bx + bar, by)], fill=(70, 70, 70), width=2)
    draw.line([(bx, by - 4), (bx, by + 4)], fill=(70, 70, 70), width=2)
    draw.line([(bx + bar, by - 4), (bx + bar, by + 4)], fill=(70, 70, 70), width=2)
    label = f'{nice} m' if nice < 1000 else f'{nice / 1000:g} km'
    draw.text((bx + bar + 6, by - 7), label, fill=(70, 70, 70), font=f_sm)

    # start/end coordinate footer (the geographic anchor, since there's no basemap)
    s0, e0 = pts[0], pts[-1]
    draw.text((pad, height - 15),
              f'Start {s0[0]:.5f}, {s0[1]:.5f}    End {e0[0]:.5f}, {e0[1]:.5f}',
              fill=(120, 120, 120), font=f_xs)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def build_track_kml(coords, name='Route'):
    """Build a route KML (a single LineString of the track) as bytes, offline.

    Uses simplekml (already a project dependency, used by ilapfuncs.kmlgen). Pair
    with check_in_embedded_media(source, kml, name + '.kml',
    force_type='application/vnd.google-earth.kml+xml', force_extension='kml') to
    surface a downloadable route file the examiner can open in Google Earth.

    Returns KML bytes, or b'' when there are fewer than two points.
    """
    pts = _norm_coords(coords)
    if len(pts) < 2:
        return b''
    try:
        import simplekml
    except ImportError:  # pragma: no cover - simplekml is a project dependency
        return b''
    kml = simplekml.Kml()
    line = kml.newlinestring(name=name, coords=[(lon, lat) for lat, lon in pts])
    line.style.linestyle.width = 3
    line.style.linestyle.color = simplekml.Color.blue
    return kml.kml().encode('utf-8')
