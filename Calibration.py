from Screen_Stuff import calibrate_via_keypress, CalibrationConfig

if __name__ == "__main__":
    calib = calibrate_via_keypress()
    calib.save_json("./calibration.json")