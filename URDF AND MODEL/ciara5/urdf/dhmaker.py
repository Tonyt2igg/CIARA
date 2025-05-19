import matlab.engine
eng = matlab.engine.start_matlab()

# Cast the input to 'double' as required by MATLAB
result = eng.sqrt(25.0)  # Pass a floating-point value
print(result)  # Should print 5.0

eng.quit()
