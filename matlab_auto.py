import matlab.engine

# Start MATLAB engine
eng = matlab.engine.start_matlab()

# Set MATLAB path to the script's directory
script_path = r"C:\Users\ACER\Documents\MATLAB"
eng.addpath(script_path, nargout=0)

# Run the MATLAB script "arm23.m"
try:
    eng.arm23(nargout=0)  # Calling the script as a function
    print("MATLAB script 'arm23.m' ran successfully.")
except Exception as e:
    print(f"Error while running 'arm23.m': {e}")

# Stop the MATLAB engine after execution
eng.quit()
