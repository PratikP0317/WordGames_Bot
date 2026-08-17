from .paths import DEFAULT_CALIBRATION_PATH
from .screen import calibrate_via_keypress


def main() -> None:
    calibration = calibrate_via_keypress()
    calibration.save_json(DEFAULT_CALIBRATION_PATH)
    print(f"Saved calibration: {DEFAULT_CALIBRATION_PATH}")


if __name__ == "__main__":
    main()
