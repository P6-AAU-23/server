import os
from src.main import main
from src.helper import list_ports
from gooey import Gooey, GooeyParser


@Gooey
def parse_args() -> any:
    cam_ports = list_ports()
    parser = GooeyParser()

    setup = parser.add_argument_group()
    cam_choice = setup.add_mutually_exclusive_group(required=True)

    cam_choice.add_argument(
        "--address",
        widget="TextField",
        default="rtmp://127.0.0.1:1935/live/",
        dest="video_capture_address",
        help="Write rtmp address",
    )
    cam_choice.add_argument(
        "--ports",
        choices=cam_ports,
        dest="video_capture_address",
        help="The port for your camera or webcam address",
    )

    setup.add_argument(
        "saved_path",
        nargs="?",
        widget="DirChooser",
        default=os.getcwd(),
        help="Choose the folder where you want to save the whiteboards",
    )

    color_adjuster = parser.add_argument_group()

    color_adjuster.add_argument(
        "--saturation", nargs="?",
        widget="TextField",
        default=1.00,
        help="Add saturation multiplier fx. 1.5"
    )
    color_adjuster.add_argument(
        "--brightness", nargs="?",
        widget="TextField",
        default=0,
        help="Add more brightness fx 50"
    )

    pipeline_modules = parser.add_argument_group()

    pipeline_modules.add_argument("--disable_remove_foreground", action="store_true")
    pipeline_modules.add_argument("--disable_color_adjuster", action="store_true")
    pipeline_modules.add_argument("--disable_transform_perspective", action="store_true")
    pipeline_modules.add_argument("--disable_idealize_colors", action="store_true")
    pipeline_modules.add_argument("--save_on_wipe", action="store_true")
    pipeline_modules.add_argument("--fast", action="store_true")
    pipeline_modules.add_argument("--slow", action="store_true")

    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
