import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def create_logo():
    # consistent with previous SVG dimensions approx ratio
    fig_width = 4
    fig_height = 1.5
    dpi = 100

    fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1], frameon=False)
    ax.set_axis_off()

    # Background "Tape" - Light Gray Rectangle with rounded appearance
    # Matplotlib doesn't have easy rounded rect patch for data coords mixed with figure,
    # but a simple rectangle is fine for the "tape" look.
    rect = patches.FancyBboxPatch((0.05, 0.2), 0.9, 0.6,
                                  boxstyle="round,pad=0.05",
                                  ec="#333333", fc="#f5f5f5",
                                  linewidth=2,
                                  transform=ax.transAxes)
    ax.add_patch(rect)

    # Tape Holes
    hole_color = '#333333'
    holes_x = [0.08, 0.08, 0.92, 0.92]
    holes_y = [0.35, 0.65, 0.35, 0.65]
    ax.scatter(holes_x, holes_y, s=50, c=hole_color, transform=ax.transAxes, zorder=5)

    # Graph Line (Stylized)
    # Generate some smooth curve data
    x = np.linspace(0.15, 0.85, 100)
    # y = sine wave + trend
    y = 0.5 + 0.15 * np.sin(x * 10) + 0.1 * (x - 0.5)

    # Colored segments for "mood"
    # We can plot the line in segments or just use a multicolored line collection.
    # Simpler: Just plotting a gradient-like line is hard in simple plot, let's use solid color
    # or segments. Let's use a color map.

    from matplotlib.collections import LineCollection

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Normalize x for color map (Red to Green)
    norm = plt.Normalize(x.min(), x.max())
    lc = LineCollection(segments, cmap='RdYlGn', norm=norm, linewidth=5)

    # Set the values used for colormapping
    lc.set_array(x)

    # We need to add this to the axes, but coordinate system is 0-1 (transAxes)
    # LineCollection uses data coordinates. Let's setup axes to 0-1
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_collection(lc)

    # Text "Ticker Tape MMI"
    ax.text(0.5, 0.82, "Ticker Tape MMI",
            transform=ax.transAxes,
            ha='center', va='center',
            fontsize=20, weight='bold', color='#333333', fontfamily='sans-serif')

    # Indicator Dot (at the end)
    last_x, last_y = x[-1], y[-1]
    ax.scatter([last_x], [last_y], s=100, c='green', zorder=10) # End point greed

    plt.savefig('logo.png', transparent=True)
    print("logo.png created")
    plt.close()

if __name__ == "__main__":
    create_logo()
