import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageDraw, ImageTk, ImageFont
import random
import io
import math
from collections import deque


class PaintApp:
    def __init__(self, root):
        # Save the main Tk window and set up the basic app window.
        self.root = root
        self.root.title("Advanced Paint App")
        self.root.geometry("1280x800")

        # Keep track of the current drawing color and whether dark mode is on.
        self.current_color = "black"
        self.dark_mode = False

        # Store the canvas size and its current background color.
        self.canvas_width = 1280
        self.canvas_height = 740
        self.canvas_bg = "white"

        # base_image is the permanent image underneath everything.
        # base_draw lets us draw directly onto that image using PIL.
        self.base_image = Image.new("RGB", (self.canvas_width, self.canvas_height), self.canvas_bg)
        self.base_draw = ImageDraw.Draw(self.base_image)

        # tk_image is the Tkinter version of the PIL image used for display.
        # undo_stack stores previous states so Undo can restore them.
        self.tk_image = None
        self.undo_stack = []

        # Used when previewing shapes or waiting for an imported image
        # to be placed on the canvas.
        self.preview_shape = None
        self.image_to_insert = None
        self.waiting_for_placement = False

        # Mouse position tracking for drawing and object editing.
        self.last_x = None
        self.last_y = None
        self.start_x = None
        self.start_y = None

        # Current mode/tool selections.
        self.mode = "brush"
        self.selected_brush = "pen"
        self.selected_tool = "select"
        self.selected_shape = "rectangle"
        self.selected_emoji = "😀"

        # Available options shown in the menus.
        self.brush_options = [
            "pen", "spray", "pencil", "marker", "airbrush",
            "calligraphy", "crayon", "watercolor", "neon", "dashed"
        ]
        self.tool_options = ["select", "eraser", "fill", "text"]
        self.shape_options = [
            "rectangle", "oval", "circle", "triangle",
            "diamond", "pentagon", "hexagon", "star"
        ]
        self.emoji_options = [
            "😀", "😂", "😍", "😎", "🤔",
            "😭", "😡", "🥳", "😴", "🤖",
            "👻", "💀", "❤️", "⭐", "🔥",
            "👍", "🎉", "🌈", "⚡", "🍕"
        ]

        # objects stores every movable/editable item placed on the canvas.
        # next_object_id gives each one a unique ID.
        self.objects = []
        self.next_object_id = 1

        # These variables keep track of which object is selected and
        # what kind of edit action is currently happening.
        self.selected_object_id = None
        self.edit_handles_visible = False
        self.dragging_object = False
        self.resizing_object = False
        self.rotating_object = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Size settings for the visible edit handles.
        self.move_handle_radius = 14
        self.resize_handle_size = 14
        self.rotate_handle_radius = 14

        # current_stroke temporarily stores a brush stroke while the user is drawing.
        self.current_stroke = None

        # Build the interface and draw the initial blank canvas.
        self.setup_ui()
        self.redraw_canvas()

    # ===============================
    # UI
    # ===============================
    def setup_ui(self):
        # Create the toolbar across the top of the window.
        self.toolbar = tk.Frame(self.root, bg="lightgray")
        self.toolbar.pack(fill=tk.X)

        # Color buttons the user can click to switch colors quickly.
        colors = ["black", "red", "green", "blue", "purple",
                  "yellow", "pink", "gray", "orange", "brown"]

        for color in colors:
            tk.Button(
                self.toolbar,
                bg=color,
                width=3,
                command=lambda c=color: self.set_color(c)
            ).pack(side=tk.LEFT, padx=2, pady=2)

        # Label showing the currently selected color.
        self.color_label = tk.Label(self.toolbar, text="Color: Black", bg="lightgray")
        self.color_label.pack(side=tk.LEFT, padx=8)

        # Slider for brush/outline width.
        self.width_slider = tk.Scale(
            self.toolbar, from_=1, to=30, orient=tk.HORIZONTAL,
            label="Width", bg="lightgray"
        )
        self.width_slider.set(3)
        self.width_slider.pack(side=tk.LEFT, padx=4)

        # Slider for text size, emoji size, and similar object sizing.
        self.size_slider = tk.Scale(
            self.toolbar, from_=12, to=140, orient=tk.HORIZONTAL,
            label="Object Size", bg="lightgray"
        )
        self.size_slider.set(36)
        self.size_slider.pack(side=tk.LEFT, padx=4)

        # Drop-down menu for brush types.
        self.brush_var = tk.StringVar(value="Brushes")
        self.brush_menu = tk.OptionMenu(
            self.toolbar,
            self.brush_var,
            *[b.capitalize() for b in self.brush_options],
            command=self.choose_brush
        )
        self.brush_menu.config(width=12)
        self.brush_menu.pack(side=tk.LEFT, padx=4)

        # Drop-down menu for tools like select, eraser, fill, and text.
        self.tool_var = tk.StringVar(value="Tools")
        self.tool_menu = tk.OptionMenu(
            self.toolbar,
            self.tool_var,
            *[t.capitalize() for t in self.tool_options],
            command=self.choose_tool
        )
        self.tool_menu.config(width=10)
        self.tool_menu.pack(side=tk.LEFT, padx=4)

        # Drop-down menu for shape choices.
        self.shape_var = tk.StringVar(value="Shapes")
        self.shape_menu = tk.OptionMenu(
            self.toolbar,
            self.shape_var,
            *[s.capitalize() for s in self.shape_options],
            command=self.choose_shape
        )
        self.shape_menu.config(width=11)
        self.shape_menu.pack(side=tk.LEFT, padx=4)

        # Drop-down menu for emoji choices.
        self.emoji_var = tk.StringVar(value="Emojis")
        self.emoji_menu = tk.OptionMenu(
            self.toolbar,
            self.emoji_var,
            *self.emoji_options,
            command=self.choose_emoji
        )
        self.emoji_menu.config(width=8)
        self.emoji_menu.pack(side=tk.LEFT, padx=4)

        # Main action buttons for common app features.
        tk.Button(self.toolbar, text="Insert Image", command=self.insert_image).pack(side=tk.LEFT, padx=3)
        tk.Button(self.toolbar, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=3)
        tk.Button(self.toolbar, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=3)
        tk.Button(self.toolbar, text="Save", command=self.save_image).pack(side=tk.LEFT, padx=3)
        tk.Button(self.toolbar, text="Load", command=self.load_image).pack(side=tk.LEFT, padx=3)
        tk.Button(self.toolbar, text="Dark Mode", command=self.toggle_dark_mode).pack(side=tk.LEFT, padx=3)
        tk.Button(self.toolbar, text="Delete Selected", command=self.delete_selected_object).pack(side=tk.LEFT, padx=3)

        # Status label tells the user what mode the app is currently in.
        self.status_label = tk.Label(self.toolbar, text="Mode: Brush (Pen)", bg="lightgray")
        self.status_label.pack(side=tk.LEFT, padx=12)

        # The main drawing area.
        self.canvas = tk.Canvas(self.root, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Mouse bindings for drawing and editing on the canvas.
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.canvas.bind("<Double-Button-1>", self.handle_double_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        # Escape cancels the current action and returns to select mode.
        self.root.bind("<Escape>", self.handle_escape)

    # ===============================
    # UI STATE
    # ===============================
    def set_color(self, color):
        # Change the current drawing color and update the toolbar label.
        self.current_color = color
        self.color_label.config(text=f"Color: {color.capitalize()}")

    def set_status(self, text):
        # Update the status message shown in the toolbar.
        self.status_label.config(text=text)

    def choose_brush(self, choice):
        # Switch into brush mode and remember which brush was chosen.
        self.mode = "brush"
        self.selected_brush = choice.lower()
        self.clear_selection()
        self.set_status(f"Mode: Brush ({self.selected_brush.capitalize()})")
        self.redraw_canvas()

    def choose_tool(self, choice):
        # Switch into tool mode and remember which tool was chosen.
        self.mode = "tool"
        self.selected_tool = choice.lower()
        if self.selected_tool != "select":
            self.clear_selection()
        self.set_status(f"Mode: Tool ({self.selected_tool.capitalize()})")
        self.redraw_canvas()

    def choose_shape(self, choice):
        # Switch into shape mode and remember which shape was chosen.
        self.mode = "shape"
        self.selected_shape = choice.lower()
        self.clear_selection()
        self.set_status(f"Mode: Shape ({self.selected_shape.capitalize()})")
        self.redraw_canvas()

    def choose_emoji(self, choice):
        # Switch into emoji mode and store the chosen emoji.
        self.mode = "emoji"
        self.selected_emoji = choice
        self.clear_selection()
        self.set_status(f"Mode: Emoji ({self.selected_emoji})")
        self.redraw_canvas()

    def clear_selection(self):
        # Deselect the current object and reset all edit states.
        self.selected_object_id = None
        self.edit_handles_visible = False
        self.dragging_object = False
        self.resizing_object = False
        self.rotating_object = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def handle_escape(self, event=None):
        # Cancel anything in progress: stroke drawing, shape preview,
        # image placement, dragging, resizing, rotation, and selection.
        self.current_stroke = None
        self.preview_shape = None
        self.start_x = None
        self.start_y = None
        self.last_x = None
        self.last_y = None

        self.waiting_for_placement = False
        self.image_to_insert = None

        self.dragging_object = False
        self.resizing_object = False
        self.rotating_object = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.selected_object_id = None
        self.edit_handles_visible = False

        # Return to select mode after cancelling.
        self.mode = "tool"
        self.selected_tool = "select"
        self.tool_var.set("Select")
        self.set_status("Mode: Tool (Select) — action cancelled")

        self.redraw_canvas()

    # ===============================
    # FONT / MATH
    # ===============================
    def load_font(self, size):
        # Try common font files in order until one works.
        # This helps text and emoji render on different systems.
        candidates = ["seguiemj.ttf", "Segoe UI Emoji.ttf", "arial.ttf"]
        for name in candidates:
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                pass
        return ImageFont.load_default()

    def rotate_point(self, x, y, cx, cy, angle_deg):
        # Rotate one point around a center point by the given angle.
        radians = math.radians(angle_deg)
        dx = x - cx
        dy = y - cy
        rx = dx * math.cos(radians) - dy * math.sin(radians)
        ry = dx * math.sin(radians) + dy * math.cos(radians)
        return cx + rx, cy + ry

    def angle_from_center(self, cx, cy, mx, my):
        # Find the angle from the object's center to the mouse position.
        return math.degrees(math.atan2(my - cy, mx - cx))

    def color_to_rgb(self, color_name):
        # Convert a Tk/PIL color name into an RGB tuple.
        return Image.new("RGB", (1, 1), color_name).getpixel((0, 0))

    def clamp(self, value, low, high):
        # Keep a number inside a minimum/maximum range.
        return max(low, min(high, value))

    def rgba_with_alpha(self, color_name, alpha):
        # Build an RGBA color tuple from a named color and transparency value.
        r, g, b = self.color_to_rgb(color_name)
        return (r, g, b, self.clamp(alpha, 0, 255))

    # ===============================
    # RESIZE / UNDO
    # ===============================
    def on_resize(self, event):
        # If the window changes size, grow the base image to match.
        # Existing artwork is pasted into the new larger image.
        if event.width < 10 or event.height < 10:
            return
        if event.width == self.canvas_width and event.height == self.canvas_height:
            return

        old_img = self.base_image
        self.canvas_width = event.width
        self.canvas_height = event.height

        new_img = Image.new("RGB", (self.canvas_width, self.canvas_height), self.canvas_bg)
        new_img.paste(old_img, (0, 0))
        self.base_image = new_img
        self.base_draw = ImageDraw.Draw(self.base_image)

        self.redraw_canvas()

    def copy_object(self, obj):
        # Make a safe copy of an object dictionary for Undo.
        copied = {}
        for k, v in obj.items():
            if isinstance(v, list):
                copied[k] = [tuple(p) if isinstance(p, tuple) else p for p in v]
            elif isinstance(v, tuple):
                copied[k] = tuple(v)
            else:
                copied[k] = v
        return copied

    def save_undo_state(self):
        # Save the current image and object list so Undo can restore it later.
        buffer = io.BytesIO()
        self.base_image.save(buffer, format="PNG")
        state = {
            "image": buffer.getvalue(),
            "objects": [self.copy_object(obj) for obj in self.objects],
            "next_object_id": self.next_object_id
        }
        self.undo_stack.append(state)
        if len(self.undo_stack) > 20:
            self.undo_stack.pop(0)

    def undo(self):
        # Restore the most recent saved state.
        if not self.undo_stack:
            return
        state = self.undo_stack.pop()
        self.base_image = Image.open(io.BytesIO(state["image"])).convert("RGB")
        self.base_draw = ImageDraw.Draw(self.base_image)
        self.objects = [self.copy_object(obj) for obj in state["objects"]]
        self.next_object_id = state["next_object_id"]
        self.clear_selection()
        self.redraw_canvas()

    # ===============================
    # OBJECTS
    # ===============================
    def add_object(self, obj):
        # Add a new drawable object to the canvas and assign it a unique ID.
        obj["id"] = self.next_object_id
        self.next_object_id += 1
        obj.setdefault("rotation", 0)
        self.objects.append(obj)
        self.selected_object_id = obj["id"]
        self.edit_handles_visible = False

    def get_object_by_id(self, obj_id):
        # Find a specific object by ID.
        for obj in reversed(self.objects):
            if obj["id"] == obj_id:
                return obj
        return None

    def get_path_bbox(self, points, width=1):
        # Return a bounding box around a brush stroke.
        if not points:
            return (0, 0, 0, 0)
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        pad = max(8, width + 6)
        return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)

    def get_shape_points(self, obj):
        # Convert a shape object into corner/point coordinates.
        x1, y1, x2, y2 = obj["bbox"]
        shape = obj["shape"]

        if shape == "rectangle":
            return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

        if shape in ("oval", "circle"):
            if shape == "circle":
                x1, y1, x2, y2 = self.normalize_circle(x1, y1, x2, y2)
            return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

        pts = self.get_polygon_points(shape, x1, y1, x2, y2)
        return [(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]

    def get_object_bbox(self, obj):
        # Return the selection bounding box for any object type.
        rotation = obj.get("rotation", 0)

        if obj["type"] == "emoji":
            s = max(20, obj["size"])
            cx, cy = obj["x"], obj["y"]
            corners = [
                (cx - s, cy - s), (cx + s, cy - s),
                (cx + s, cy + s), (cx - s, cy + s)
            ]
            if rotation:
                corners = [self.rotate_point(x, y, cx, cy, rotation) for x, y in corners]
            xs = [p[0] for p in corners]
            ys = [p[1] for p in corners]
            return min(xs), min(ys), max(xs), max(ys)

        if obj["type"] == "text":
            # Approximate text size so the app can show selection handles.
            s = max(20, obj["size"])
            approx_w = max(s, int(len(obj["text"]) * s * 0.55))
            approx_h = int(s * 1.0)
            cx, cy = obj["x"], obj["y"]
            corners = [
                (cx - approx_w // 2, cy - approx_h // 2),
                (cx + approx_w // 2, cy - approx_h // 2),
                (cx + approx_w // 2, cy + approx_h // 2),
                (cx - approx_w // 2, cy + approx_h // 2),
            ]
            if rotation:
                corners = [self.rotate_point(x, y, cx, cy, rotation) for x, y in corners]
            xs = [p[0] for p in corners]
            ys = [p[1] for p in corners]
            return min(xs), min(ys), max(xs), max(ys)

        if obj["type"] == "shape":
            pts = self.get_shape_points(obj)
            if rotation:
                cx, cy = self.get_object_center(obj)
                pts = [self.rotate_point(x, y, cx, cy, rotation) for x, y in pts]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            return min(xs), min(ys), max(xs), max(ys)

        if obj["type"] == "stroke":
            return self.get_path_bbox(obj["points"], obj["width"])

        return (0, 0, 0, 0)

    def find_object_at(self, x, y):
        # Check from topmost object down to find what the user clicked.
        for obj in reversed(self.objects):
            x1, y1, x2, y2 = self.get_object_bbox(obj)
            if x1 <= x <= x2 and y1 <= y <= y2:
                return obj
        return None

    def get_object_center(self, obj):
        # Return the center point of an object.
        if obj["type"] in ("emoji", "text"):
            return obj["x"], obj["y"]

        if obj["type"] == "shape":
            x1, y1, x2, y2 = obj["bbox"]
            return (x1 + x2) / 2, (y1 + y2) / 2

        x1, y1, x2, y2 = self.get_object_bbox(obj)
        return (x1 + x2) / 2, (y1 + y2) / 2

    def get_move_handle_position(self, obj):
        # Position the green move handle near the top-left of the selection box.
        x1, y1, _, _ = self.get_object_bbox(obj)
        return (x1 + 16, y1 + 16)

    def get_resize_handle_position(self, obj):
        # Position the orange resize handle near the bottom-right.
        _, _, x2, y2 = self.get_object_bbox(obj)
        return (x2 - 16, y2 - 16)

    def get_rotate_handle_position(self, obj):
        # Position the rotate handle above the selected object.
        x1, y1, x2, _ = self.get_object_bbox(obj)
        return ((x1 + x2) / 2, y1 - 36)

    def hit_test_move_handle(self, obj, x, y):
        # Return True if the mouse is over the move handle.
        hx, hy = self.get_move_handle_position(obj)
        return ((x - hx) ** 2 + (y - hy) ** 2) <= (self.move_handle_radius + 4) ** 2

    def hit_test_resize_handle(self, obj, x, y):
        # Return True if the mouse is over the resize handle.
        hx, hy = self.get_resize_handle_position(obj)
        s = self.resize_handle_size + 4
        return hx - s <= x <= hx + s and hy - s <= y <= hy + s

    def hit_test_rotate_handle(self, obj, x, y):
        # Return True if the mouse is over the rotate handle.
        hx, hy = self.get_rotate_handle_position(obj)
        return ((x - hx) ** 2 + (y - hy) ** 2) <= (self.rotate_handle_radius + 4) ** 2

    # ===============================
    # TEXT EDITING / SHAPES
    # ===============================
    def edit_text_object(self, obj):
        # Ask the user for replacement text when a text object is edited.
        new_text = simpledialog.askstring(
            "Edit Text",
            "Update text:",
            initialvalue=obj["text"]
        )
        if new_text is not None and new_text.strip():
            self.save_undo_state()
            obj["text"] = new_text.strip()
            obj["size"] = self.size_slider.get()
            obj["color"] = self.current_color

    def get_polygon_points(self, shape_name, x1, y1, x2, y2):
        # Calculate point lists for non-rectangle polygon shapes.
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)

        cx = (left + right) / 2
        cy = (top + bottom) / 2
        r = min(right - left, bottom - top) / 2

        if shape_name == "triangle":
            return [cx, top, left, bottom, right, bottom]

        if shape_name == "diamond":
            return [cx, top, left, cy, cx, bottom, right, cy]

        if shape_name == "pentagon":
            pts = []
            for i in range(5):
                a = math.radians(-90 + i * 72)
                pts.extend([cx + r * math.cos(a), cy + r * math.sin(a)])
            return pts

        if shape_name == "hexagon":
            pts = []
            for i in range(6):
                a = math.radians(-90 + i * 60)
                pts.extend([cx + r * math.cos(a), cy + r * math.sin(a)])
            return pts

        if shape_name == "star":
            pts = []
            outer_r = r
            inner_r = r * 0.45
            for i in range(10):
                a = math.radians(-90 + i * 36)
                rr = outer_r if i % 2 == 0 else inner_r
                pts.extend([cx + rr * math.cos(a), cy + rr * math.sin(a)])
            return pts

        return []

    def normalize_circle(self, x1, y1, x2, y2):
        # Force the circle preview and final circle to stay perfectly round.
        side = min(abs(x2 - x1), abs(y2 - y1))
        x2 = x1 + side if x2 >= x1 else x1 - side
        y2 = y1 + side if y2 >= y1 else y1 - side
        return x1, y1, x2, y2

    # ===============================
    # STROKE HELPERS
    # ===============================
    def point_distance(self, p1, p2):
        # Standard distance formula between two points.
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def interpolate_points(self, p1, p2, step):
        # Create extra points between two mouse points so effects like spray
        # and watercolor do not leave gaps when the mouse moves quickly.
        dist = self.point_distance(p1, p2)
        if dist == 0:
            return [p1]
        count = max(1, int(dist / max(1, step)))
        pts = []
        for i in range(count + 1):
            t = i / count
            pts.append((p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t))
        return pts

    def get_path_segments(self, points, step):
        # Turn a path into a denser list of points.
        stamped = []
        if len(points) < 2:
            return stamped
        for i in range(len(points) - 1):
            stamped.extend(self.interpolate_points(points[i], points[i + 1], step))
        return stamped

    def jittered_polyline(self, points, jitter):
        # Add randomness to a line to make brushes like pencil feel rougher.
        jittered = []
        for x, y in points:
            jittered.append((x + random.uniform(-jitter, jitter), y + random.uniform(-jitter, jitter)))
        return jittered

    # ===============================
    # BRUSH PREVIEW ON CANVAS
    # ===============================
    def draw_temporary_stroke(self, stroke):
        # Draw the current stroke directly on the Tk canvas so the user sees
        # live feedback while dragging the mouse.
        points = stroke["points"]
        if len(points) < 2:
            return

        brush = stroke["brush"]
        color = stroke["color"]
        width = stroke["width"]

        if brush == "pen":
            flat = []
            for px, py in points:
                flat.extend([px, py])
            self.canvas.create_line(*flat, fill=color, width=width, smooth=True, capstyle=tk.ROUND)
            return

        if brush == "pencil":
            # Pencil is drawn as several lightly jittered lines.
            for _ in range(3):
                jittered = self.jittered_polyline(points, max(1, width * 0.35))
                flat = []
                for px, py in jittered:
                    flat.extend([px, py])
                self.canvas.create_line(*flat, fill=color, width=max(1, width // 2), smooth=True, capstyle=tk.ROUND)
            return

        if brush == "marker":
            # Marker is thicker and more blocky than a pen.
            flat = []
            for px, py in points:
                flat.extend([px, py])
            self.canvas.create_line(*flat, fill=color, width=width + 8, smooth=True, capstyle=tk.PROJECTING)
            return

        if brush == "dashed":
            # Dashed draws every other line segment to create a broken line.
            for i in range(0, len(points) - 1, 2):
                if i + 1 < len(points):
                    self.canvas.create_line(
                        points[i][0], points[i][1], points[i + 1][0], points[i + 1][1],
                        fill=color, width=width, capstyle=tk.ROUND, smooth=True
                    )
            return

        stamped = self.get_path_segments(points, max(1, width // 2))

        if brush == "spray":
            radius = max(4, width + 4)
            for x, y in stamped:
                for _ in range(10):
                    px = x + random.randint(-radius, radius)
                    py = y + random.randint(-radius, radius)
                    self.canvas.create_oval(px, py, px + 1, py + 1, outline=color, fill=color)
            return

        if brush == "airbrush":
            radius = max(6, width + 6)
            for x, y in stamped:
                for _ in range(16):
                    px = x + random.randint(-radius, radius)
                    py = y + random.randint(-radius, radius)
                    self.canvas.create_oval(px, py, px + 1, py + 1, outline=color, fill=color)
            return

        if brush == "crayon":
            for x, y in stamped:
                for _ in range(4):
                    jx = random.randint(-max(2, width), max(2, width))
                    jy = random.randint(-max(2, width), max(2, width))
                    size = random.randint(1, max(2, width // 2 + 1))
                    self.canvas.create_line(
                        x + jx, y + jy, x + jx + size, y + jy + size,
                        fill=color, width=max(1, width // 3), capstyle=tk.ROUND
                    )
            return

        if brush == "watercolor":
            radius = max(6, width + 4)
            for x, y in stamped:
                self.canvas.create_oval(
                    x - radius, y - radius, x + radius, y + radius,
                    outline=color, width=1
                )
            return

        if brush == "neon":
            # Neon uses a thick outer line plus a thin white center highlight.
            flat = []
            for px, py in points:
                flat.extend([px, py])
            self.canvas.create_line(*flat, fill=color, width=width + 10, smooth=True, capstyle=tk.ROUND)
            self.canvas.create_line(*flat, fill="white", width=max(1, width // 2), smooth=True, capstyle=tk.ROUND)
            return

        if brush == "calligraphy":
            for i in range(len(stamped) - 1):
                x1, y1 = stamped[i]
                x2, y2 = stamped[i + 1]
                self.canvas.create_line(x1 - 3, y1 + 3, x2 - 3, y2 + 3, fill=color, width=max(2, width + 2))
                self.canvas.create_line(x1 + 2, y1 - 2, x2 + 2, y2 - 2, fill=color, width=max(1, width // 2 + 1))
            return

    # ===============================
    # CANVAS REDRAW / OBJECT RENDERING
    # ===============================
    def redraw_canvas(self):
        # Rebuild the visible canvas from the base image plus all objects.
        self._canvas_temp_images = []
        self.tk_image = ImageTk.PhotoImage(self.base_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        for obj in self.objects:
            self.draw_object_on_canvas(obj)

        if self.current_stroke is not None:
            self.draw_temporary_stroke(self.current_stroke)

        if self.selected_object_id is not None and self.edit_handles_visible:
            obj = self.get_object_by_id(self.selected_object_id)
            if obj:
                self.draw_edit_handles(obj)

    def draw_rotated_text_canvas(self, x, y, text, size, color, angle):
        # Draw text directly if not rotated.
        # If rotated, render it to a temporary image first and then display it.
        if angle == 0:
            self.canvas.create_text(x, y, text=text, font=("Arial", size), fill=color, anchor=tk.CENTER)
            return

        font = self.load_font(size)
        temp = Image.new("RGBA", (max(200, int(len(text) * size * 2)), max(100, size * 3)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(temp)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(((temp.width - tw) // 2, (temp.height - th) // 2), text, font=font, fill=color)
        rotated = temp.rotate(angle, expand=True)
        tk_img = ImageTk.PhotoImage(rotated)
        self._canvas_temp_images.append(tk_img)
        self.canvas.create_image(x, y, image=tk_img, anchor=tk.CENTER)

    def draw_rotated_emoji_canvas(self, x, y, emoji, size, angle):
        # Same approach as rotated text, but for emoji characters.
        if angle == 0:
            self.canvas.create_text(x, y, text=emoji, font=("Segoe UI Emoji", size), anchor=tk.CENTER)
            return

        font = self.load_font(size)
        temp = Image.new("RGBA", (max(120, size * 3), max(120, size * 3)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(temp)
        bbox = draw.textbbox((0, 0), emoji, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(((temp.width - tw) // 2, (temp.height - th) // 2), emoji, font=font, fill="black")
        rotated = temp.rotate(angle, expand=True)
        tk_img = ImageTk.PhotoImage(rotated)
        self._canvas_temp_images.append(tk_img)
        self.canvas.create_image(x, y, image=tk_img, anchor=tk.CENTER)

    def draw_object_on_canvas(self, obj):
        # Draw one object on the visible Tk canvas.
        rotation = obj.get("rotation", 0)

        if obj["type"] == "emoji":
            self.draw_rotated_emoji_canvas(obj["x"], obj["y"], obj["text"], obj["size"], rotation)

        elif obj["type"] == "text":
            self.draw_rotated_text_canvas(obj["x"], obj["y"], obj["text"], obj["size"], obj["color"], rotation)

        elif obj["type"] == "shape":
            x1, y1, x2, y2 = obj["bbox"]
            width = obj["width"]
            color = obj["color"]
            shape = obj["shape"]

            if shape == "rectangle":
                pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                if rotation:
                    cx, cy = self.get_object_center(obj)
                    pts = [self.rotate_point(px, py, cx, cy, rotation) for px, py in pts]
                self.canvas.create_polygon(pts, outline=color, fill="", width=width)

            elif shape in ("oval", "circle"):
                if shape == "circle":
                    x1, y1, x2, y2 = self.normalize_circle(x1, y1, x2, y2)
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                rx = abs(x2 - x1) / 2
                ry = abs(y2 - y1) / 2
                pts = []
                for i in range(40):
                    a = 2 * math.pi * i / 40
                    px = cx + rx * math.cos(a)
                    py = cy + ry * math.sin(a)
                    if rotation:
                        px, py = self.rotate_point(px, py, cx, cy, rotation)
                    pts.append((px, py))
                self.canvas.create_polygon(pts, outline=color, fill="", width=width, smooth=True)

            else:
                pts = self.get_polygon_points(shape, x1, y1, x2, y2)
                pairs = [(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]
                if rotation:
                    cx, cy = self.get_object_center(obj)
                    pairs = [self.rotate_point(px, py, cx, cy, rotation) for px, py in pairs]
                self.canvas.create_polygon(pairs, outline=color, fill="", width=width)

        elif obj["type"] == "stroke":
            self.draw_temporary_stroke(obj)

    def draw_edit_handles(self, obj):
        # Draw the selection box plus move, resize, and rotate handles.
        x1, y1, x2, y2 = self.get_object_bbox(obj)
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="dodgerblue", dash=(4, 2), width=2)

        mx, my = self.get_move_handle_position(obj)
        self.canvas.create_oval(
            mx - self.move_handle_radius, my - self.move_handle_radius,
            mx + self.move_handle_radius, my + self.move_handle_radius,
            fill="#32CD32", outline="black", width=2
        )
        self.canvas.create_text(mx, my, text="M", font=("Arial", 10, "bold"))

        rx, ry = self.get_resize_handle_position(obj)
        s = self.resize_handle_size
        self.canvas.create_rectangle(
            rx - s, ry - s, rx + s, ry + s,
            fill="#FFA500", outline="black", width=2
        )
        self.canvas.create_text(rx, ry, text="R", font=("Arial", 10, "bold"))

        qx, qy = self.get_rotate_handle_position(obj)
        self.canvas.create_oval(
            qx - self.rotate_handle_radius, qy - self.rotate_handle_radius,
            qx + self.rotate_handle_radius, qy + self.rotate_handle_radius,
            fill="#AA66FF", outline="black", width=2
        )
        self.canvas.create_text(qx, qy, text="⟲", font=("Arial", 10, "bold"))

        self.canvas.create_line(
            (x1 + x2) / 2, y1,
            qx, qy + self.rotate_handle_radius,
            fill="gray50", dash=(2, 2), width=2
        )

    # ===============================
    # PIL TEXT / EMOJI / SHAPE DRAWING
    # ===============================
    def draw_text_on_pil(self, base, obj):
        # Render text onto a PIL image so it becomes part of the saved output.
        font = self.load_font(obj["size"])
        temp = Image.new("RGBA", (max(300, int(len(obj["text"]) * obj["size"] * 2)), max(120, obj["size"] * 3)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(temp)
        bbox = draw.textbbox((0, 0), obj["text"], font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(((temp.width - tw) // 2, (temp.height - th) // 2), obj["text"], font=font, fill=obj["color"])
        rotated = temp.rotate(obj.get("rotation", 0), expand=True)
        base.alpha_composite(rotated, (int(obj["x"] - rotated.width / 2), int(obj["y"] - rotated.height / 2)))

    def draw_emoji_on_pil(self, base, obj):
        # Render emoji onto a PIL image for saving/exporting.
        font = self.load_font(obj["size"])
        temp = Image.new("RGBA", (max(140, obj["size"] * 3), max(140, obj["size"] * 3)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(temp)
        bbox = draw.textbbox((0, 0), obj["text"], font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(((temp.width - tw) // 2, (temp.height - th) // 2), obj["text"], font=font, fill="black")
        rotated = temp.rotate(obj.get("rotation", 0), expand=True)
        base.alpha_composite(rotated, (int(obj["x"] - rotated.width / 2), int(obj["y"] - rotated.height / 2)))

    def draw_object_on_pil(self, draw, obj, base_rgba=None):
        # Draw one object onto the final PIL image used for saving.
        rotation = obj.get("rotation", 0)

        if obj["type"] == "emoji":
            if base_rgba is not None:
                self.draw_emoji_on_pil(base_rgba, obj)

        elif obj["type"] == "text":
            if base_rgba is not None:
                self.draw_text_on_pil(base_rgba, obj)

        elif obj["type"] == "shape":
            x1, y1, x2, y2 = obj["bbox"]
            color = obj["color"]
            width = obj["width"]
            shape = obj["shape"]

            if shape == "rectangle":
                pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                if rotation:
                    cx, cy = self.get_object_center(obj)
                    pts = [self.rotate_point(px, py, cx, cy, rotation) for px, py in pts]
                draw.polygon(pts, outline=color, width=width)

            elif shape in ("oval", "circle"):
                if shape == "circle":
                    x1, y1, x2, y2 = self.normalize_circle(x1, y1, x2, y2)
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                rx = abs(x2 - x1) / 2
                ry = abs(y2 - y1) / 2
                pts = []
                for i in range(64):
                    a = 2 * math.pi * i / 64
                    px = cx + rx * math.cos(a)
                    py = cy + ry * math.sin(a)
                    if rotation:
                        px, py = self.rotate_point(px, py, cx, cy, rotation)
                    pts.append((px, py))
                draw.polygon(pts, outline=color, width=width)

            else:
                pts = self.get_polygon_points(shape, x1, y1, x2, y2)
                pairs = [(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]
                if rotation:
                    cx, cy = self.get_object_center(obj)
                    pairs = [self.rotate_point(px, py, cx, cy, rotation) for px, py in pairs]
                draw.polygon(pairs, outline=color, width=width)

        elif obj["type"] == "stroke":
            self.draw_stroke_on_pil(draw, obj)

    # ===============================
    # BRUSH RENDERING ON PIL
    # ===============================
    def draw_pencil_on_pil(self, draw, points, color, width):
        # Pencil effect for saved output.
        for _ in range(4):
            jittered = self.jittered_polyline(points, max(1, width * 0.4))
            draw.line(jittered, fill=color, width=max(1, width // 2))

    def draw_marker_on_pil(self, draw, points, color, width):
        # Marker effect for saved output.
        stamped = self.get_path_segments(points, max(1, width // 2))
        radius_x = max(4, width + 5)
        radius_y = max(2, width // 2 + 2)
        for x, y in stamped:
            draw.ellipse(
                (x - radius_x, y - radius_y, x + radius_x, y + radius_y),
                fill=color
            )

    def draw_spray_on_pil(self, draw, points, color, width, dense=False):
        # Spray and airbrush both place random dots around the path.
        stamped = self.get_path_segments(points, max(1, width // 2))
        radius = max(6, width + (7 if dense else 4))
        dots = 28 if dense else 16
        for x, y in stamped:
            for _ in range(dots):
                px = x + random.randint(-radius, radius)
                py = y + random.randint(-radius, radius)
                draw.point((px, py), fill=color)

    def draw_calligraphy_on_pil(self, draw, points, color, width):
        # Calligraphy uses offset strokes to fake a broad-edged pen.
        stamped = self.get_path_segments(points, max(1, width // 2))
        for i in range(len(stamped) - 1):
            x1, y1 = stamped[i]
            x2, y2 = stamped[i + 1]
            draw.line([x1 - 3, y1 + 3, x2 - 3, y2 + 3], fill=color, width=max(2, width + 2))
            draw.line([x1 + 2, y1 - 2, x2 + 2, y2 - 2], fill=color, width=max(1, width // 2 + 1))

    def draw_crayon_on_pil(self, draw, points, color, width):
        # Crayon is made from short, rough marks clustered around the path.
        stamped = self.get_path_segments(points, max(1, width // 2))
        for x, y in stamped:
            for _ in range(8):
                jx = random.randint(-max(2, width), max(2, width))
                jy = random.randint(-max(2, width), max(2, width))
                size = random.randint(1, max(2, width // 2 + 1))
                draw.line(
                    [x + jx, y + jy, x + jx + size, y + jy + size],
                    fill=color,
                    width=max(1, width // 3 + 1)
                )

    def draw_watercolor_on_pil(self, base_rgba, points, color, width):
        # Watercolor is built on a transparent overlay and then blended in.
        stamped = self.get_path_segments(points, max(1, width // 2))
        overlay = Image.new("RGBA", base_rgba.size, (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        radius = max(6, width + 6)
        for x, y in stamped:
            for _ in range(3):
                jx = random.randint(-3, 3)
                jy = random.randint(-3, 3)
                alpha = random.randint(28, 48)
                odraw.ellipse(
                    (x - radius + jx, y - radius + jy, x + radius + jx, y + radius + jy),
                    fill=self.rgba_with_alpha(color, alpha)
                )
        base_rgba.alpha_composite(overlay)

    def draw_neon_on_pil(self, base_rgba, points, color, width):
        # Neon adds a translucent glow first, then draws a bright line on top.
        overlay = Image.new("RGBA", base_rgba.size, (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        glow_color = self.rgba_with_alpha(color, 70)
        odraw.line(points, fill=glow_color, width=width + 14)
        odraw.line(points, fill=glow_color, width=width + 8)
        base_rgba.alpha_composite(overlay)
        draw = ImageDraw.Draw(base_rgba)
        draw.line(points, fill=color, width=width + 2)
        draw.line(points, fill="white", width=max(1, width // 2))

    def draw_stroke_on_pil(self, draw, obj):
        # Pick the correct rendering style for each saved brush stroke.
        points = obj["points"]
        if len(points) < 2:
            return

        brush = obj["brush"]
        color = obj["color"]
        width = obj["width"]

        if brush == "pen":
            draw.line(points, fill=color, width=width)
        elif brush == "pencil":
            self.draw_pencil_on_pil(draw, points, color, width)
        elif brush == "marker":
            self.draw_marker_on_pil(draw, points, color, width)
        elif brush == "dashed":
            for i in range(0, len(points) - 1, 2):
                if i + 1 < len(points):
                    draw.line([points[i], points[i + 1]], fill=color, width=width)
        elif brush == "spray":
            self.draw_spray_on_pil(draw, points, color, width, dense=False)
        elif brush == "airbrush":
            self.draw_spray_on_pil(draw, points, color, width, dense=True)
        elif brush == "calligraphy":
            self.draw_calligraphy_on_pil(draw, points, color, width)
        elif brush == "crayon":
            self.draw_crayon_on_pil(draw, points, color, width)
        elif brush == "watercolor":
            pass
        elif brush == "neon":
            pass

    def build_final_image(self):
        # Combine the base image and all objects into one final image.
        rgba = self.base_image.convert("RGBA")
        draw = ImageDraw.Draw(rgba)
        for obj in self.objects:
            if obj["type"] == "stroke" and obj["brush"] == "watercolor":
                self.draw_watercolor_on_pil(rgba, obj["points"], obj["color"], obj["width"])
            elif obj["type"] == "stroke" and obj["brush"] == "neon":
                self.draw_neon_on_pil(rgba, obj["points"], obj["color"], obj["width"])
            else:
                self.draw_object_on_pil(draw, obj, rgba)
        return rgba.convert("RGB")

    # ===============================
    # INTERACTION
    # ===============================
    def handle_double_click(self, event):
        # Double-click selects an object and, if it is text, opens the edit prompt.
        obj = self.find_object_at(event.x, event.y)
        if obj:
            self.selected_object_id = obj["id"]
            self.edit_handles_visible = True

            if obj["type"] == "text":
                self.edit_text_object(obj)
        else:
            self.clear_selection()

        self.redraw_canvas()

    def on_mouse_move(self, event):
        # Change the cursor to match what the mouse is hovering over.
        if self.selected_object_id is not None and self.edit_handles_visible:
            obj = self.get_object_by_id(self.selected_object_id)
            if obj:
                if self.hit_test_move_handle(obj, event.x, event.y):
                    self.canvas.config(cursor="fleur")
                    return

                if self.hit_test_resize_handle(obj, event.x, event.y):
                    self.canvas.config(cursor="sizing")
                    return

                if self.hit_test_rotate_handle(obj, event.x, event.y):
                    self.canvas.config(cursor="exchange")
                    return

                x1, y1, x2, y2 = self.get_object_bbox(obj)
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.canvas.config(cursor="hand2")
                    return

        self.canvas.config(cursor="cross")

    def start_draw(self, event):
        # Save where the mouse press started.
        self.start_x, self.start_y = event.x, event.y
        self.last_x, self.last_y = event.x, event.y

        # If the user previously selected an image to insert,
        # this click places it on the base image.
        if self.waiting_for_placement and self.image_to_insert:
            self.save_undo_state()
            self.base_image.paste(self.image_to_insert, (event.x, event.y))
            self.base_draw = ImageDraw.Draw(self.base_image)
            self.waiting_for_placement = False
            self.image_to_insert = None
            self.redraw_canvas()
            return

        # Selection mode handles clicking on objects and edit handles.
        if self.mode == "tool" and self.selected_tool == "select":
            if self.selected_object_id is not None and self.edit_handles_visible:
                obj = self.get_object_by_id(self.selected_object_id)
                if obj:
                    if self.hit_test_move_handle(obj, event.x, event.y):
                        self.save_undo_state()
                        self.dragging_object = True
                        cx, cy = self.get_object_center(obj)
                        self.drag_offset_x = event.x - cx
                        self.drag_offset_y = event.y - cy
                        return

                    if self.hit_test_resize_handle(obj, event.x, event.y):
                        self.save_undo_state()
                        self.resizing_object = True
                        return

                    if self.hit_test_rotate_handle(obj, event.x, event.y):
                        self.save_undo_state()
                        self.rotating_object = True
                        return

            clicked_obj = self.find_object_at(event.x, event.y)

            if clicked_obj:
                # First click selects the object. A later drag can move it.
                if self.selected_object_id != clicked_obj["id"] or not self.edit_handles_visible:
                    self.selected_object_id = clicked_obj["id"]
                    self.edit_handles_visible = True
                    self.redraw_canvas()
                    return

                obj = self.get_object_by_id(self.selected_object_id)
                if obj:
                    x1, y1, x2, y2 = self.get_object_bbox(obj)
                    if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                        self.save_undo_state()
                        self.dragging_object = True
                        cx, cy = self.get_object_center(obj)
                        self.drag_offset_x = event.x - cx
                        self.drag_offset_y = event.y - cy
                        return
            else:
                self.clear_selection()
                self.redraw_canvas()
                return

        if self.mode == "emoji":
            # Clicking in emoji mode places the selected emoji immediately.
            self.save_undo_state()
            self.add_object({
                "type": "emoji",
                "text": self.selected_emoji,
                "x": event.x,
                "y": event.y,
                "size": self.size_slider.get(),
                "color": self.current_color,
                "rotation": 0
            })
            self.redraw_canvas()
            return

        if self.mode == "tool" and self.selected_tool == "text":
            # Text mode asks for text and then places it at the click point.
            text_value = simpledialog.askstring("Text", "Enter text:")
            if text_value is not None and text_value.strip():
                self.save_undo_state()
                self.add_object({
                    "type": "text",
                    "text": text_value.strip(),
                    "x": event.x,
                    "y": event.y,
                    "size": self.size_slider.get(),
                    "color": self.current_color,
                    "rotation": 0
                })
                self.redraw_canvas()
            return

        if self.mode == "tool" and self.selected_tool == "fill":
            # Fill uses flood fill on the base image only.
            self.save_undo_state()
            try:
                target_color = self.base_image.getpixel((event.x, event.y))
                replacement_color = self.color_to_rgb(self.current_color)
                self.flood_fill(event.x, event.y, target_color, replacement_color)
                self.redraw_canvas()
            except Exception:
                pass
            return

        if self.mode == "brush":
            # Start a new freehand stroke and collect points as the mouse moves.
            self.save_undo_state()
            self.current_stroke = {
                "type": "stroke",
                "brush": self.selected_brush,
                "color": self.current_color,
                "width": self.width_slider.get(),
                "points": [(event.x, event.y)],
                "rotation": 0
            }
            self.redraw_canvas()
            return

        if self.mode == "tool" and self.selected_tool == "eraser":
            # The eraser is really a thick marker stroke in the background color.
            self.save_undo_state()
            self.current_stroke = {
                "type": "stroke",
                "brush": "marker",
                "color": self.canvas_bg,
                "width": self.width_slider.get() + 4,
                "points": [(event.x, event.y)],
                "rotation": 0
            }
            self.redraw_canvas()
            return

    def draw_motion(self, event):
        # Mouse-drag behavior depends on the current mode.
        if self.dragging_object and self.selected_object_id is not None:
            obj = self.get_object_by_id(self.selected_object_id)
            if obj:
                self.move_object(obj, event.x - self.drag_offset_x, event.y - self.drag_offset_y)
                self.redraw_canvas()
            return

        if self.resizing_object and self.selected_object_id is not None:
            obj = self.get_object_by_id(self.selected_object_id)
            if obj:
                self.resize_object(obj, event.x, event.y)
                self.redraw_canvas()
            return

        if self.rotating_object and self.selected_object_id is not None:
            obj = self.get_object_by_id(self.selected_object_id)
            if obj:
                cx, cy = self.get_object_center(obj)
                obj["rotation"] = self.angle_from_center(cx, cy, event.x, event.y) + 90
                self.redraw_canvas()
            return

        if self.mode == "shape":
            # While dragging in shape mode, only show a preview.
            self.redraw_canvas()
            self.draw_shape_preview(self.selected_shape, self.start_x, self.start_y, event.x, event.y)
            return

        if self.current_stroke is not None:
            # While drawing a stroke, collect more points and update the preview.
            self.current_stroke["points"].append((event.x, event.y))
            self.redraw_canvas()
            return

    def end_draw(self, event):
        # When the mouse is released, finish the current action.
        if self.mode == "shape" and self.start_x is not None and self.start_y is not None:
            self.save_undo_state()
            self.add_object({
                "type": "shape",
                "shape": self.selected_shape,
                "bbox": [self.start_x, self.start_y, event.x, event.y],
                "color": self.current_color,
                "width": self.width_slider.get(),
                "rotation": 0
            })
            self.redraw_canvas()

        if self.current_stroke is not None:
            if len(self.current_stroke["points"]) > 1:
                self.add_object(self.current_stroke)
            self.current_stroke = None
            self.redraw_canvas()

        # Reset temporary state after finishing the action.
        self.preview_shape = None
        self.dragging_object = False
        self.resizing_object = False
        self.rotating_object = False
        self.start_x = None
        self.start_y = None
        self.last_x = None
        self.last_y = None

    # ===============================
    # MOVE / RESIZE
    # ===============================
    def move_object(self, obj, new_center_x, new_center_y):
        # Move the selected object so its center follows the mouse.
        if obj["type"] in ("emoji", "text"):
            obj["x"] = new_center_x
            obj["y"] = new_center_y

        elif obj["type"] == "shape":
            x1, y1, x2, y2 = obj["bbox"]
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            dx = new_center_x - cx
            dy = new_center_y - cy
            obj["bbox"] = [x1 + dx, y1 + dy, x2 + dx, y2 + dy]

        elif obj["type"] == "stroke":
            cx, cy = self.get_object_center(obj)
            dx = new_center_x - cx
            dy = new_center_y - cy
            obj["points"] = [(px + dx, py + dy) for px, py in obj["points"]]

    def resize_object(self, obj, mouse_x, mouse_y):
        # Resize behavior depends on the object type.
        if obj["type"] == "shape":
            x1, y1, _, _ = obj["bbox"]
            obj["bbox"] = [x1, y1, mouse_x, mouse_y]

        elif obj["type"] in ("emoji", "text"):
            cx, cy = obj["x"], obj["y"]
            dist = max(abs(mouse_x - cx), abs(mouse_y - cy))
            obj["size"] = max(12, int(dist))

        elif obj["type"] == "stroke":
            x1, y1, x2, y2 = self.get_object_bbox(obj)
            old_w = max(1, x2 - x1)
            old_h = max(1, y2 - y1)
            cx, cy = self.get_object_center(obj)

            scale_x = max(0.2, abs(mouse_x - cx) / max(1, old_w / 2))
            scale_y = max(0.2, abs(mouse_y - cy) / max(1, old_h / 2))

            new_points = []
            for px, py in obj["points"]:
                dx = px - cx
                dy = py - cy
                new_points.append((cx + dx * scale_x, cy + dy * scale_y))
            obj["points"] = new_points

    # ===============================
    # SHAPE PREVIEW / FILL
    # ===============================
    def draw_shape_preview(self, shape, x1, y1, x2, y2):
        # Draw a temporary shape preview during dragging.
        width = self.width_slider.get()
        color = self.current_color

        if shape == "rectangle":
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=width)
        elif shape == "oval":
            self.canvas.create_oval(x1, y1, x2, y2, outline=color, width=width)
        elif shape == "circle":
            x1, y1, x2, y2 = self.normalize_circle(x1, y1, x2, y2)
            self.canvas.create_oval(x1, y1, x2, y2, outline=color, width=width)
        else:
            pts = self.get_polygon_points(shape, x1, y1, x2, y2)
            self.canvas.create_polygon(pts, outline=color, fill="", width=width)

    def flood_fill(self, x, y, target_color, replacement_color):
        # Classic queue-based flood fill used by the paint bucket tool.
        width, height = self.base_image.size
        pixels = self.base_image.load()

        if target_color == replacement_color:
            return

        queue = deque([(x, y)])
        while queue:
            px, py = queue.popleft()

            if px < 0 or py < 0 or px >= width or py >= height:
                continue
            if pixels[px, py] != target_color:
                continue

            pixels[px, py] = replacement_color
            queue.append((px + 1, py))
            queue.append((px - 1, py))
            queue.append((px, py + 1))
            queue.append((px, py - 1))

    # ===============================
    # FILE / IMAGE
    # ===============================
    def insert_image(self):
        # Let the user choose an image file and prepare it for placement.
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not path:
            return

        img = Image.open(path).convert("RGB")
        img = img.resize((300, 300))
        self.image_to_insert = img
        self.waiting_for_placement = True
        self.set_status("Mode: Click canvas to place image")

    def save_image(self):
        # Save the finished image to disk.
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")]
        )
        if path:
            final_image = self.build_final_image()
            final_image.save(path)

    def load_image(self):
        # Load an image from disk and make it the new base canvas image.
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if path:
            self.save_undo_state()
            loaded = Image.open(path).convert("RGB")
            new_img = Image.new("RGB", (self.canvas_width, self.canvas_height), self.canvas_bg)
            new_img.paste(loaded.resize((self.canvas_width, self.canvas_height)), (0, 0))
            self.base_image = new_img
            self.base_draw = ImageDraw.Draw(self.base_image)
            self.objects = []
            self.clear_selection()
            self.redraw_canvas()

    # ===============================
    # CONTROLS
    # ===============================
    def delete_selected_object(self):
        # Remove the currently selected object.
        if self.selected_object_id is None:
            return
        self.save_undo_state()
        self.objects = [o for o in self.objects if o["id"] != self.selected_object_id]
        self.clear_selection()
        self.redraw_canvas()

    def clear_canvas(self):
        # Reset the canvas to a blank background and remove all objects.
        self.save_undo_state()
        self.base_image = Image.new("RGB", (self.canvas_width, self.canvas_height), self.canvas_bg)
        self.base_draw = ImageDraw.Draw(self.base_image)
        self.objects = []
        self.clear_selection()
        self.redraw_canvas()

    def toggle_dark_mode(self):
        # Switch the UI and canvas between light mode and dark mode.
        # This also rebuilds the base image so the background color changes.
        self.dark_mode = not self.dark_mode
        toolbar_bg = "#2b2b2b" if self.dark_mode else "lightgray"
        fg = "white" if self.dark_mode else "black"
        self.canvas_bg = "#1e1e1e" if self.dark_mode else "white"

        self.toolbar.config(bg=toolbar_bg)
        self.color_label.config(bg=toolbar_bg, fg=fg)
        self.status_label.config(bg=toolbar_bg, fg=fg)
        self.width_slider.config(bg=toolbar_bg, fg=fg, highlightbackground=toolbar_bg)
        self.size_slider.config(bg=toolbar_bg, fg=fg, highlightbackground=toolbar_bg)
        self.brush_menu.config(bg=toolbar_bg, fg=fg, highlightbackground=toolbar_bg)
        self.tool_menu.config(bg=toolbar_bg, fg=fg, highlightbackground=toolbar_bg)
        self.shape_menu.config(bg=toolbar_bg, fg=fg, highlightbackground=toolbar_bg)
        self.emoji_menu.config(bg=toolbar_bg, fg=fg, highlightbackground=toolbar_bg)
        self.canvas.config(bg=self.canvas_bg)

        rebuilt = Image.new("RGB", (self.canvas_width, self.canvas_height), self.canvas_bg)
        final_img = self.build_final_image()
        rebuilt.paste(final_img, (0, 0))
        self.base_image = rebuilt
        self.base_draw = ImageDraw.Draw(self.base_image)
        self.objects = []
        self.clear_selection()
        self.redraw_canvas()


if __name__ == "__main__":
    # Create the app window and start Tkinter's event loop.
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
