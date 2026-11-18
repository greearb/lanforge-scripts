"""
Draws robot markers onto the testhouse automation Web-GUI's floor-plan
images, so a report can show where each robot was on the floor plan.

Any script that has a robo_coordinates_json blob (see
FloorPlanMarkers.render_floor_images for what that looks like) can use this
class on its own - it doesn't depend on any test script's state.

Example:
    from lf_floor_plan_markers import FloorPlanMarkers

    robo_coordinates = FloorPlanMarkers(robo_coordinates_json, selected_coordinates=["1", "2"])
    if robo_coordinates.has_valid_coordinates():
        rendered = robo_coordinates.render_floor_images(output_dir)
        # rendered == [(floor_id, "/path/to/robo_coordinates_floor_f1.png"), ...]
"""
import ast
import json
import logging
import os

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class FloorPlanMarkers:

    # Background floor-plan images used by the testhouse automation Web-GUI.
    IMAGE_ASSETS_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../local/interop-webGUI/resources/static/resources/assets/images/"))

    # Mirrors the Web-GUI's `.coordinate` marker CSS (40px, #3c4b64, 4px border, white bold text).
    MARKER_DIAMETER = 40
    MARKER_COLOR = (60, 75, 100)  # #3c4b64
    MARKER_BORDER_WIDTH = 4
    MARKER_TEXT_COLOR = (255, 255, 255)  # white
    MARKER_FONT_SIZE = 16

    def __init__(self, robo_coordinates_json, selected_coordinates=None):
        self.robo_coordinates_json = robo_coordinates_json
        self.selected_coordinates = {str(c) for c in selected_coordinates} if selected_coordinates else None

    @staticmethod
    def _to_float(value):
        """Converts value to a float, returning None if it's missing or not a number."""
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _is_selected(self, robo_id):
        """True if robo_id is one of self.selected_coordinates - or always, when none were given."""
        if self.selected_coordinates is None:
            return True
        return str(robo_id) in self.selected_coordinates

    def has_valid_coordinates(self):
        """
        Checks whether there's at least one floor with at least one robot
        that has a valid x/y position.

        Callers check this before calling render_floor_images(), so a report
        doesn't try to draw floor plans when there's nothing to draw (e.g.
        only when do_bandsteering/do_roaming is enabled and this is True).

        Returns:
            bool: True if at least one robot has a usable x/y, else False.
        """
        robo_coordinates_json = self.robo_coordinates_json
        if not isinstance(robo_coordinates_json, dict):
            return False

        floors = robo_coordinates_json.get('floors')
        if not isinstance(floors, dict) or not floors:
            return False

        for floor_data in floors.values():
            if not isinstance(floor_data, dict):
                continue
            robo_coordinates = floor_data.get('robo_coordinates')
            if not isinstance(robo_coordinates, dict):
                continue
            for robo_id, coord in robo_coordinates.items():
                if not isinstance(coord, dict) or not self._is_selected(robo_id):
                    continue
                if self._to_float(coord.get('x')) is not None and self._to_float(coord.get('y')) is not None:
                    return True

        return False

    def render_floor_images(self, output_dir):
        """
        Draws each robot's marker on its floor's background image and saves
        one annotated PNG per floor into output_dir. A floor with no
        coordinates, no background image, or any other problem is skipped
        (with a warning logged) rather than failing the whole report.

        Args:
            output_dir (str): Directory to save the rendered images into.

        Returns:
            list: (floor_id, image_path) tuples, one per floor that was
            actually rendered - empty if nothing usable was found.
        """
        rendered_images = []

        robo_coordinates_json = self.robo_coordinates_json
        floors = robo_coordinates_json.get('floors') if isinstance(robo_coordinates_json, dict) else None
        if not isinstance(floors, dict):
            return rendered_images

        fallback_image_details = robo_coordinates_json.get('background_image_details')
        if not isinstance(fallback_image_details, dict):
            fallback_image_details = {}

        for floor_id, floor_data in floors.items():
            if not isinstance(floor_data, dict):
                continue

            robo_coordinates = floor_data.get('robo_coordinates')
            if not isinstance(robo_coordinates, dict) or not robo_coordinates:
                continue
            robo_coordinates = {robo_id: coord for robo_id, coord in robo_coordinates.items()
                                if isinstance(coord, dict) and self._is_selected(robo_id)}
            if not robo_coordinates:
                continue

            image_details = floor_data.get('image_details')
            if not isinstance(image_details, dict):
                image_details = {}

            bg_img = image_details.get('bg_img') or fallback_image_details.get('bg_img')
            if not bg_img:
                logger.warning("Skipping robot-coordinate rendering for floor '%s': no background image configured.", floor_id)
                continue

            image_path = os.path.join(self.IMAGE_ASSETS_PATH, bg_img)
            if not os.path.exists(image_path):
                logger.warning("Skipping robot-coordinate rendering for floor '%s': background image not found at '%s'.", floor_id, image_path)
                continue

            try:
                with Image.open(image_path) as floor_image:
                    annotated_image = floor_image.convert("RGBA")
                    draw = ImageDraw.Draw(annotated_image)
                    font = None
                    for font_name in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"):
                        try:
                            font = ImageFont.truetype(font_name, self.MARKER_FONT_SIZE)
                            break
                        except OSError:
                            continue
                    if font is None:
                        font = ImageFont.load_default()

                    for robo_id, coord in robo_coordinates.items():
                        left = self._to_float(coord.get('x'))
                        top = self._to_float(coord.get('y'))
                        if left is None or top is None:
                            continue

                        right = left + self.MARKER_DIAMETER
                        bottom = top + self.MARKER_DIAMETER
                        draw.ellipse(
                            [left, top, right, bottom],
                            fill=self.MARKER_COLOR,
                            outline=self.MARKER_COLOR,
                            width=self.MARKER_BORDER_WIDTH,
                        )

                        label = str(robo_id)
                        text_bbox = draw.textbbox((0, 0), label, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]
                        text_x = left + (self.MARKER_DIAMETER - text_width) / 2 - text_bbox[0]
                        text_y = top + (self.MARKER_DIAMETER - text_height) / 2 - text_bbox[1]
                        draw.text((text_x, text_y), label, fill=self.MARKER_TEXT_COLOR, font=font)
            except Exception as e:
                logger.warning("Skipping robot-coordinate rendering for floor '%s': failed to load/annotate '%s' (%s).", floor_id, image_path, e)
                continue

            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, f"robo_coordinates_floor_{floor_id}.png")
            annotated_image.convert("RGB").save(out_path, "PNG")
            rendered_images.append((floor_id, out_path))

        return rendered_images

    @staticmethod
    def parse_json(value):
        """
        Turns value into a dict, whether it's a dict already, a path to a
        JSON file, a JSON string, or a Python dict written out as a string.
        Logs a warning and returns None if it can't be parsed.

        Args:
            value: The raw value to parse (dict, file path, or string).

        Returns:
            dict or None.
        """
        if not value:
            return None
        if isinstance(value, dict):
            return value
        if not isinstance(value, str):
            logger.warning("Unsupported robo_coordinates_json type %s; robot markers will not be rendered.", type(value).__name__)
            return None

        if os.path.exists(value):
            try:
                with open(value) as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                logger.warning("Could not read/parse robo_coordinates_json file '%s': %s", value, e)
                return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            logger.warning("Could not parse robo_coordinates_json as a file path, JSON, or Python literal; robot markers will not be rendered.")
            return None

        if not isinstance(parsed, dict):
            logger.warning("Parsed robo_coordinates_json is not a dict (got %s); robot markers will not be rendered.", type(parsed).__name__)
            return None
        return parsed
